use crate::filter::Filterable;
use actix_web::http::StatusCode;
use async_trait::async_trait;
use chrono::Local;
use rand::Rng;
use sar_types::MyFilter;
use serde::{Deserialize, Serialize};
use std::borrow::BorrowMut;
use std::collections::BTreeMap;
use std::fmt::{Debug, Display, Formatter};
use std::io::BufWriter;
use std::marker::PhantomData;
use std::ops::Deref;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::SystemTime;
use tokio::fs::DirEntry;
use tokio::io::AsyncReadExt;
use tokio::sync::{Mutex, MutexGuard};

const JSON_ENDING: &str = "json";
pub type DBResult<T> = Result<T, DBError>;

#[derive(Debug, thiserror::Error)]
pub enum DBError {
    StreamClosed,
    IOError(std::io::Error, Option<String>),
    NotFound,
    BadInput(String),
    Other(String),
}

pub enum ObjState<T> {
    Created(T),
    Updated(T),
}

impl<T> ObjState<T> {
    pub fn into_inner(self) -> T {
        match self {
            ObjState::Created(v) => v,
            ObjState::Updated(v) => v,
        }
    }

    pub fn as_inner(&self) -> &T {
        match self {
            ObjState::Created(v) => v,
            ObjState::Updated(v) => v,
        }
    }

    pub fn as_inner_mut(&mut self) -> &mut T {
        match self {
            ObjState::Created(v) => v,
            ObjState::Updated(v) => v,
        }
    }

    pub fn is_created(&self) -> bool {
        match self {
            ObjState::Created(_) => true,
            _ => false,
        }
    }
}

impl Display for DBError {
    fn fmt(&self, f: &mut Formatter<'_>) -> core::fmt::Result {
        write!(f, "{:?}", self)
    }
}

impl actix_web::ResponseError for DBError {
    fn status_code(&self) -> StatusCode {
        match self {
            DBError::IOError(_, _) | DBError::Other(_) => StatusCode::INTERNAL_SERVER_ERROR,
            DBError::NotFound => StatusCode::NOT_FOUND,
            DBError::BadInput(_) => StatusCode::BAD_REQUEST,
            DBError::StreamClosed => StatusCode::BAD_REQUEST,
        }
    }
}

#[async_trait]
pub trait FileTable<T> {
    async fn load_all(&self) -> DBResult<()>;

    fn root_dir(&self) -> &Path;

    fn url_prefix(&self) -> &str;

    fn init_directory(&self) -> std::io::Result<()> {
        make_dir(self.root_dir())
    }

    fn ref_to_id<'a>(&self, reference: &'a str) -> DBResult<&'a str> {
        let prefix = self.url_prefix();
        if reference.starts_with(prefix) {
            Ok(&reference[prefix.len()..])
        } else {
            Err(DBError::BadInput(format!(
                "Invalid reference {}. It does not start with {}",
                reference, prefix
            )))
        }
    }

    async fn clear(&self) -> DBResult<()>;

    async fn create(&self, obj: T) -> DBResult<String>;

    async fn get(&self, id: &str) -> DBResult<T>;

    async fn delete(&self, id: &str) -> DBResult<()>;

    async fn update(&self, obj: T) -> DBResult<T>;

    async fn get_all(&self) -> DBResult<Vec<T>>;

    async fn contains(&self, id: &str) -> bool;

    async fn insert_or_update(&self, id: &str, mut obj: T) -> DBResult<ObjState<String>>;
}

pub struct JsonTable<T> {
    root: PathBuf,
    url_root: String,
    map: Arc<Mutex<BTreeMap<String, T>>>,
}

impl<T> JsonTable<T> {
    pub fn new(root: PathBuf, url_root: &str) -> Self {
        assert!(url_root.starts_with("/") && url_root.ends_with("/"));
        Self {
            root,
            url_root: url_root.to_owned(),
            map: Arc::new(Mutex::new(BTreeMap::new())),
        }
    }
}

impl<T: Filterable + FileObject + 'static> JsonTable<T> {
    pub async fn get_filtered2(&self, filter: MyFilter) -> DBResult<Vec<T>> {
        let guard = self.map.lock().await;
        let map = guard.deref();

        let result = match (&filter.min_id, &filter.max_id) {
            (Some(ref min), Some(ref max)) => do_iterate(
                map.range(min.to_string()..max.to_string()).map(|e| e.1),
                filter,
            ),
            (Some(ref min), None) => do_iterate(map.range(min.to_string()..).map(|e| e.1), filter),
            (None, Some(ref max)) => do_iterate(map.range(..max.to_string()).map(|e| e.1), filter),
            (None, None) => do_iterate(map.values(), filter),
        };

        Ok(result)
    }
}

fn do_iterate<'a, T: Filterable + FileObject + 'static>(
    iter: impl DoubleEndedIterator<Item = &'a T>,
    filter: MyFilter,
) -> Vec<T> {
    if filter.reverse {
        do_filter(iter.rev(), filter)
    } else {
        do_filter(iter, filter)
    }
}

fn do_filter<'a, T: Filterable + FileObject + 'static>(
    iter: impl Iterator<Item = &'a T>,
    filter: MyFilter,
) -> Vec<T> {
    iter.filter(|e| e.matches(&filter))
        .map(|e| e.clone())
        .take(filter.limit.unwrap_or(1000) as usize)
        .collect()
}

#[async_trait]
impl<T> FileTable<T> for JsonTable<T>
where
    T: FileObject,
{
    async fn load_all(&self) -> DBResult<()> {
        let mut guard = self.map.lock().await;
        do_load_json_files(&self.root, guard.borrow_mut()).await
    }

    fn root_dir(&self) -> &Path {
        self.root.deref()
    }

    fn url_prefix(&self) -> &str {
        &self.url_root
    }

    async fn clear(&self) -> DBResult<()> {
        let mut guard = self.map.lock().await;

        let to_delete: Vec<_> = guard.keys().map(|k| k.to_string()).collect();

        let mut failed = 0;
        for key in to_delete {
            if let Err(e) = delete_object(guard.borrow_mut(), self.root_dir(), &key).await {
                log::error!("Failed to delete object {}: {:?}", key, e);
                failed += 1;
            }
        }

        if failed == 0 {
            Ok(())
        } else {
            Err(DBError::Other(format!("Failed to delete {} files", failed)))
        }
    }

    async fn create(&self, mut obj: T) -> DBResult<String> {
        let guard = self.map.lock().await;

        obj.set_id(create_id());

        create_object(&self.url_root, guard, self.root_dir(), &obj, obj.get_id())
            .await
            .map(|s| s.into_inner())
    }

    async fn get(&self, id: &str) -> DBResult<T> {
        let guard = self.map.lock().await;
        guard.get(id).map(T::clone).ok_or(DBError::NotFound)
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        let mut guard = self.map.lock().await;
        delete_object(guard.borrow_mut(), self.root_dir(), id).await
    }

    async fn update(&self, obj: T) -> DBResult<T> {
        let mut guard = self.map.lock().await;

        let to_update = guard.get_mut(obj.get_id()).ok_or(DBError::NotFound)?;
        *to_update = obj.clone();

        write_json_file(self.root_dir(), obj.get_id(), &obj).await?;

        Ok(obj.clone())
    }

    async fn get_all(&self) -> DBResult<Vec<T>> {
        let guard = self.map.lock().await;
        let result: Vec<_> = guard.values().map(|e| e.clone()).collect();
        drop(guard);
        Ok(result)
    }

    async fn contains(&self, id: &str) -> bool {
        let guard = self.map.lock().await;

        guard.deref().contains_key(id)
    }

    async fn insert_or_update(&self, id: &str, mut obj: T) -> DBResult<ObjState<String>> {
        let guard = self.map.lock().await;

        obj.set_id(id.to_string());

        create_object(&self.url_root, guard, self.root_dir(), &obj, obj.get_id()).await
    }
}

// impl <T> JsonTable<T>
// where T: FileObject + DroneHolder + TerrainHolder {
//     async fn get_filtered2(&self, filter: MyFilter) -> DBResult<Vec<T>> {
//         let guard = self.map.lock().await;
//         guard.values()
//     }
// }

pub trait FileObject: Debug + Clone + Send + Sync + Serialize + for<'de> Deserialize<'de> {
    fn get_id(&self) -> &str;

    fn set_id(&mut self, id: String);

    fn type_name() -> &'static str;
}

async fn do_load_json_files<P, O>(
    directory: P,
    target: &mut BTreeMap<String, O>,
) -> Result<(), DBError>
where
    P: AsRef<Path>,
    O: FileObject,
{
    let directory = directory.as_ref();
    let mut dir_iter = tokio::fs::read_dir(directory)
        .await
        .map_err(|e| io_err2(e, &directory))?;

    while let Some(entry) = dir_iter.next_entry().await.map_err(io_err)? {
        if let Some(path) = when_json_file(entry).await {
            let full_path = directory.join(&path);

            let (name, drone) = load_json(&full_path).await?;
            target.insert(name, drone);
        }
    }

    Ok(())
}

pub fn io_err2<D: Debug>(e: std::io::Error, msg: D) -> DBError {
    DBError::IOError(e, Some(format!("{:?}", msg)))
}

pub fn io_err(e: std::io::Error) -> DBError {
    DBError::IOError(e, None)
}

async fn load_json<P, O>(name: P) -> Result<(String, O), DBError>
where
    P: AsRef<Path>,
    O: FileObject,
{
    let name = name.as_ref();
    let mut reader = tokio::fs::File::open(name)
        .await
        .map_err(|e| io_err2(e, name))?;
    let mut buffer = Vec::new();
    reader
        .read_to_end(&mut buffer)
        .await
        .map_err(|e| io_err2(e, name))?;

    let object: O = serde_json::from_slice(&buffer)
        .map_err(|e| DBError::Other(format!("Failed parsing {}: {:?}", O::type_name(), e)))?;
    let name = name
        .file_stem()
        .ok_or(DBError::BadInput("bad file name".to_string()))?;
    if let Ok(name) = name.to_owned().into_string() {
        Ok((name, object))
    } else {
        Err(DBError::BadInput(
            "Cannot convert name to UTF-8".to_string(),
        ))
    }
}

fn log_bad_dir_entry(entry: std::io::Result<DirEntry>) -> Option<DirEntry> {
    match entry {
        Ok(entry) => Some(entry),
        Err(e) => {
            log::error!("Failed to load directory entry: {:?}", e);
            None
        }
    }
}

async fn when_json_file(entry: DirEntry) -> Option<PathBuf> {
    if let Ok(metadata) = entry.metadata().await {
        if metadata.is_file() && !metadata.permissions().readonly() {
            let name = entry.file_name();

            let p_name = PathBuf::from(name);

            if p_name
                .extension()
                .and_then(|e| e.to_str())
                .map(|e| e == JSON_ENDING)
                .unwrap_or(false)
            {
                Some(p_name)
            } else {
                None
            }
        } else {
            None
        }
    } else {
        None
    }
}

async fn create_object<T>(
    url_root: &str,
    mut collection: MutexGuard<'_, BTreeMap<String, T>>,
    obj_dir: &Path,
    obj: &T,
    obj_id: &str,
) -> DBResult<ObjState<String>>
where
    T: Serialize + Clone,
{
    if obj_id.is_empty() {
        return Err(DBError::BadInput("Invalid ID".to_string()));
    }

    let is_new = collection
        .borrow_mut()
        .insert(obj_id.to_string(), obj.clone())
        .is_none();

    write_json_file(obj_dir, obj_id, obj).await?;

    drop(collection);

    let location = url_root.to_string() + &obj_id;
    Ok(if is_new {
        ObjState::Created(location)
    } else {
        ObjState::Updated(location)
    })
}

async fn write_json_file<T>(obj_dir: &Path, obj_id: &str, obj: &T) -> DBResult<()>
where
    T: Serialize,
{
    let obj_file = obj_dir.to_path_buf().join(obj_id.to_string() + ".json");
    let out = std::fs::File::create(&obj_file);
    if let Err(e) = out {
        let msg = format!("Failed to write file {}: {:?}", obj_file.display(), e);
        log::warn!("{}", msg);
        return Err(DBError::IOError(e, Some(msg)));
    }
    let out = out.unwrap();

    let buf_out = BufWriter::new(out);
    if let Err(e) = serde_json::to_writer(buf_out, &obj) {
        log::warn!("Failed to write file {}: {:?}", obj_file.display(), e);
        return Err(DBError::Other(e.to_string()));
    }

    Ok(())
}

async fn delete_object<T>(
    collection: &mut BTreeMap<String, T>,
    obj_dir: &Path,
    id: &str,
) -> DBResult<()> {
    if id.is_empty() {
        return Err(DBError::BadInput("Invalid id".to_string()));
    }

    let obj_file = obj_dir.to_owned().join(id.to_string() + ".json");
    let mut deleted = false;
    if obj_file.exists() {
        if let Err(e) = std::fs::remove_file(&obj_file) {
            return Err(DBError::IOError(
                e,
                Some(format!("Cleanup failed {:?}", obj_file)),
            ));
        }
    } else {
        log::warn!(
            "Missing obj file {} when deleting object with id {}",
            obj_file.display(),
            id
        );
        deleted = true;
    }

    if collection.remove(id).is_some() {
        deleted = true;
    }

    if deleted {
        Ok(())
    } else {
        Err(DBError::NotFound)
    }
}

pub fn create_id() -> String {
    let ts = SystemTime::now();
    let ct: chrono::DateTime<Local> = chrono::DateTime::from(ts);
    let ts = ct.format("%Y%m%dT%H%M%S%3f");
    let rand_suffix: u16 = rand::thread_rng().gen();
    format!("{}_{:04X}", ts, rand_suffix)
}

pub struct ForeignKeyReference<U, T: FileTable<U>> {
    name: String,
    target: Option<Arc<T>>,
    _content: PhantomData<U>,
}

impl<U, T> ForeignKeyReference<U, T>
where
    T: FileTable<U>,
    U: FileObject,
{
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            target: None,
            _content: PhantomData::default(),
        }
    }

    pub fn init(&mut self, target: Arc<T>) {
        self.target = Some(target)
    }

    pub async fn exists(&self, id: &str) -> bool {
        self.target.as_ref().unwrap().get(id).await.is_ok()
    }

    pub async fn delete(&self, id: &str) -> DBResult<()> {
        match self.target.as_ref().unwrap().delete(id).await {
            Ok(_) => Ok(()),
            Err(DBError::NotFound) => Ok(()),
            Err(e) => Err(e),
        }
    }

    pub async fn check_id(&self, id: Option<&str>) -> DBResult<()> {
        if let Some(id) = id {
            let target = self.target.as_deref().unwrap();
            if target.contains(id).await {
                Ok(())
            } else {
                Err(DBError::BadInput(format!(
                    "Cannot resolve id {} with value {}",
                    &self.name, &id
                )))
            }
        } else {
            Ok(())
        }
    }

    pub async fn check_ref(&self, reference: Option<&str>) -> DBResult<()> {
        if let Some(reference) = reference {
            let target = self.target.as_deref().unwrap();
            let id = target.ref_to_id(reference)?;
            if target.contains(id).await {
                Ok(())
            } else {
                Err(DBError::BadInput(format!(
                    "Cannot resolve reference {} with value {}",
                    &self.name, &reference
                )))
            }
        } else {
            Ok(())
        }
    }
}

pub fn make_dir(dir: &Path) -> std::io::Result<()> {
    if !dir.exists() {
        std::fs::create_dir(dir)?;
    } else if !dir.is_dir() {
        return Err(std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("Expected {} to be a directory", dir.display()),
        ));
    }

    Ok(())
}
