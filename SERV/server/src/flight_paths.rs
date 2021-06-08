use sar_types::{FlightPath, MyFilter};
use crate::file_db::{FileTable, JsonTable, ForeignKeyReference, FileObject, DBResult, ObjState};
use crate::filter::{DroneHolder, LocationHolder, Filterable, do_filter};
use crate::drone_info::{DBDroneInfo, DroneInfos};
use crate::location_infos::{DBLocationInfo, LocationInfos};
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DBFlightPath(pub FlightPath);

impl FileObject for DBFlightPath {
    fn get_id(&self) -> &str {
        &self.0.id
    }

    fn set_id(&mut self, id: String) {
        self.0.id = id
    }

    fn type_name() -> &'static str {
        "FlightPath"
    }
}

impl DroneHolder for DBFlightPath {
    fn get_drone_id(&self) -> Option<&str> {
        self.0.drone_id.as_deref()
    }
}

impl LocationHolder for DBFlightPath {
    fn get_location_id(&self) -> Option<&str> {
        self.0.location_id.as_deref()
    }
}

impl Filterable for DBFlightPath {
    fn matches(&self, filter: &sar_types::MyFilter) -> bool {
        do_filter(self, filter)
    }
}

pub struct FlightPathTable {
    db: JsonTable<DBFlightPath>,
    pub drone_ref: ForeignKeyReference<DBDroneInfo, DroneInfos>,
    pub location_ref: ForeignKeyReference<DBLocationInfo, LocationInfos>,
}

impl FlightPathTable {
    pub fn new(root: PathBuf, url_root: &str) -> Self {
        Self {
            db: JsonTable::new(root.clone(), url_root),
            drone_ref: ForeignKeyReference::new("drone"),
            location_ref: ForeignKeyReference::new("location"),
        }
    }

    pub async fn get_filtered2(&self, filter: MyFilter) -> DBResult<Vec<DBFlightPath>> {
        self.db.get_filtered2(filter).await
    }

    async fn check_refs(&self, obj: &DBFlightPath) -> DBResult<()> {
        self.drone_ref.check_id(obj.0.drone_id.as_deref()).await?;
        self.location_ref.check_id(obj.0.location_id.as_deref()).await
    }
}

#[async_trait::async_trait]
impl FileTable<DBFlightPath> for FlightPathTable {
    async fn load_all(&self) -> DBResult<()> {
        self.db.load_all().await
    }

    fn root_dir(&self) -> &Path {
        &self.db.root_dir()
    }

    fn url_prefix(&self) -> &str {
        &self.db.url_prefix()
    }

    async fn clear(&self) -> DBResult<()> {
        self.db.clear().await
    }

    async fn create(&self, obj: DBFlightPath) -> DBResult<String> {
        self.check_refs(&obj).await?;
        self.db.create(obj).await
    }

    async fn get(&self, id: &str) -> DBResult<DBFlightPath> {
        self.db.get(id).await
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        self.db.delete(id).await
    }

    async fn update(&self, obj: DBFlightPath) -> DBResult<DBFlightPath> {
        self.check_refs(&obj).await?;
        self.db.update(obj).await
    }

    async fn get_all(&self) -> DBResult<Vec<DBFlightPath>> {
        self.db.get_all().await
    }

    async fn contains(&self, id: &str) -> bool {
        self.db.contains(id).await
    }


    async fn insert_or_update(&self, id: &str, mut obj: DBFlightPath) -> DBResult<ObjState<String>> {
        self.check_refs(&obj).await?;
        self.db.insert_or_update(id, obj).await
    }
}