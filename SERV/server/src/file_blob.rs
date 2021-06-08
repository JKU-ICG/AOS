use crate::file_db::{create_id, io_err2, DBError, DBResult, ObjState};
use actix_web::error::PayloadError;
use regex::Regex;
use std::ffi::OsString;
use std::io::ErrorKind;
use std::ops::Deref;
use std::path::{Path, PathBuf};
use tokio::io::AsyncWriteExt;
use tokio::stream::StreamExt;

pub trait Blobs {
    fn name(&self) -> &str;

    fn root_dir(&self) -> &PathBuf;

    fn suffix(&self) -> &OsString;

    fn reference_regex(&self) -> &Regex;

    fn path_buf(&self, id: &str) -> PathBuf {
        let suffix = self.suffix();
        let mut name = OsString::with_capacity(id.len() + suffix.len());
        name.push(id);
        name.push(suffix);
        let name: PathBuf = name.into();

        let buf = self.root_dir();
        buf.join(name)
    }

    fn is_path_match(&self, p: &Path) -> bool {
        let matches_extension = p
            .file_name()
            .and_then(|name| name.to_os_string().into_string().ok())
            .map_or(false, |name| {
                name.ends_with(&self.suffix().clone().into_string().unwrap())
            });

        p.starts_with(self.root_dir()) && matches_extension
    }

    fn id_of_path(&self, p: &Path) -> Option<String> {
        if self.is_path_match(p) {
            p.file_stem()
                .and_then(|stem| stem.to_os_string().into_string().ok())
        } else {
            None
        }
    }

    fn id_to_actix_file(
        &self,
        id: &str,
    ) -> Result<actix_files::NamedFile, actix_web::error::Error> {
        self.as_actix_file(&self.path_buf(id))
    }

    fn as_actix_file(&self, p: &Path) -> Result<actix_files::NamedFile, actix_web::error::Error> {
        if self.is_path_match(p) {
            actix_files::NamedFile::open(p).map_err(actix_web::error::Error::from)
        } else {
            Err(actix_web::error::ErrorNotFound(format!("{}", p.display())))
        }
    }

    fn delete_path(&self, p: &Path) -> DBResult<()> {
        if self.is_path_match(p) {
            std::fs::remove_file(p).map_err(|e| io_err2(e, p))
        } else {
            Err(DBError::NotFound)
        }
    }

    fn delete_by_id(&self, id: &str) -> DBResult<()> {
        match std::fs::remove_file(self.path_buf(id)) {
            Ok(_) => Ok(()),
            Err(e) => {
                if e.kind() == ErrorKind::NotFound {
                    Err(DBError::NotFound)
                } else {
                    Err(DBError::IOError(e, Some(id.to_string())))
                }
            }
        }
    }

    fn id_of_reference<'a>(&self, reference: &'a str) -> Option<&'a str> {
        self.reference_regex()
            .captures(reference)
            .and_then(|c| c.get(1))
            .map(|c| c.as_str())
    }

    fn cascade_delete(&self, reference: Option<&String>) -> DBResult<()> {
        if let Some(id) = reference {
            self.delete_by_ref(id)
        } else {
            Ok(())
        }
    }

    fn delete_by_ref(&self, reference: &str) -> DBResult<()> {
        if let Some(id) = self.id_of_reference(reference) {
            self.delete_by_id(id)
        } else {
            Err(DBError::NotFound)
        }
    }

    fn exists_by_ref(&self, reference: &str) -> bool {
        if let Some(id) = self.id_of_reference(reference) {
            self.path_buf(id).exists()
        } else {
            false
        }
    }

    fn check_ref(&self, reference: Option<&str>) -> DBResult<()> {
        if let Some(reference) = reference {
            if self.exists_by_ref(reference) {
                Ok(())
            } else {
                Err(DBError::BadInput(format!(
                    "Reference to {} with value {} is invalid",
                    self.name(),
                    reference
                )))
            }
        } else {
            Ok(())
        }
    }
}

#[derive(Clone, Debug)]
pub struct ReferenceBuilder {
    prefix: String,
    suffix: String,
    extra_bytes: usize,
}

impl ReferenceBuilder {
    pub fn new(prefix: &str, suffix: &str) -> Self {
        Self {
            prefix: prefix.to_owned(),
            suffix: suffix.to_owned(),
            extra_bytes: prefix.len() + suffix.len(),
        }
    }

    pub fn create_ref(&self, id: &str) -> String {
        String::with_capacity(self.extra_bytes + id.len()) + &self.prefix + id + &self.suffix
    }
}

#[derive(Clone, Debug)]
pub struct BlobReference {
    pub name: String,
    pub reference_regex: Regex,
    pub reference_builder: ReferenceBuilder,
    pub root_dir: PathBuf,
    pub suffix: OsString,
}

impl BlobReference {
    pub async fn store_or_update_blob(
        &self,
        id: &str,
        content: actix_web::web::Payload,
    ) -> DBResult<ObjState<String>> {
        let target_file = self.path_buf(id);

        let is_new = !target_file.exists();
        store_upload(target_file, content).await?;

        let reference = self.reference_builder.create_ref(id);
        Ok(if is_new {
            ObjState::Created(reference)
        } else {
            ObjState::Updated(reference)
        })
    }

    pub async fn create_blob(&self, content: actix_web::web::Payload) -> DBResult<String> {
        let id = create_id();
        let target_file = self.path_buf(&id);

        store_upload(target_file, content).await?;

        Ok(self.reference_builder.create_ref(&id))
    }
}

impl Blobs for BlobReference {
    fn name(&self) -> &str {
        &self.name
    }

    fn root_dir(&self) -> &PathBuf {
        &self.root_dir
    }

    fn suffix(&self) -> &OsString {
        &self.suffix
    }

    fn reference_regex(&self) -> &Regex {
        &self.reference_regex
    }
}

async fn store_upload(target: PathBuf, payload: actix_web::web::Payload) -> DBResult<()> {
    async fn write_file_content(
        mut file: tokio::fs::File,
        mut payload: actix_web::web::Payload,
    ) -> std::io::Result<()> {
        while let Some(chunk) = payload.next().await {
            let chunk = chunk.map_err(|e| match e {
                PayloadError::Incomplete(_) => std::io::Error::new(ErrorKind::UnexpectedEof, ""),

                e => std::io::Error::new(ErrorKind::InvalidData, format!("{:?}", e)),
            })?;

            file.write_all(chunk.deref()).await?;
        }
        file.flush().await
    }

    let file = match tokio::fs::File::create(&target).await {
        Err(e) => {
            return Err(DBError::Other(format!(
                "failed to write image {}: {:?}",
                target.display(),
                e
            )));
        }
        Ok(file) => file,
    };

    if let Err(e) = write_file_content(file, payload).await {
        if let Err(e) = tokio::fs::remove_file(&target).await {
            log::error!(
                "Failed to delete incomplete upload {}: {:?}",
                target.display(),
                e
            );
        }
        Err(DBError::Other(format!(
            "failed to write image {}: {:?}",
            target.display(),
            e
        )))
    } else {
        Ok(())
    }
}
