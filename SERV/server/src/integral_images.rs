use crate::drone_images::{DBImage, ImagesTable};
use crate::file_blob::{BlobReference, Blobs, ReferenceBuilder};
use crate::file_db::{DBResult, FileObject, FileTable, ForeignKeyReference, JsonTable, ObjState, DBError};
use crate::filter::{filter_by_drone_id, filter_by_id, filter_by_location_id, DroneHolder, Filterable, LocationHolder, do_filter};
use crate::location_infos::{DBLocationInfo, LocationInfos};
use async_trait::async_trait;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::ffi::OsString;
use std::path::{Path, PathBuf};
use std::str::FromStr;
use sar_types::{IntegralImage, MyFilter};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DBIntegralImage {
    #[serde(flatten)]
    pub data: sar_types::IntegralImage,
}

impl FileObject for DBIntegralImage {
    fn get_id(&self) -> &str {
        &self.data.id
    }

    fn set_id(&mut self, id: String) {
        self.data.id = id
    }

    fn type_name() -> &'static str {
        "IntegralImage"
    }
}

impl LocationHolder for DBIntegralImage {
    fn get_location_id(&self) -> Option<&str> {
        self.data.location_id.as_deref()
    }
}

impl DroneHolder for DBIntegralImage {
    fn get_drone_id(&self) -> Option<&str> {
        self.data.drone_id.as_deref()
    }
}

impl Filterable for DBIntegralImage {
    fn matches(&self, filter: &MyFilter) -> bool {
        do_filter(self, filter)
            && filter_by_drone_id(self, &filter)
            && filter_by_location_id(self, &filter)
    }
}

pub struct IntegralImageTable {
    db: JsonTable<DBIntegralImage>,
    pub location_reference: ForeignKeyReference<DBLocationInfo, LocationInfos>,
    pub images_reference: ForeignKeyReference<DBImage, ImagesTable>,
    pub image_blob: BlobReference,
}

impl IntegralImageTable {
    pub fn new(root: PathBuf, url_root: &str) -> Self {
        Self {
            db: JsonTable::new(root.clone(), url_root),
            location_reference: ForeignKeyReference::new("terrain"),
            images_reference: ForeignKeyReference::new("images"),
            image_blob: BlobReference {
                name: "IntegralImage".to_string(),
                reference_regex: Regex::new(r#"/integrals/((?:\w|_|-)+).png"#).unwrap(),
                reference_builder: ReferenceBuilder::new("/integrals/", ".png"),
                root_dir: root,
                suffix: OsString::from_str(".png").unwrap(),
            },
        }
    }

    pub async fn get_filtered2(&self, filter: MyFilter) -> DBResult<Vec<DBIntegralImage>> {
        self.db.get_filtered2(filter).await
    }

    pub async fn store_image_png(
        &self,
        id: &str,
        payload: actix_web::web::Payload,
    ) -> DBResult<ObjState<String>> {
        let reference = self.image_blob.store_or_update_blob(id, payload).await?;

        if let Ok(mut image) = self.get(id).await {
            image.data.image_file = Some(reference.as_inner().clone());
            self.update(image).await?;
        }

        Ok(reference)
    }

    pub async fn delete_integral_png(
        &self,
        id: &str,
    ) -> DBResult<()> {
        self.image_blob.delete_by_id(id)?;

        if let Ok(mut image) = self.get(id).await {
            image.data.image_file = None;
            self.update(image).await?;
        }

        Ok(())
    }
}

#[async_trait]
impl FileTable<DBIntegralImage> for IntegralImageTable {
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

    async fn create(&self, mut obj: DBIntegralImage) -> DBResult<String> {
        for source_ref in &obj.data.source_images {
            self.images_reference.check_ref(Some(source_ref)).await?;
        }

        self.location_reference
            .check_id(obj.data.location_id.as_deref())
            .await?;

        if obj.data.image_file.is_some() {
            self.image_blob.check_ref(obj.data.image_file.as_deref())?;
        } else if !obj.get_id().is_empty() {
            let possible_ref = self.image_blob.reference_builder.create_ref(obj.get_id());
            if self.image_blob.exists_by_ref(&possible_ref) {
                obj.data.image_file = Some(possible_ref);
            }
        }

        self.db.create(obj).await
    }

    async fn get(&self, id: &str) -> DBResult<DBIntegralImage> {
        self.db.get(id).await
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        let to_delete = self.get(id).await?;

        self.image_blob.cascade_delete(to_delete.data.image_file.as_ref())?;

        self.db.delete(id).await
    }

    async fn update(&self, obj: DBIntegralImage) -> DBResult<DBIntegralImage> {
        self.location_reference.check_id(obj.get_location_id()).await?;
        self.image_blob.check_ref(obj.data.image_file.as_deref())?;
        self.db.update(obj).await
    }

    async fn get_all(&self) -> DBResult<Vec<DBIntegralImage>> {
        self.db.get_all().await
    }

    async fn contains(&self, id: &str) -> bool {
        self.db.contains(id).await
    }

    async fn insert_or_update(&self, id: &str, obj: DBIntegralImage) -> DBResult<ObjState<String>> {
        self.db.insert_or_update(id, obj).await
    }
}

#[test]
fn ser_de() {
    let input = r#"{
  "drone_id": "drone1",
  "location_id": "/locations/Test20201022F1",
  "m3x4": [
    [
      0.9956087693884628,
      0.09361184923283353,
      -0.0,
      53.61449846375633
    ],
    [
      -0.09361184923283353,
      0.9956087693884628,
      0.0,
      29.626991802770554
    ],
    [
      0.0,
      0.0,
      1.0,
      345.6988
    ]
  ],
  "source_images": [
    "/images/20210403T025653441_1939",
    "/images/20210403T025653444_EA85",
    "/images/20210403T025653446_F428",
    "/images/20210403T025653449_1267",
    "/images/20210403T025653451_A606",
    "/images/20210403T025653454_0486",
    "/images/20210403T025653456_FB2E",
    "/images/20210403T025653458_1555",
    "/images/20210403T025653460_99BC",
    "/images/20210403T025653462_6869",
    "/images/20210403T025653463_1F88",
    "/images/20210403T025653465_4C5D",
    "/images/20210403T025653467_A7ED",
    "/images/20210403T025653469_4127",
    "/images/20210403T025653471_4734",
    "/images/20210403T025653473_C9DD",
    "/images/20210403T025653475_9900",
    "/images/20210403T025653476_FCBB",
    "/images/20210403T025653479_B84A",
    "/images/20210403T025653482_604A",
    "/images/20210403T025653484_4E4D",
    "/images/20210403T025653486_CB6F",
    "/images/20210403T025653488_8C4A",
    "/images/20210403T025653490_44B6",
    "/images/20210403T025653492_0D33",
    "/images/20210403T025653494_7C26",
    "/images/20210403T025653496_9036",
    "/images/20210403T025653498_7778",
    "/images/20210403T025653500_00B8",
    "/images/20210403T025653502_F88F",
    "/images/20210403T025653504_B621",
    "/images/20210403T025653506_20E6",
    "/images/20210403T025653508_359C",
    "/images/20210403T025653510_97C7",
    "/images/20210403T025653512_0184"
  ]
}
"#;
    let de: IntegralImage = serde_json::from_str(input).unwrap();
    println!("{:?}", de);
}