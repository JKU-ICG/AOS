use crate::angles::{Deg, Rad};
use crate::compare::{CoordinateCompare, SimpleFloatEq};
use crate::datum::{Datum, WGS84};
use crate::error::Error;
use num_enum::TryFromPrimitive;
use std::fmt::{Debug, Display, Formatter};
use std::iter::Peekable;
use std::str::{Chars, FromStr};
use serde::{Deserialize, Serialize, Serializer, Deserializer};
use serde::de::Visitor;
use crate::zone::Zone;
use crate::band::{Band, Hemisphere};
use std::ops::Deref;
use crate::{LatLon, UtmRelative, UtmProjectable};

#[derive(Clone, Debug, PartialEq)]
pub struct LatLonUtm {
    pub lon_lat: LatLon,
    pub convergence: Deg,
    pub scale: f64,
}

#[derive(Copy, Clone, Debug, PartialEq, Serialize)]
#[serde(into = "UtmTuple")]
pub struct Utm {
    pub easting: f64,
    pub northing: f64,
    pub zone: Zone,
    pub band: Band,
}

impl Utm {
    pub fn relative_to(&self, reference: &Utm) -> UtmRelative {
        let (easting, northing) = if self.zone == reference.zone {
            (
                reference.easting - self.easting,
                reference.northing - self.northing,
            )
        } else {
            let gps = self.to_lat_lon();
            let same_utm = gps.to_utm_configured(UtmConfig {
                datum: &self::WGS84,
                zone_override: Some(reference.zone),
                band_override: None,
            }).unwrap_or_else(|_| reference.clone());
            (
                reference.easting - same_utm.easting,
                reference.northing - same_utm.northing,
            )
        };

        UtmRelative {
            easting: easting as f32,
            northing: northing as f32,
        }
    }

    pub fn to_lat_lon(self) -> LatLon {
        utm_to_lat_lon(self, UtmConfig::default()).lon_lat
    }

    pub fn to_lat_lon_extra(self) -> LatLonUtm {
        utm_to_lat_lon(self, UtmConfig::default())
    }

    pub fn parse(s: &str) -> Result<Utm, Error> {
        let mut chars = s.chars().peekable();
        let mut zone = 0;
        while let Some(ch) = chars.peek() {
            if ch.is_ascii_digit() {
                if zone > 80 {
                    return Err(Error::ParseError);
                }
                zone = zone * 10 + (*ch as u32 - '0' as u32);
                chars.next();
            } else {
                break;
            }
        }
        let zone = Zone::new(zone).map_err(|_| Error::ParseError)?;

        Utm::skip_blanks(&mut chars);

        let band_ch = chars.next().ok_or_else(|| Error::ParseError)?;
        let band = Band::from_char(band_ch)?;

        Utm::skip_blanks(&mut chars);

        let mut first_num = String::with_capacity(10);
        while let Some(ch) = chars.next() {
            if ch.is_ascii_digit() || ch == '.' {
                first_num.push(ch);
            } else {
                break;
            }
        }

        let easting = f64::from_str(&first_num).map_err(|_| Error::ParseError)?;

        Utm::skip_blanks(&mut chars);

        let last_num: String = chars.collect();
        let northing = f64::from_str(&last_num).map_err(|_| Error::ParseError)?;

        Ok(Utm {
            easting,
            northing,
            zone,
            band,
        })
    }

    fn skip_blanks(chars: &mut Peekable<Chars>) {
        while let Some(ch) = chars.peek() {
            if *ch == ' ' {
                chars.next();
            } else {
                break;
            }
        }
    }
}

impl Display for Utm {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} ", self.zone.get())?;
        self.band.fmt(f)?;
        write!(f, " {:.4} {:.4}", self.easting, self.northing)
    }
}

struct UtmString(Utm);


impl Serialize for UtmString {
    fn serialize<S>(&self, serializer: S) -> Result<<S as Serializer>::Ok, <S as Serializer>::Error> where
        S: Serializer {
        serializer.serialize_str(&self.0.to_string())
    }
}


/// Custom deserialization logic for UTM coordinates
///
/// Allows formats `[ lon, lat, zone, band ]`
/// and the standardized format `32 U
impl<'de> Deserialize<'de> for Utm {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
        where
            D: Deserializer<'de> {
        deserializer.deserialize_any(UtmDeserializer)
    }
}

struct UtmDeserializer;

impl<'de> Visitor<'de> for UtmDeserializer {
    type Value = Utm;

    fn expecting<'a>(&self, formatter: &mut Formatter<'a>) -> std::fmt::Result {
        write!(formatter, "UTM")
    }

    fn visit_str<E: serde::de::Error>(self, s: &str) -> Result<Utm, E> {
        Utm::parse(s).map_err(|e| serde::de::Error::custom(e))
    }

    fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
        where
            A: serde::de::SeqAccess<'de>,
    {
        use serde::de::Error;

        let easting: f64 = seq.next_element()?.ok_or(Error::missing_field("easting"))?;
        let northing: f64 = seq.next_element()?.ok_or(Error::missing_field("northing"))?;
        let zone: Zone = seq.next_element()?.ok_or(Error::missing_field("zone"))?;
        let band: Band = seq.next_element()?.ok_or(Error::missing_field("band"))?;

        Ok(Utm {
            easting,
            northing,
            zone,
            band,
        })
    }
}


#[derive(Clone, Deserialize, Serialize)]
struct UtmTuple(f64, f64, Zone, Band);

impl Into<UtmTuple> for Utm {
    fn into(self) -> UtmTuple {
        UtmTuple(self.easting, self.northing, self.zone, self.band)
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct UtmExtra {
    pub utm: Utm,
    pub convergence: Deg,
    pub scale: f64,
}

impl CoordinateCompare<f64> for Utm {
    #[inline]
    fn is_eq_by(&self, other: &Self, accuracy: f64) -> bool {
        self.zone == other.zone
            && self.band == other.band
            && self.easting.var_delta_eq(other.easting, accuracy)
            && self.northing.var_delta_eq(other.northing, accuracy)
    }

    #[inline(always)]
    fn is_eq(&self, other: &Self) -> bool {
        self.is_eq_by(other, 0.01)
    }
}

#[derive(Copy, Clone, Debug)]
#[allow(non_snake_case)]
pub struct UtmConfig {
    pub datum: &'static Datum,
    pub zone_override: Option<Zone>,
    pub band_override: Option<Band>,
}

impl Default for UtmConfig {
    fn default() -> Self {
        UtmConfig {
            datum: WGS84.deref(),
            zone_override: None,
            band_override: None,
        }
    }
}

pub(crate) fn utm_to_lat_lon(utm: Utm, config: UtmConfig) -> LatLonUtm {
    let pc = &config.datum.pc;

    let eccentricity = pc.eccentricity;
    let meridian_radius = pc.meridian_radius;

    // start of actual coordinate calculation
    let x = utm.easting - config.datum.false_easting; // make x relative to central meridian
    let y = match Hemisphere::from(utm.band) {
        // make y relative to the equator
        Hemisphere::S => utm.northing - config.datum.false_northing,
        Hemisphere::N => utm.northing,
    };

    let eta = x / (config.datum.k0 * meridian_radius);
    let xi = y / (config.datum.k0 * meridian_radius);

    let xi_d: f64 = xi
        - pc.beta
        .iter()
        .cloned()
        .map(|(two_i, beta_i)| beta_i * (two_i * xi).sin() * (two_i * eta).cosh())
        .sum::<f64>();

    let eta_d: f64 = eta
        - pc.beta
        .iter()
        .cloned()
        .map(|(two_i, beta_i)| beta_i * (two_i * xi).cos() * (two_i * eta).sinh())
        .sum::<f64>();

    let sinh_eta_d = eta_d.sinh();
    let (sin_xi_d, cos_xi_d) = xi_d.sin_cos();

    let tau0 = sin_xi_d / (sinh_eta_d * sinh_eta_d + cos_xi_d * cos_xi_d).sqrt();

    let mut tau_i = tau0;

    let tau: f64 = loop {
        let sigma_i =
            (eccentricity * (eccentricity * tau_i / (1.0 + tau_i * tau_i).sqrt()).atanh()).sinh();
        let tau_id =
            tau_i * (1.0 + sigma_i * sigma_i).sqrt() - sigma_i * (1.0 + tau_i * tau_i).sqrt();
        let delta_tau_i = (tau0 - tau_id) / (1.0 + tau_id * tau_id).sqrt()
            * (1.0 + (1.0 - eccentricity * eccentricity) * tau_i * tau_i)
            / ((1.0 - eccentricity * eccentricity) * (1.0 + tau_i * tau_i).sqrt());
        tau_i += delta_tau_i;
        if delta_tau_i.abs() <= 1e-12 {
            break tau_i;
        }
    };

    let lat = tau.atan();

    let lon_local = f64::atan2(sinh_eta_d, cos_xi_d);

    // ---- convergence: Karney 2011 Eq 26, 27

    let p = 1.0
        - pc.beta
        .iter()
        .map(|(two_i, beta_i)| two_i * beta_i * (two_i * xi).cos() * (two_i * eta).cosh())
        .sum::<f64>();

    let q = 0.0
        + pc.beta
        .iter()
        .map(|(two_i, beta_i)| two_i * beta_i * (two_i * xi).sin() * (two_i * eta).sinh())
        .sum::<f64>();

    let gamma_1 = f64::atan(f64::tan(xi_d) * f64::tanh(eta_d));
    let gamma_2 = f64::atan2(q, p);

    let convergence = gamma_1 + gamma_2;

    // ---- scale: Karney 2011 Eq 28

    let sin_phi = lat.sin();
    let k1 = (1.0 - eccentricity * eccentricity * sin_phi * sin_phi).sqrt()
        * (1.0 + tau * tau).sqrt()
        * (sinh_eta_d * sinh_eta_d + cos_xi_d * cos_xi_d).sqrt();
    let k2 = meridian_radius / config.datum.a() / (p * p + q * q).sqrt();

    let scale = config.datum.k0 * k1 * k2;

    // ------------
    let lon0 = utm.zone.to_radians().0; // longitude of central meridian
    let lon = lon_local + lon0; // move λ from zonal to global coordinates

    // round to reasonable precision

    let convergence_deg = Rad(convergence).to_degrees();

    LatLonUtm {
        lon_lat: LatLon {
            lat: Rad(lat).to_degrees(),
            lon: Rad(lon).to_degrees(),
        },
        convergence: convergence_deg,
        scale,
    }
}

pub(crate) fn zone_and_band(this: LatLon, config: UtmConfig) -> Result<(Zone, Band, Rad), Error> {
    let lat = this.lat.0;
    let lon = this.lon.0;
    if !(-80.0 <= lat && lat <= 84.0) {
        return Err(Error::ZoneOutOfRange);
    }

    // grid zones are 8° tall; 0°N is offset 10 into latitude bands array
    let lat_band: Band = if let Some(band) = config.band_override {
        band
    } else {
        let lat_band = (lat / 8.0 + 10.0) as u8;
        if lat_band > 19 {
            Band::X
        } else {
            Band::try_from_primitive(lat_band).unwrap()
        }
    };

    let six_degrees = Deg(6.0).to_radians().0;
    if let Some(zone) = config.zone_override {
        return Ok((zone, lat_band, zone.to_radians()));
    }

    let mut zone = Zone::new(((lon + 180.0) / 6.0) as u32 + 1).unwrap(); // longitudinal zone
    let mut lambda0: f64 = zone.to_radians().0; // longitude of central meridian

    // ---- handle Norway/Svalbard exceptions

    // adjust zone & central meridian for Norway
    if zone.get() == 31 && lat_band == Band::V && lon >= 3.0 {
        zone += 1;
        lambda0 += six_degrees;
    }
    // adjust zone & central meridian for Svalbard
    if zone.get() == 32 && lat_band == Band::X && lon < 9.0 {
        zone -= 1;
        lambda0 -= six_degrees
    }
    if zone.get() == 32 && lat_band == Band::X && lon >= 9.0 {
        zone += 1;
        lambda0 += six_degrees
    }
    if zone.get() == 34 && lat_band == Band::X && lon < 21.0 {
        zone -= 1;
        lambda0 -= six_degrees
    }
    if zone.get() == 34 && lat_band == Band::X && lon >= 21.0 {
        zone += 1;
        lambda0 += six_degrees
    }
    if zone.get() == 36 && lat_band == Band::X && lon < 33.0 {
        zone -= 1;
        lambda0 -= six_degrees
    }
    if zone.get() == 36 && lat_band == Band::X && lon >= 33.0 {
        zone += 1;
        lambda0 += six_degrees
    }

    Ok((zone, lat_band, Rad(lambda0)))
}

pub(crate) fn lat_lon_to_utm(this: LatLon, config: UtmConfig) -> Result<UtmExtra, Error> {
    let pc = &config.datum.pc;

    let (zone, lat_band, lambda0) = zone_and_band(this.clone(), config)?;

    let lat = this.lat.to_radians().0; // latitude ± from equator
    let lon = this.lon.to_radians().0 - lambda0.0; // longitude ± from central meridian

    // allow alternative ellipsoid to be specified
    let a = config.datum.a();

    // ---- easting, northing: Karney 2011 Eq 7-14, 29, 35:

    let e = pc.eccentricity; // eccentricity

    let (sin_lon, cos_lon) = lon.sin_cos();
    let tan_lon = lon.tan();

    let tan_lat = lat.tan(); // τ ≡ tanφ, τʹ ≡ tanφʹ; prime (ʹ) indicates angles on the conformal sphere
    let sigma = (e * (e * tan_lat / (1.0 + tan_lat * tan_lat).sqrt()).atanh()).sinh();

    let tau_1 = tan_lat * (1.0 + sigma * sigma).sqrt() - sigma * (1.0 + tan_lat * tan_lat).sqrt();

    let xi_1 = tau_1.atan2(cos_lon);
    let eta_1 = (sin_lon / (tau_1 * tau_1 + cos_lon * cos_lon).sqrt()).asinh();

    let xi = xi_1
        + pc.alpha
        .iter()
        .map(|(two_i, alpha_i)| alpha_i * (two_i * xi_1).sin() * (two_i * eta_1).cosh())
        .sum::<f64>();

    let eta = eta_1
        + pc.alpha
        .iter()
        .map(|(two_i, alpha_i)| alpha_i * (two_i * xi_1).cos() * (two_i * eta_1).sinh())
        .sum::<f64>();

    let x = config.datum.k0 * pc.meridian_radius * eta;
    let y = config.datum.k0 * pc.meridian_radius * xi;

    // ---- convergence: Karney 2011 Eq 23, 24

    let p_1: f64 = 1.0
        + pc.alpha
        .iter()
        .map(|(two_i, alpha_i)| two_i * alpha_i * (two_i * xi_1).cos() * (two_i * eta_1).cosh())
        .sum::<f64>();

    let q_1: f64 = 0.0
        + pc.alpha
        .iter()
        .map(|(two_i, alpha_i)| two_i * alpha_i * (two_i * xi_1).sin() * (two_i * eta_1).sinh())
        .sum::<f64>();

    let gamma_1 = (tau_1 / (1.0 + tau_1 * tau_1).sqrt() * tan_lon).atan();
    let gamma_2 = q_1.atan2(p_1);

    let gamma = gamma_1 + gamma_2;

    // ---- scale: Karney 2011 Eq 25

    let sin_lat = lat.sin();
    let k_1 = (1.0 - e * e * sin_lat * sin_lat).sqrt() * (1.0 + tan_lat * tan_lat).sqrt()
        / (tau_1 * tau_1 + cos_lon * cos_lon).sqrt();
    let k_2 = pc.meridian_radius / a * (p_1 * p_1 + q_1 * q_1).sqrt();

    let k = config.datum.k0 * k_1 * k_2;

    // ------------

    // shift x/y to false origins
    let x = x + config.datum.false_easting; // make x relative to false easting
    let y = if y < 0.0 { y + config.datum.false_northing } else { y }; // make y in southern hemisphere relative to false northing

    let convergence = Rad(gamma).to_degrees();
    let scale = k;

    Ok(UtmExtra {
        utm: Utm {
            easting: x,
            northing: y,
            zone,
            band: lat_band,
        },
        convergence,
        scale,
    })
}


#[cfg(test)]
mod test {
    use crate::utm::*;
    use std::mem::size_of;

    #[test]
    fn deserialize_zone() {
        let z: Zone = serde_json::from_str("33").unwrap();
        let reference = Zone::new(33).unwrap();
        assert_eq!(z, reference);
        assert_eq!(serde_json::to_string(&reference).unwrap(), "33".to_string());
    }

    #[test]
    fn deserialize_band() {
        let b: Band = serde_json::from_str("\"U\"").unwrap();
        assert_eq!(b, Band::U);
        assert_eq!(serde_json::to_string(&Band::U).unwrap(), "\"U\"");
    }

    const UTM_33U: Utm = unsafe {
        Utm {
            easting: 450488.5,
            northing: 5354284.5,
            zone: Zone::new_unchecked(33),
            band: Band::U,
        }
    };

    #[test]
    fn deserialize_utm_tuple() {
        let utm_string = "[450488.5,5354284.5,33,\"U\"]".to_string();

        let parsed: Utm = serde_json::from_str(&utm_string).unwrap();
        assert_eq!(parsed, UTM_33U);

        assert_eq!(serde_json::to_string(&UTM_33U).unwrap(), utm_string);
    }

    #[test]
    fn deserialize_utm_string() {
        let utm_string = "\"33U 450488.5 5354284.5\"";

        let utm: Utm = serde_json::from_str(&utm_string).unwrap();
        assert_eq!(utm, UTM_33U);
    }


    #[test]
    fn type_sizes() {
        assert_eq!(size_of::<UtmConfig>(), 16);
        assert_eq!(size_of::<Zone>(), size_of::<Option<Zone>>());
        assert_eq!(size_of::<Band>(), size_of::<Option<Band>>())
    }

    #[test]
    fn basic_test() {
        let z33 = Zone::new(33).unwrap();
        assert_conversion(
            Utm {
                zone: z33,
                band: Band::U,
                easting: 450488.0,
                northing: 5354284.0,
            },
            LatLon {
                lat: Deg(48.33980),
                lon: Deg(14.33186),
            },
        );

        assert_conversion(
            Utm {
                zone: z33,
                band: Band::U,
                easting: 458464.0,
                northing: 5351971.0,
            },
            LatLon {
                lat: Deg(48.31956),
                lon: Deg(14.43972),
            },
        );

        assert_conversion(
            Utm {
                zone: z33,
                band: Band::U,
                easting: 458777.0,
                northing: 5352983.0,
            },
            LatLon {
                lat: Deg(48.32869),
                lon: Deg(14.44384),
            },
        );

        assert_conversion(
            Utm {
                zone: Zone::new(32).unwrap(),
                band: Band::V,
                easting: 346581.0,
                northing: 6629006.0,
            },
            LatLon {
                lat: Deg(59.77043),
                lon: Deg(6.26785),
            },
        );

        let zero = LatLon {
            lat: Deg(0.1),
            lon: Deg(0.1),
        };
        let zone31 = Zone::new(31).unwrap();
        assert_conversion(
            Utm {
                zone: zone31,
                band: Band::N,
                easting: 177164.0,
                northing: 11067.0,
            },
            zero.clone(),
        );

        let (zone, band, offset) = zone_and_band(zero, UtmConfig::default()).unwrap();
        assert_eq!(zone, zone31);
        assert_eq!(band, Band::N);
        assert_eq!(offset, zone31.to_radians());

        assert_conversion(
            Utm {
                zone: zone31,
                band: Band::N,
                easting: 166023.0,
                northing: 1.0,
            },
            LatLon {
                lat: Deg(0.00001),
                lon: Deg(0.00001),
            },
        );
    }

    fn assert_conversion(utm: Utm, lat_lon: LatLon) {
        let cfg = UtmConfig::default();

        let utm_as_lat_lon = utm_to_lat_lon(utm, cfg);

        assert!(
            utm_as_lat_lon.lon_lat.is_eq_by(&lat_lon, 0.00001),
            "{:?} == {:?}",
            utm_as_lat_lon.lon_lat,
            lat_lon
        );
        let utm_back = lat_lon_to_utm(utm_as_lat_lon.lon_lat.clone(), cfg).unwrap();
        assert!(
            utm.is_eq_by(&utm_back.utm, 0.0001),
            "{:?} == {:?}",
            utm,
            utm_back
        );

        let lat_lon_as_utm = lat_lon_to_utm(lat_lon.clone(), UtmConfig::default()).unwrap();

        assert!(
            lat_lon_as_utm.utm.is_eq_by(&utm, 0.5),
            "{:?} == {:?}",
            lat_lon_as_utm,
            utm
        );

        let lat_lon_back = utm_to_lat_lon(lat_lon_as_utm.utm.clone(), cfg);
        assert!(
            lat_lon.is_eq_by(&lat_lon_back.lon_lat, 0.0000001),
            "{:?} == {:?}",
            lat_lon,
            lat_lon_back.lon_lat
        );
    }

    #[test]
    fn parse_utm() {
        let u1 = Utm {
            easting: 183180.0,
            northing: 1331877.0,
            zone: Zone::new(31).unwrap(),
            band: Band::P,
        };
        assert_eq!(Utm::parse("31 P 183180 1331877").unwrap(), u1);
        assert_eq!(Utm::parse("31   P   183180 1331877").unwrap(), u1);
        assert_eq!(Utm::parse("31P183180 1331877").unwrap(), u1);
        assert_eq!(Utm::parse("31 P 183180.0000 1331877.0000").unwrap(), u1);

        assert_eq!(Utm::parse("331 P 183180 1331877"), Err(Error::ParseError));
    }
}

//
// #[test]
// fn basic_utm_conversion() {
//             let latitude = 60.9679875497;
//             let longitude = -149.119325194;
//             let (northing, easting, meridan_convgergence) = to_utm_wgs84(latitude, longitude, 6);
//             assert!((385273.02 - easting).abs() < 1e-2);
//             assert!((6761077.20 - northing).abs() < 1e-2);
//             assert!((0.0323 - meridan_convgergence).abs() < 1e-4);
// }
