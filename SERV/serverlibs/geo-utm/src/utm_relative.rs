use crate::utm::{Utm};
use std::ops::{Add, Sub};
use crate::{Error, LatLon};
use crate::datum::Datum;
use crate::band::Band;

#[derive(Copy, Clone, Debug, PartialEq, serde::Deserialize, serde::Serialize)]
#[serde(into = "(f32, f32)")]
#[serde(from = "(f32, f32)")]
pub struct UtmRelative {
    pub easting: f32,
    pub northing: f32,
}

impl UtmRelative {
    pub fn to_absolute(self, reference: Utm) -> Utm {
        Utm {
            easting: reference.easting + self.easting as f64,
            northing: reference.northing + self.northing as f64,
            zone: reference.zone,
            band: reference.band,
        }
    }

    pub fn from_absolute(local: Utm, reference: Utm) -> Result<UtmRelative, Error> {
        if local.zone == reference.zone && local.band == reference.band {
            Ok(UtmRelative {
                easting: (local.easting - reference.easting) as f32,
                northing: (local.northing - reference.northing) as f32,
            })
        } else {
            Err(Error::IncompatibleZone)
        }
    }
}

impl Add<UtmRelative> for Utm {
    type Output = Utm;

    fn add(self, rhs: UtmRelative) -> Self::Output {
        Utm {
            easting: self.easting + rhs.easting as f64,
            northing: self.northing + rhs.northing as f64,
            zone: self.zone,
            band: self.band,
        }
    }
}

impl Sub<UtmRelative> for Utm {
    type Output = Utm;

    fn sub(self, rhs: UtmRelative) -> Self::Output {
        Utm {
            easting: self.easting - rhs.easting as f64,
            northing: self.northing - rhs.northing as f64,
            zone: self.zone,
            band: self.band,
        }
    }
}

impl From<(f32, f32)> for UtmRelative {
    fn from(v: (f32, f32)) -> Self {
        Self {
            easting: v.0,
            northing: v.1,
        }
    }
}

impl Into<(f32, f32)> for UtmRelative {
    fn into(self) -> (f32, f32) {
        (self.easting, self.northing)
    }
}

pub fn lat_lon_to_relative_utm(
    lat_lon: LatLon,
    reference: &Utm,
    datum: &Datum,
) -> UtmRelative {
    let lambda0 = reference.zone.to_radians();

    let lat = lat_lon.lat.to_radians().0; // latitude ± from equator
    let lon = lat_lon.lon.to_radians().0 - lambda0.0; // longitude ± from central meridian

    // ---- easting, northing: Karney 2011 Eq 7-14, 29, 35:

    let e = datum.pc.eccentricity;

    let (sin_lon, cos_lon) = lon.sin_cos();

    let tan_lat = lat.tan();
    let sigma = (e * (e * tan_lat / (1.0 + tan_lat * tan_lat).sqrt()).atanh()).sinh();

    let tau_1 = tan_lat * (1.0 + sigma * sigma).sqrt() - sigma * (1.0 + tan_lat * tan_lat).sqrt();

    let xi_1 = tau_1.atan2(cos_lon);
    let eta_1 = (sin_lon / (tau_1 * tau_1 + cos_lon * cos_lon).sqrt()).asinh();

    let xi = {
        let a = &datum.pc.alpha;
        let (t0, a0) = a[0];
        let (t1, a1) = a[1];
        let (t2, a2) = a[2];
        let (t3, a3) = a[3];
        let r0 = a0 * (t0 * xi_1).sin() * (t0 * eta_1).cosh();
        let r1 = a1 * (t1 * xi_1).sin() * (t1 * eta_1).cosh();
        let r2 = a2 * (t2 * xi_1).sin() * (t2 * eta_1).cosh();
        let r3 = a3 * (t3 * xi_1).sin() * (t3 * eta_1).cosh();

        r0 + r1 + r2 + r3
    };

    // let xi = xi_1
    //     + datum
    //     .pc
    //     .alpha
    //     .iter()
    //     .map(|(two_i, alpha_i)| alpha_i * (two_i * xi_1).sin() * (two_i * eta_1).cosh())
    //     .sum::<f64>();

    let eta = eta_1
        + datum
        .pc
        .alpha
        .iter()
        .map(|(two_i, alpha_i)| alpha_i * (two_i * xi_1).cos() * (two_i * eta_1).sinh())
        .sum::<f64>();

    // shift x/y to false origins
    let x = datum.k0 * datum.pc.meridian_radius * eta + datum.false_easting;
    let y = datum.k0 * datum.pc.meridian_radius * xi
        + if reference.band < Band::N {
        datum.false_northing
    } else {
        0.0
    };

    UtmRelative {
        easting: (x - reference.easting) as f32,
        northing: (y - reference.northing) as f32,
    }
}