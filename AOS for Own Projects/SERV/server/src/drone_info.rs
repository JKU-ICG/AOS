use crate::file_db::{DBResult, FileObject, FileTable, JsonTable, ObjState};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::ops::Deref;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DBDroneInfo {
    #[serde(flatten)]
    pub data: sar_types::DroneInfo,
}

pub struct DroneInfos {
    db: JsonTable<DBDroneInfo>,
}

impl Deref for DBDroneInfo {
    type Target = sar_types::DroneInfo;

    fn deref(&self) -> &Self::Target {
        &self.data
    }
}

impl DroneInfos {
    pub fn new(db_location: PathBuf, root_url: &str) -> Self {
        Self {
            db: JsonTable::new(db_location, root_url),
        }
    }
}

#[async_trait]
impl FileTable<DBDroneInfo> for DroneInfos {
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

    async fn create(&self, obj: DBDroneInfo) -> DBResult<String> {
        self.db.create(obj).await
    }

    async fn get(&self, id: &str) -> DBResult<DBDroneInfo> {
        self.db.get(id).await
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        self.db.delete(id).await
    }

    async fn update(&self, obj: DBDroneInfo) -> DBResult<DBDroneInfo> {
        self.db.update(obj).await
    }

    async fn get_all(&self) -> DBResult<Vec<DBDroneInfo>> {
        self.db.get_all().await
    }

    async fn contains(&self, id: &str) -> bool {
        self.db.contains(id).await
    }

    async fn insert_or_update(&self, id: &str, obj: DBDroneInfo) -> DBResult<ObjState<String>> {
        self.db.insert_or_update(id, obj).await
    }
}

impl FileObject for DBDroneInfo {
    fn get_id(&self) -> &str {
        &self.data.drone_id
    }

    fn set_id(&mut self, id: String) {
        self.data.drone_id = id;
    }

    fn type_name() -> &'static str {
        "DroneInfo"
    }
}
