use crate::drone_info::{DBDroneInfo, DroneInfos};
use crate::file_blob::{BlobReference, Blobs, ReferenceBuilder};
use crate::file_db::{DBResult, FileObject, FileTable, ForeignKeyReference, JsonTable, ObjState};
use crate::filter::{filter_by_drone_id, filter_by_id, filter_by_location_id, DroneHolder, Filterable, LocationHolder, do_filter};
use crate::location_infos::{DBLocationInfo, LocationInfos};
use async_trait::async_trait;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::ffi::OsString;
use std::path::{Path, PathBuf};
use std::str::FromStr;
use sar_types::MyFilter;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DBImage {
    #[serde(flatten)]
    pub data: sar_types::Image,
}

impl FileObject for DBImage {
    fn get_id(&self) -> &str {
        &self.data.image_id
    }

    fn set_id(&mut self, id: String) {
        self.data.image_id = id;
    }

    fn type_name() -> &'static str {
        "Image"
    }
}

impl DroneHolder for DBImage {
    fn get_drone_id(&self) -> Option<&str> {
        self.data.drone_id.as_deref()
    }
}

impl LocationHolder for DBImage {
    fn get_location_id(&self) -> Option<&str> {
        self.data.location_id.as_deref()
    }
}

impl Filterable for DBImage {
    fn matches(&self, filter: &sar_types::MyFilter) -> bool {
        do_filter(self, filter)
    }
}


pub struct ImagesTable {
    db: JsonTable<DBImage>,
    pub image_files: BlobReference,
    pub drone_reference: ForeignKeyReference<DBDroneInfo, DroneInfos>,
    pub location_reference: ForeignKeyReference<DBLocationInfo, LocationInfos>,
}

impl ImagesTable {
    pub fn new(root: PathBuf, url_root: &str) -> Self {
        Self {
            db: JsonTable::new(root.clone(), url_root),
            image_files: BlobReference {
                name: "image".to_string(),
                root_dir: root,
                suffix: OsString::from_str(".png").unwrap(),
                reference_regex: Regex::new(r#"/images/((?:\w|-|_)+)\.png"#).unwrap(),
                reference_builder: ReferenceBuilder::new("/images/", ".png"),
            },
            drone_reference: ForeignKeyReference::new("drone"),
            location_reference: ForeignKeyReference::new("terrain"),
        }
    }

    pub async fn store_image_png(
        &self,
        id: &str,
        payload: actix_web::web::Payload,
    ) -> DBResult<ObjState<String>> {
        let reference = self.image_files.store_or_update_blob(id, payload).await?;

        if let Ok(mut image) = self.get(id).await {
            image.data.image_file = Some(reference.as_inner().clone());
            self.update(image).await?;
        }

        Ok(reference)
    }

    pub async fn delete_image_png(
        &self,
        id: &str
    ) -> DBResult<()> {
        self.image_files.delete_by_id(id)?;

        if let Ok(mut image) = self.get(id).await {
            image.data.image_file = None;
            self.update(image).await?;
        }

        Ok(())
    }

    pub async fn get_filtered2(&self, filter: MyFilter) -> DBResult<Vec<DBImage>> {
        self.db.get_filtered2(filter).await
    }
}

#[async_trait]
impl FileTable<DBImage> for ImagesTable {
    async fn load_all(&self) -> DBResult<()> {
        self.db.load_all().await
    }

    fn root_dir(&self) -> &Path {
        self.db.root_dir()
    }

    fn url_prefix(&self) -> &str {
        self.db.url_prefix()
    }

    async fn clear(&self) -> DBResult<()> {
        self.db.clear().await
    }

    async fn create(&self, mut obj: DBImage) -> DBResult<String> {
        self.drone_reference
            .check_id(obj.data.drone_id.as_deref())
            .await?;
        self.location_reference
            .check_id(obj.data.location_id.as_deref())
            .await?;

        if obj.data.image_file.is_none() && !obj.get_id().is_empty() {
            // automatically link to an existing blob with the same ID
            let possible_ref = self.image_files.reference_builder.create_ref(obj.get_id());
            if let Ok(_) = self.image_files.check_ref(Some(&possible_ref)) {
                obj.data.image_file = Some(possible_ref);
            }
        } else {
            self.image_files.check_ref(obj.data.image_file.as_deref())?;
        }

        self.db.create(obj).await
    }

    async fn get(&self, id: &str) -> DBResult<DBImage> {
        self.db.get(id).await
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        if let Ok(ref image) = self.db.get(id).await {
            self.image_files
                .cascade_delete(image.data.image_file.as_ref())?;
        }
        self.db.delete(id).await
    }

    async fn update(&self, obj: DBImage) -> DBResult<DBImage> {
        self.db.update(obj).await
    }

    async fn get_all(&self) -> DBResult<Vec<DBImage>> {
        self.db.get_all().await
    }

    async fn contains(&self, id: &str) -> bool {
        self.db.contains(id).await
    }

    async fn insert_or_update(&self, id: &str, obj: DBImage) -> DBResult<ObjState<String>> {
        self.drone_reference.check_id(obj.get_drone_id()).await?;
        self.location_reference.check_id(obj.get_location_id()).await?;
        self.db.insert_or_update(id, obj).await
    }
}

#[test]
fn deserialize_json() {
    let input = r#"{
                    "location_id": "/locations/Test20201022F1",
                    "drone_id": "/drones/drone1",
                    "M3x4": [[0.9956087693884628, 0.09361184923283353, -0.0, 68.73988239726691],
                             [-0.09361184923283353, 0.9956087693884628, 0.0, 35.96844788511991],
                             [0.0, 0.0, 1.0, 345.6988]]
                }"#;
    let de: sar_types::Image = serde_json::from_str(input).unwrap();
    assert_eq!(de.drone_id.as_deref(), Some("/drones/drone1"))
}
