use crate::file_blob::{BlobReference, Blobs, ReferenceBuilder};
use crate::file_db::{DBResult, FileObject, FileTable, JsonTable, ObjState};
use async_trait::async_trait;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::ffi::OsString;
use std::ops::Deref;
use std::path::{Path, PathBuf};
use std::str::FromStr;

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DBLocationInfo {
    #[serde(flatten)]
    pub data: sar_types::LocationInfo,
}

impl DBLocationInfo {
    fn set_obj_file(&mut self, reference: String) {
        self.data.obj_file = Some(reference);
    }

    fn clear_obj_file(&mut self, reference: &str) -> bool {
        if self.data.obj_file.as_deref() == Some(reference) {
            self.data.obj_file = None;
            true
        } else {
            false
        }
    }

    fn set_geometry_file(&mut self, reference: String) {
        self.data.binary_geometry_file = Some(reference);
    }

    fn clear_geometry_file(&mut self, reference: &str) -> bool {
        if self.data.binary_geometry_file.as_deref() == Some(reference) {
            self.data.binary_geometry_file = None;
            true
        } else {
            false
        }
    }

    fn set_satellite_image(&mut self, reference: String) {
        self.data.satellite_image = Some(reference);
    }

    fn clear_satellite_image(&mut self, reference: &str) -> bool {
        if self.data.satellite_image.as_deref() == Some(reference) {
            self.data.satellite_image = None;
            true
        } else {
            false
        }
    }

    fn set_shading_image(&mut self, reference: String) {
        self.data.shading_image = Some(reference);
    }

    fn clear_shading_image(&mut self, reference: &str) -> bool {
        if self.data.shading_image.as_deref() == Some(reference) {
            self.data.shading_image = None;
            true
        } else {
            false
        }
    }

    fn set_geo_tiff_file(&mut self, reference: String) {
        self.data.geo_tiff_image = Some(reference);
    }

    fn clear_geo_tiff_file(&mut self, reference: &str) -> bool {
        if self.data.geo_tiff_image.as_deref() == Some(reference) {
            self.data.geo_tiff_image = None;
            true
        } else {
            false
        }
    }
}

impl Deref for DBLocationInfo {
    type Target = sar_types::LocationInfo;

    fn deref(&self) -> &Self::Target {
        &self.data
    }
}

impl FileObject for DBLocationInfo {
    fn get_id(&self) -> &str {
        &self.data.location_id
    }

    fn set_id(&mut self, id: String) {
        self.data.location_id = id;
    }

    fn type_name() -> &'static str {
        "TerrainInfo"
    }
}

#[derive(Debug, Copy, Clone, Eq, PartialEq)]
pub enum Relation {
    ObjFile,
    Geometry,
    SatelliteImage,
    ShadingImage,
    GeoTiffFile,
}

pub struct LocationInfos {
    db: JsonTable<DBLocationInfo>,
    pub obj_files: BlobReference,
    pub geometry_files: BlobReference,
    pub satellite_images: BlobReference,
    pub shading_images: BlobReference,
    pub geo_tiff_files: BlobReference,
}

impl LocationInfos {
    pub fn new(root: PathBuf, url_root: &str) -> Self {
        fn blobref(name: &str, suffix: &str, root_dir: &PathBuf) -> BlobReference {
            let regex_suffix = suffix.clone().replace(".", "\\.");
            let re = r#"/locations/(:?(\w|_|-)+)"#.to_string() + &regex_suffix;
            BlobReference {
                name: name.to_string(),
                reference_regex: Regex::new(&re).unwrap(),
                suffix: OsString::from_str(suffix).unwrap(),
                root_dir: root_dir.clone(),
                reference_builder: ReferenceBuilder::new("/locations/", suffix),
            }
        }

        let root_dir = root.clone();
        Self {
            db: JsonTable::new(root, url_root),
            obj_files: blobref("obj_file", ".obj", &root_dir),
            geometry_files: blobref("geometry_file", ".model", &root_dir),
            geo_tiff_files: blobref("geo_tiff", ".tiff", &root_dir),
            satellite_images: blobref("satellite_image", "_satellite.png", &root_dir),
            shading_images: blobref("shading_image", "_shading.png", &root_dir),
        }
    }

    pub async fn store_related(
        &self,
        relation: Relation,
        obj_id: &str,
        content: actix_web::web::Payload,
    ) -> DBResult<ObjState<String>> {
        let (blob_ref, set_fn) = match relation {
            Relation::ObjFile => (&self.obj_files, SetRefFn(DBLocationInfo::set_obj_file)),
            Relation::Geometry => (
                &self.geometry_files,
                SetRefFn(DBLocationInfo::set_geometry_file),
            ),
            Relation::SatelliteImage => (
                &self.satellite_images,
                SetRefFn(DBLocationInfo::set_satellite_image),
            ),
            Relation::ShadingImage => (
                &self.shading_images,
                SetRefFn(DBLocationInfo::set_shading_image),
            ),
            Relation::GeoTiffFile => (
                &self.geo_tiff_files,
                SetRefFn(DBLocationInfo::set_geo_tiff_file),
            ),
        };

        let mut state = blob_ref.store_or_update_blob(obj_id, content).await?;

        let reference = blob_ref.reference_builder.create_ref(obj_id);
        if let Ok(mut owner) = self.get(obj_id).await {
            set_fn.0(&mut owner, reference.clone());
            self.update(owner).await?;
        }

        *state.as_inner_mut() = reference;

        Ok(state)
    }

    pub async fn delete_related(&self, relation: Relation, obj_id: &str) -> DBResult<()> {
        let (blob_ref, clear_fn) = match relation {
            Relation::ObjFile => (&self.obj_files, DelRefFn(DBLocationInfo::clear_obj_file)),
            Relation::Geometry => (
                &self.geometry_files,
                DelRefFn(DBLocationInfo::clear_geometry_file),
            ),
            Relation::SatelliteImage => (
                &self.satellite_images,
                DelRefFn(DBLocationInfo::clear_satellite_image),
            ),
            Relation::ShadingImage => (
                &self.shading_images,
                DelRefFn(DBLocationInfo::clear_shading_image),
            ),
            Relation::GeoTiffFile => (
                &self.geo_tiff_files,
                DelRefFn(DBLocationInfo::clear_geo_tiff_file),
            ),
        };

        blob_ref.delete_by_id(obj_id)?;

        let reference = blob_ref.reference_builder.create_ref(obj_id);

        if let Ok(mut own_obj) = self.get(obj_id).await {
            if clear_fn.0(&mut own_obj, &reference) {
                self.update(own_obj).await?;
            }
            Ok(())
        } else {
            Ok(())
        }
    }
}

/// Newtype to give explicit lifetime to function to set a reference to a blob
struct SetRefFn<'a>(fn(&'a mut DBLocationInfo, String) -> ());

/// Newtype to give explicit lifetimes to the function pointer that removes
/// a reference from a DBTerrainInfo
///
/// Lifetime <'a> means that the TerrainInfo reference and the passed str have the same
/// lifetime - actually both only need to live for the function call only.
struct DelRefFn<'a>(fn(&'a mut DBLocationInfo, &'a str) -> bool);

impl LocationInfos {
    fn check_references(&self, obj: &DBLocationInfo) -> DBResult<()> {
        self.geo_tiff_files
            .check_ref(obj.geo_tiff_image.as_deref())?;
        self.satellite_images
            .check_ref(obj.satellite_image.as_deref())?;
        self.shading_images
            .check_ref(obj.shading_image.as_deref())?;
        self.obj_files.check_ref(obj.obj_file.as_deref())?;
        self.geometry_files
            .check_ref(obj.binary_geometry_file.as_deref())?;
        Ok(())
    }
}

#[async_trait]
impl FileTable<DBLocationInfo> for LocationInfos {
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

    async fn create(&self, obj: DBLocationInfo) -> DBResult<String> {
        self.check_references(&obj)?;

        self.db.create(obj).await
    }

    async fn get(&self, id: &str) -> DBResult<DBLocationInfo> {
        self.db.get(id).await
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        if let Ok(to_delete) = self.get(id).await {
            let to_delete = &to_delete.data;
            self.obj_files.cascade_delete(to_delete.obj_file.as_ref())?;
            self.geometry_files
                .cascade_delete(to_delete.binary_geometry_file.as_ref())?;
            self.shading_images
                .cascade_delete(to_delete.shading_image.as_ref())?;
            self.satellite_images
                .cascade_delete(to_delete.satellite_image.as_ref())?;
            self.geo_tiff_files
                .cascade_delete(to_delete.geo_tiff_image.as_ref())?;
        }
        self.db.delete(id).await
    }

    async fn update(&self, obj: DBLocationInfo) -> DBResult<DBLocationInfo> {
        self.check_references(&obj)?;

        self.db.update(obj).await
    }

    async fn get_all(&self) -> DBResult<Vec<DBLocationInfo>> {
        self.db.get_all().await
    }

    async fn contains(&self, id: &str) -> bool {
        self.db.contains(id).await
    }

    async fn insert_or_update(&self, id: &str, obj: DBLocationInfo) -> DBResult<ObjState<String>> {
        self.db.insert_or_update(id, obj).await
    }
}
