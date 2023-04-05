use crate::file_db::{DBResult, FileObject, FileTable, ForeignKeyReference, JsonTable, ObjState};
use crate::filter::{DroneHolder, Filterable, LocationHolder};
use crate::location_infos::{DBLocationInfo, LocationInfos};
use async_trait::async_trait;
use geo_utm::{Utm, UtmRelative};
use kml::types::{
    AltitudeMode, Coord, Element, Geometry, LinearRing, MultiGeometry, Placemark, Point,
};
use kml::Kml;
use sar_types::{PolyDEM, MyFilter};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::ops::Add;
use std::path::{Path, PathBuf};

fn poly_dem_to_kml_coords(pd: &PolyDEM, origin: &Utm) -> Vec<Coord> {
    pd.0.iter()
        .map(|e| {
            let rel = UtmRelative {
                easting: e.0,
                northing: e.1,
            };
            let abs: Utm = origin.add(rel);
            let gps = abs.to_lat_lon();
            Coord {
                x: gps.lon.0,
                y: gps.lat.0,
                z: Some(e.2 as f64),
            }
        })
        .collect()
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DBLabel {
    #[serde(flatten)]
    pub data: sar_types::Label,
}

impl DBLabel {
    pub fn to_kml(&self, origin: &Utm) -> Kml {
        let mut map = HashMap::new();

        if let Some(id) = self.data.location_id.as_ref() {
            map.insert("location".to_string(), id.clone());
        }
        map.insert("class".to_string(), self.data.class.to_string());

        let coords: Vec<Coord> = poly_dem_to_kml_coords(&self.data.poly_dem, origin);

        let mut elements = Vec::new();
        if let Some(id) = self.get_location_id() {
            elements.push(Element {
                name: "location_id".to_string(),
                attrs: Default::default(),
                content: Some(id.to_string()),
                children: vec![],
            });
        }

        if let Some(id) = self.get_drone_id() {
            elements.push(Element {
                name: "drone_id".to_string(),
                attrs: Default::default(),
                content: Some(id.to_string()),
                children: vec![],
            });
        }

        Kml::Placemark(Placemark {
            name: Some(self.data.label.clone()),
            description: Some(format!("Category {}", self.data.class)),
            geometry: Some(Geometry::MultiGeometry(MultiGeometry {
                geometries: vec![
                    Geometry::Point(Point {
                        coord: Coord::from(self.data.poly_dem.average_xy()),
                        extrude: true,
                        altitude_mode: AltitudeMode::ClampToGround,
                        ..Default::default()
                    }),
                    Geometry::LinearRing(LinearRing {
                        coords,
                        ..Default::default()
                    }),
                ],
                attrs: Default::default(),
            })),
            attrs: Default::default(),
            children: vec![],
        })
    }
}

impl FileObject for DBLabel {
    fn get_id(&self) -> &str {
        &self.data.label_id
    }

    fn set_id(&mut self, id: String) {
        self.data.label_id = id;
    }

    fn type_name() -> &'static str {
        "Label"
    }
}

impl DroneHolder for DBLabel {
    fn get_drone_id(&self) -> Option<&str> {
        None
    }
}

impl LocationHolder for DBLabel {
    fn get_location_id(&self) -> Option<&str> {
        self.data.location_id.as_deref()
    }
}

impl Filterable for DBLabel {
    fn matches(&self, filter: &MyFilter) -> bool {
        crate::filter::do_filter(self, filter)
    }
}

pub struct LabelTable {
    db: JsonTable<DBLabel>,
    pub location_reference: ForeignKeyReference<DBLocationInfo, LocationInfos>,
}

impl LabelTable {
    pub fn new(root: PathBuf, url_root: &str) -> Self {
        Self {
            db: JsonTable::new(root, url_root),
            location_reference: ForeignKeyReference::new("terrain"),
        }
    }

    pub async fn get_filtered2(&self, filter: MyFilter) -> DBResult<Vec<DBLabel>> {
        self.db.get_filtered2(filter).await
    }
}

#[async_trait]
impl FileTable<DBLabel> for LabelTable {
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

    async fn create(&self, obj: DBLabel) -> DBResult<String> {
        self.db.create(obj).await
    }

    async fn get(&self, id: &str) -> DBResult<DBLabel> {
        self.db.get(id).await
    }

    async fn delete(&self, id: &str) -> DBResult<()> {
        self.db.delete(id).await
    }

    async fn update(&self, obj: DBLabel) -> DBResult<DBLabel> {
        self.db.update(obj).await
    }

    async fn get_all(&self) -> DBResult<Vec<DBLabel>> {
        self.db.get_all().await
    }

    async fn contains(&self, id: &str) -> bool {
        self.db.contains(id).await
    }

    async fn insert_or_update(&self, id: &str, obj: DBLabel) -> DBResult<ObjState<String>> {
        self.db.insert_or_update(id, obj).await
    }
}

#[cfg(test)]
mod test {
    use crate::labels::DBLabel;
    use futures::SinkExt;
    use geo_utm::{Band, Utm, Zone};
    use kml::{Kml, KmlDocument, KmlWriter};
    use sar_types::{Label, PolyDEM, TexturePolygon};

    #[test]
    fn to_kml_document() {
        let origin = Utm {
            easting: 450393.91024515807,
            northing: 5354280.539372292,
            zone: Zone::new(33).unwrap(),
            band: Band::U,
        };

        let label = Label {
            label_id: "some_id".to_ascii_lowercase(),
            location_id: None,
            class: 1,
            center: None,
            label: "K".to_string(),
            texture_poly: Some(TexturePolygon(vec![
                (247, 282),
                (202, 282),
                (202, 339),
                (247, 339),
            ])),
            poly_dem: PolyDEM(vec![
                (-50.25, -32.90625, -314.25),
                (-47.71875, -32.71875, -315.0),
                (-47.875, -29.21875, -313.25),
                (-50.5625, -29.328125, -312.25),
            ]),
            description: "".to_string()
        };

        let kml: Kml = DBLabel { data: label }.to_kml(&origin);

        println!("{:?}", kml);

        let mut buf = Vec::new();

        let mut writer = KmlWriter::from_writer(&mut buf);
        writer.write(&kml).unwrap();
        std::mem::drop(writer);

        println!("{}", String::from_utf8(buf).unwrap());
    }
}
