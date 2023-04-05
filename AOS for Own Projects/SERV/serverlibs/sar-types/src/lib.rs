use geo_utm::{Utm, UtmRelative};
use serde::{Deserialize, Serialize};
use std::time::Instant;
use chrono::Local;

/// Information about a single drone
///
/// Mostly provides details about the camera on the drone
/// For simplicity, we assume exactly one camera per drone (or at least all cameras have
/// the exact same properties)
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DroneInfo {
    #[serde(default)]
    pub drone_id: String,
    pub camera: Option<CameraInfo>,
}

/// Information about a camera needed to project camera images on a 3d surface.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct CameraInfo {
    pub fov: Fov,
    pub near: f32,
    pub far: f32,
    #[serde(default)]
    pub aspect: f32,
    pub resolution: Option<(u32, u32)>,
}

/// Vertical field of view value.
///
/// Right now this is always the vertical field-of-view
#[derive(Clone, Debug, Deserialize, Serialize)]
pub enum Fov {
    Deg(f32),
    Rad(f32),
}


#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct CenterPoses {
    pub images: Vec<Image>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Image {
    #[serde(default)]
    pub image_id: String,

    pub location_id: Option<String>,
    pub drone_id: Option<String>,
    #[serde(alias = "imagefile")]
    pub image_file: Option<String>,
    #[serde(alias = "M3x4")]
    pub m3x4: [[f32; 4]; 3],
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct IntegralImage {
    #[serde(default)]
    pub id: String,
    pub drone_id: Option<String>,
    pub location_id: Option<String>,
    pub image_file: Option<String>,
    pub m3x4: [[f32; 4]; 3],
    pub source_images: Vec<String>,
}

#[derive(Clone, Debug, Default, serde::Deserialize, serde::Serialize)]
pub struct MyFilter {
    pub min_id: Option<String>,
    pub max_id: Option<String>,
    pub drone_id: Option<String>,
    pub location_id: Option<String>,
    pub limit: Option<u32>,
    #[serde(default)]
    pub reverse: bool,
}



#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct UtmSer(pub f64, pub f64, pub i32, pub char);

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct LatLon(pub f64, pub f64);

#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct GKM31(pub f64, pub f64);

/// representation of the json data that comes with the terrain
///
/// Resource name is `/locations`
#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct LocationInfo {
    #[serde(default)]
    pub location_id: String,

    #[serde(default)]
    pub description: String,

    pub satellite_image: Option<String>,

    pub shading_image: Option<String>,

    pub geo_tiff_image: Option<String>,

    pub obj_file: Option<String>,

    pub binary_geometry_file: Option<String>,

    // typo from source json file
    #[serde(alias = "startHeigth")]
    #[serde(alias = "startHeight")]
    pub start_height: f64,

    #[serde(alias = "startLatLon")]
    pub start_lat_lon: LatLon,

    #[serde(alias = "centerLatLon")]
    pub center_lat_lon: LatLon,

    #[serde(alias = "startUTM")]
    pub start_utm: Utm,

    #[serde(alias = "centerUTM")]
    pub center_utm: Utm,

    /// GKM coordinates are not used by sar-client
    #[serde(alias = "startGKM31")]
    pub start_gkm31: Option<GKM31>,

    /// GKM coordinates are not used by sar-client
    #[serde(alias = "centerGKM31")]
    pub center_gkm31: Option<GKM31>,

    /// The default conversion matrix just inverts the y and z axis
    pub relative_utm_conversion_matrix: Option<[[f32; 4]; 4]>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct TerrainMesh {
    pub location_id: String,
    pub positions: Vec<f32>,
    pub normals: Option<Vec<f32>>,
    pub texcoords: Vec<f32>,
    pub indices: Vec<u32>,
    pub bounding_box: Option<BBox>,
}

/// Bounding Box implementation based on http://people.csail.mit.edu/amy/papers/box-jgt.pdf
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BBox {
    pub min: [f32; 3],
    pub max: [f32; 3],
}

#[derive(Debug, Clone, Deserialize)]
pub struct Labels {
    #[serde(alias = "Labels")]
    pub labels: Vec<Label>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Label {
    #[serde(default)]
    pub label_id: String,

    pub location_id: Option<String>,

    #[serde(alias = "Class")]
    pub class: u32,

    #[serde(alias = "Label")]
    #[serde(alias = "Label1")]
    pub label: String,

    #[serde(default)]
    pub description: String,

    /// center of the label in an undefined coordinate system,
    /// but always in the same coordinate system as PolyDEM
    pub center: Option<(f32, f32, f32)>,

    /// Polygon around the label
    ///
    /// Coordinate system is not defined. Typically the same coordinate system as the
    /// main terrain mesh
    #[serde(alias = "polyDEM")]
    pub poly_dem: PolyDEM,

    #[serde(alias = "poly")]
    pub texture_poly: Option<TexturePolygon>,
}

impl Label {
    pub fn calc_text_position(&self) -> Option<(f32, f32, f32)> {
        if self.poly_dem.0.is_empty() {
            return None;
        }

        let (mut max_x, mut min_y, mut min_z) = (f32::MIN, f32::MAX, f32::MAX);
        for (x, y, z) in self.poly_dem.0.iter() {
            max_x = max_x.max(*x);
            min_y = min_y.min(*y);
            min_z = min_z.min(*z);
        }

        Some((max_x, min_y, min_z))
    }

    pub fn text_position(&self) -> Option<(f32, f32, f32)> {
        self.center.or_else(|| self.calc_text_position())
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct TexturePolygon(pub Vec<(i32, i32)>);

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct PolyDEM(pub Vec<(f32, f32, f32)>);

impl PolyDEM {
    pub fn average_xy(&self) -> (f64, f64) {
        let mut sx = 0.0f64;
        let mut sy = 0.0f64;
        for (x, y, _) in &self.0 {
            sx += *x as f64;
            sy += *y as f64;
        }

        let denom = self.0.len() as f64;
        (sx / denom, sy / denom)
    }
}

/// A point in relative coordinates in an UTM coordinate system.
/// Each coordinate has a unit type of 1 Meter. (approximately)
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(into = "(f32, f32, f32)")]
#[serde(from = "(f32, f32, f32)")]
pub struct UtmRelH {
    pub e: f32,
    pub n: f32,
    pub h: f32,
}

impl From<(f32, f32, f32)> for UtmRelH {
    fn from(v: (f32, f32, f32)) -> Self {
        Self {
            e: v.0,
            n: v.1,
            h: v.2,
        }
    }
}

impl Into<(f32, f32, f32)> for UtmRelH {
    fn into(self) -> (f32, f32, f32) {
        (self.e, self.n, self.h)
    }
}

impl UtmRelH {
    pub fn to_utm_relative(&self) -> UtmRelative {
        UtmRelative {
            easting: self.e,
            northing: self.n,
        }
    }

    pub fn from_utm_relative(rel: &UtmRelative, height: f32) -> Self {
        UtmRelH {
            e: rel.easting,
            n: rel.northing,
            h: height,
        }
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct InvestigationPlan {
    #[serde(default)]
    pub id: String,
    pub terrain_id: String,
    pub details: Vec<InvestigationDetail>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub enum InvestigationDetail {
    Poly(InvestigationPoly),
    HeatMap(InvestigationHeatMap),
    Point(InvestigationPoint),
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct InvestigationPoly {
    strength: f32,
    bounding_path: Vec<(f32, f32)>,
    #[serde(default)]
    description: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct InvestigationHeatMap {
    p0: UtmRelative,
    p1: UtmRelative,
    bitmap: Option<String>,
    description: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct InvestigationPoint {
    strength: f32,
    pos: (f32, f32),
    description: String,
}


#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct FlightPath {
    #[serde(default)]
    pub id: String,
    pub start_time: Option<chrono::DateTime<Local>>,
    pub end_time: Option<chrono::DateTime<Local>>,
    pub location_id: Option<String>,
    pub drone_id: Option<String>,
    pub positions: Vec<FlightPosition>,
    #[serde(default)]
    pub description: String,
    pub alt_mode: AltMode,
}

impl PartialEq for FlightPath {
    fn eq(&self, other: &Self) -> bool {
        if !self.id.is_empty() {
            self.id == other.id
        } else if other.id.is_empty() {
            self.location_id == other.location_id
                && self.drone_id == other.drone_id
                && self.positions == other.positions
                && self.alt_mode == other.alt_mode
        } else {
            false
        }
    }
}

#[derive(Clone, PartialEq, Debug, Deserialize, Serialize)]
pub struct FlightPosition {
    pub gps: LatLon,
    pub utm: Utm,
    pub altitude: f32,
    pub visit_time: Option<chrono::DateTime<Local>>,
}

#[derive(Copy, Clone, Eq, PartialEq, Debug, Deserialize, Serialize)]
pub enum AltMode {
    /// Undefined mode - use default of the application
    Undefined,
    /// Position relative to 0 level of the gkm 31 ellipsoid
    Absolute,
    /// Position relative to ground level
    Relative,
}

#[cfg(test)]
mod test {
    use crate::{
        CameraInfo, DroneInfo, Fov, Image, Label, LatLon, LocationInfo, PolyDEM, TexturePolygon,
        Utm, GKM31,
    };
    use geo_utm::{Band, Zone};

    #[test]
    fn parse_utm() {
        let input = r#"[450393.91024515807, 5354280.539372292, 33, "U"]"#;

        let parsed: Utm = serde_json::from_str(input).unwrap();
        assert_eq!(
            parsed,
            Utm {
                easting: 450393.91024515807,
                northing: 5354280.539372292,
                zone: Zone::new(33).unwrap(),
                band: Band::U,
            }
        );
        println!("Utm size: {}", std::mem::size_of::<Utm>());
    }

    #[test]
    fn drone_info_test() {
        let drone = DroneInfo {
            drone_id: "some_id".to_string(),
            camera: Some(CameraInfo {
                fov: Fov::Deg(90.0),
                near: 1.0,
                far: 100.0,
                aspect: 1.0,
                resolution: Some((512, 512)),
            }),
        };

        let result = serde_json::to_string(&drone).unwrap();

        eprintln!("{}", result);
    }

    #[test]
    fn location_info_test() {
        let location = LocationInfo {
            location_id: "some_id".to_string(),
            description: "The description".to_string(),
            satellite_image: None,
            shading_image: None,
            geo_tiff_image: None,
            obj_file: None,
            binary_geometry_file: None,
            start_height: 307.0020751953125,

            start_gkm31: Some(GKM31(73989.71284555788, 356206.4560305681)),
            center_gkm31: Some(GKM31(74084.00932285623, 356212.9582170388)),
            start_lat_lon: LatLon(48.339758, 14.33059),
            center_lat_lon: LatLon(48.3398054625, 14.3318629125),
            start_utm: Utm {
                easting: 450393.91024515807,
                northing: 5354280.539372292,
                zone: Zone::new(33).unwrap(),
                band: Band::U,
            },
            center_utm: Utm {
                easting: 450488.28387294046,
                northing: 5354284.992294418,
                zone: Zone::new(33).unwrap(),
                band: Band::U,
            },
            relative_utm_conversion_matrix: None,
        };

        let result = serde_json::to_string(&location).unwrap();

        eprintln!("{}", result);
        let parsed: LocationInfo = serde_json::from_str(&result).unwrap();
        assert_eq!(parsed, location);
    }

    #[test]
    fn parse_image() {
        let input = r#"
            {
                "location_id": "Test20201022F1",
                "drone_id": "drone1",
                "imagefile": "20201022_091540.png",
                "M3x4": [[0.9956087693884628, 0.09361184923283353, -0.0, 68.73988239726691],
                         [-0.09361184923283353, 0.9956087693884628, 0.0, 35.96844788511991],
                         [0.0, 0.0, 1.0, 345.6988]]
            }"#;

        let image: Image = serde_json::from_str(input).unwrap();

        let expected = Image {
            image_id: String::new(),
            location_id: Some("Test20201022F1".to_string()),
            drone_id: Some("drone1".to_string()),
            image_file: Some("20201022_091540.png".to_string()),
            m3x4: [
                [
                    0.9956087693884628,
                    0.09361184923283353,
                    -0.0,
                    68.73988239726691,
                ],
                [
                    -0.09361184923283353,
                    0.9956087693884628,
                    0.0,
                    35.96844788511991,
                ],
                [0.0, 0.0, 1.0, 345.6988],
            ],
        };

        let expected_ser = serde_json::to_string(&expected).unwrap();
        let parsed_ser = serde_json::to_string(&image).unwrap();

        assert_eq!(parsed_ser, expected_ser);
    }

    #[test]
    fn parse_location() {
        let input = r#"{"location_id": "Test20201022F1",
                     "start_height": 307.0020751953125,
                     "start_lat_lon": [48.339758, 14.33059],
                     "center_lat_lon": [48.3398054625, 14.3318629125],
                     "start_utm": [450393.91024515807, 5354280.539372292, 33, "U"],
                     "start_gkm31": [73989.71284555788, 356206.4560305681],
                     "center_gkm31": [74084.00932285623, 356212.9582170388],
                     "center_utm": [450488.28387294046, 5354284.992294418, 33, "U"]}"#;
        let parsed: LocationInfo = serde_json::from_str(input).unwrap();

        assert_eq!(&parsed.location_id, "Test20201022F1")
    }

    #[test]
    fn label_ser_de() {
        let input = r#"{
  "class": 0,
  "Label1": "K",
  "poly": [
    [
      247,
      282
    ],
    [
      202,
      282
    ],
    [
      202,
      339
    ],
    [
      247,
      339
    ]
  ],
  "polyDEM": [
    [
      -50.25,
      -32.90625,
      -314.25
    ],
    [
      -47.71875,
      -32.71875,
      -315.0
    ],
    [
      -47.875,
      -29.21875,
      -313.25
    ],
    [
      -50.5625,
      -29.328125,
      -312.25
    ]
  ]
}
"#;
        let orig = Label {
            label_id: "".to_string(),
            location_id: None,
            class: 0,
            label: "K".to_string(),
            description: "".to_string(),
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

            center: None,
        };
        let ser = serde_json::to_string_pretty(&orig).unwrap();
        println!("{}", ser);
        let de: Label = serde_json::from_str(input).unwrap();
        println!("{:?}", de);
    }
}
