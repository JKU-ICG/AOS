use crate::compare::{CoordinateCompare, SimpleFloatEq};
use crate::datum::{UtmProjectable, WGS84};
use crate::{Deg, Error, Utm, UtmConfig, UtmExtra, UtmRelative};
use serde::de::{Error as SErr, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize};
use std::fmt::{Display, Formatter};
use std::ops::Deref;
use std::str::FromStr;

/// EPSG:4326 latitude, longitude coordinate on the WGS84 Ellipsoid.
/// Used by GPS and can be projected as Utm coordinates
///
/// Attribute order is latitude, longitude as that order is used
/// by Google Maps and most other GPS based applications.
#[derive(Copy, Clone, Debug, PartialEq, Serialize)]
#[serde(into = "(f64,f64)")]
#[repr(align(32))]
pub struct LatLon {
    /// North-south position; y coordinate
    pub lat: Deg,
    /// east-west position; x coordinate
    pub lon: Deg,
}

impl Into<(f64, f64)> for LatLon {
    fn into(self) -> (f64, f64) {
        (self.lat.0, self.lon.0)
    }
}

impl From<(f64, f64)> for LatLon {
    fn from(i: (f64, f64)) -> Self {
        LatLon {
            lat: Deg(i.0),
            lon: Deg(i.1),
        }
    }
}

impl UtmProjectable for LatLon {
    fn to_utm(&self) -> Result<Utm, Error> {
        crate::utm::lat_lon_to_utm(self.clone(), UtmConfig::default()).map(|r| r.utm)
    }

    fn to_utm_extra(&self) -> Result<UtmExtra, Error> {
        crate::utm::lat_lon_to_utm(self.clone(), UtmConfig::default())
    }

    fn to_utm_configured(&self, config: UtmConfig) -> Result<Utm, Error> {
        crate::utm::lat_lon_to_utm(self.clone(), config).map(|r| r.utm)
    }

    fn to_utm_extra_configured(&self, config: UtmConfig) -> Result<UtmExtra, Error> {
        crate::utm::lat_lon_to_utm(self.clone(), config)
    }

    fn to_relative_utm(&self, reference: &Utm) -> UtmRelative {
        crate::utm_relative::lat_lon_to_relative_utm(self.clone(), reference, WGS84.deref())
    }
}

impl LatLon {
    pub fn from_degrees(lat: f64, lon: f64) -> Self {
        Self {
            lat: Deg(lat),
            lon: Deg(lon),
        }
    }
}

impl Display for LatLon {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:.7}°N {:.7}°E", self.lat.0, self.lon.0)
    }
}

impl CoordinateCompare<f64> for LatLon {
    fn is_eq_by(&self, other: &Self, delta: f64) -> bool {
        self.lat.0.var_delta_eq(other.lat.0, delta) && self.lon.0.var_delta_eq(other.lon.0, delta)
    }

    fn is_eq(&self, other: &Self) -> bool {
        self.is_eq_by(other, 0.00001)
    }
}

impl<'de> Deserialize<'de> for LatLon {
    fn deserialize<D>(deserializer: D) -> Result<Self, <D as Deserializer<'de>>::Error>
    where
        D: Deserializer<'de>,
    {
        deserializer.deserialize_any(LatLonDeserializer)
    }
}

struct LatLonDeserializer;

impl<'de> Visitor<'de> for LatLonDeserializer {
    type Value = LatLon;

    fn expecting(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "LatLon coordinate")
    }

    fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Self::Value, E> {
        fn parse_plain<E: serde::de::Error>(s: &str, name: &str) -> Result<f64, E> {
            f64::from_str(s).map_err(|_| SErr::custom(format!("invalid {}", name)))
        }
        fn parse_tagged<E: SErr>(s: &str, tag: &str, name: &str) -> Result<f64, E> {
            if s.starts_with(tag) {
                parse_plain(&s[tag.len()..].trim(), name)
            } else if s.ends_with(tag) {
                parse_plain(&s[0..(s.len() - tag.len())], name)
            } else {
                Err(SErr::custom(format!("invalid {}", name)))
            }
        }

        let mut s = v.trim().split_ascii_whitespace();
        let m = (
            s.next().ok_or(SErr::custom("missing first element"))?,
            s.next().ok_or(SErr::custom("missing second element"))?,
        );

        let (lat, lon) = match (
            m.0.contains("N"),
            m.0.contains("E"),
            m.1.contains("N"),
            m.1.contains("E"),
        ) {
            (false, false, false, false) => (
                parse_plain(m.0, "latitude")?,
                parse_plain(m.1, "longitude")?,
            ),
            (true, false, false, true) => (
                parse_tagged(m.0, "N", "latitude")?,
                parse_tagged(m.1, "E", "longitude")?,
            ),
            (false, true, true, false) => (
                parse_tagged(m.1, "N", "latitude")?,
                parse_tagged(m.0, "E", "longitude")?,
            ),
            _ => return Err(SErr::custom(format!("Invalid coordinate: {}", v))),
        };

        Ok(LatLon {
            lat: Deg(lat),
            lon: Deg(lon),
        })
    }

    fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
    where
        A: SeqAccess<'de>,
    {
        let lat: f64 = seq
            .next_element()?
            .ok_or(SErr::custom("Missing latitude"))?;
        let lon: f64 = seq
            .next_element()?
            .ok_or(SErr::custom("Missing longitude"))?;
        if let Some(unexpected) = seq.next_element::<&str>()? {
            return Err(SErr::custom(format!(
                "Unexpected coordinate: {}",
                unexpected
            )));
        }

        Ok(LatLon {
            lat: Deg(lat),
            lon: Deg(lon),
        })
    }
}

pub struct LatLonDegrees(pub LatLon);

impl LatLonDegrees {
    fn min_sec(angle: Deg) -> (i32, i32, f64) {
        let deg = angle.0.trunc();
        let minutes = ((angle.0 - deg) * 60.0).trunc();
        let seconds = (angle.0 - deg - minutes/60.0) * 3600.0;
        (deg as i32, minutes as i32, seconds.abs())
    }
}

impl Display for LatLonDegrees {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let (lat_deg, lat_minutes, lat_seconds) = Self::min_sec(self.0.lat);
        let (lon_deg, lon_minutes, lon_seconds) = Self::min_sec(self.0.lon);
        let (lat_deg, lat_suffix) = if lat_deg >= 0 {
            (lat_deg, 'N')
        } else {
            (-lat_deg, 'S')
        };
        let (lon_deg, lon_suffix) = if lon_deg >= 0 {
            (lon_deg, 'E')
        } else {
            (-lon_deg, 'W')
        };

        write!(
            f,
            "{}°{}'{:.2}''{} {}°{}'{:.2}''{}",
            lat_deg,
            lat_minutes,
            lat_seconds,
            lat_suffix,
            lon_deg,
            lon_minutes,
            lon_seconds,
            lon_suffix
        )
    }
}

#[test]
fn lat_lon_serde_json() {
    let input = LatLon::from_degrees(48.5213, 16.412156);
    let ser = serde_json::to_string(&input).unwrap();
    let de: LatLon = serde_json::from_str(&ser).unwrap();
    assert_eq!(&ser, "[48.5213,16.412156]");
    assert_eq!(de, input);
}

#[test]
fn lat_lon_decimal() {
    let ll = LatLon::from_degrees(48.5213, 16.412156);
    let de: LatLon = serde_json::from_str("\"N48.5213 E16.412156\"").unwrap();
    assert_eq!(de, ll);
    let de: LatLon = serde_json::from_str("\"E16.412156 N48.5213\"").unwrap();
    assert_eq!(de, ll);
}
