use crate::error::Error;
use crate::utm::{Utm, UtmConfig, UtmExtra};
use crate::UtmRelative;

extern crate geo_types;

#[derive(Clone, Debug, PartialEq)]
pub struct Datum {
    pub(crate) a: f64,
    pub(crate) b: f64,
    pub(crate) f: f64,
    pub(crate) k0: f64,
    pub(crate) false_easting: f64,
    pub(crate) false_northing: f64,
    pub(crate) pc: Precalc,
}

const FALSE_EASTING: f64 = 500e3;
const FALSE_NORTHING: f64 = 10000e3;
const K0: f64 = 0.9996; // UTM scale on the central meridian

lazy_static! {
    /// Ellipsoidal used by most GPS systems and the UTM coordinate system
    pub static ref WGS84: Datum = {
        let a = 6_378_137.0;
        let b =6_356_752.314245;
        let f = 1.0 / 298.257223563;

        Datum::new(a, b, f, K0, FALSE_EASTING, FALSE_NORTHING).unwrap()
    };

    /// Bessel 1841 Ellipsoid used in central Europe: EPSG::7004
    pub static ref BESSEL: Datum = {
        let a = 6_377_397.155;
        let b = 6_356_078.963;
        let f = 1.0 / 299.152815;
        // FIXME - initial scale, easting and northing are actually wrong here
        Datum::new(a, b, f, K0, FALSE_EASTING,FALSE_NORTHING).unwrap()
    };
}

impl Datum {
    #[allow(unused)]
    pub fn new(a: f64, b: f64, f: f64, k0: f64, false_easting: f64, false_northing: f64) -> Result<Datum, Error> {
        if !a.is_normal() || !b.is_normal() || !f.is_normal() {
            return Err(Error::NaN);
        }

        Ok(Self {
            a,
            b,
            f,
            k0,
            false_easting,
            false_northing,
            pc: Precalc::for_ellipsoidal(a, f),
        })
    }

    pub fn a(&self) -> f64 {
        self.a
    }

    #[allow(unused)]
    pub fn b(&self) -> f64 {
        self.b
    }

    pub fn f(&self) -> f64 {
        self.f
    }

    pub fn precalculated(&self) -> &Precalc {
        &self.pc
    }
}

#[derive(Clone, Debug)]
pub struct Precalc {
    pub(crate) eccentricity: f64,
    pub(crate) meridian_radius: f64,
    pub(crate) alpha: [(f64, f64); 4],
    pub(crate) beta: [(f64, f64); 4],
}

impl PartialEq for Precalc {
    fn eq(&self, _: &Self) -> bool {
        true
    }
}

impl Precalc {
    fn for_ellipsoidal(a: f64, f: f64) -> Self {
        // ---- from Karney 2011 Eq 15-22, 36:
        // only depending on the elipsoid - therefore should be pre-calculated and cached
        let eccentricity = (f * (2.0 - f)).sqrt();
        let n = f / (2.0 - f); // 3rd flattening
        let n2 = n * n;
        let n3 = n * n2;
        let n4 = n2 * n2;
        let n5 = n2 * n3;
        let n6 = n3 * n3;

        let meridian_radius =
            a / (1.0 + n) * (1.0 + 1.0 / 4.0 * n2 + 1.0 / 64.0 * n4 + 1.0 / 256.0 * n6);

        // note α is one-based array (6th order Krüger expressions)
        #[rustfmt::skip]
            let alpha = [
            (2.0, 1.0 / 2.0 * n - 2.0 / 3.0 * n2 + 5.0 / 16.0 * n3 + 41.0 / 180.0 * n4 - 127.0 / 288.0 * n5 + 7891.0 / 37800.0 * n6),
            (4.0, 13.0 / 48.0 * n2 - 3.0 / 5.0 * n3 + 557.0 / 1440.0 * n4 + 281.0 / 630.0 * n5 - 1983433.0 / 1935360.0 * n6),
            (6.0, 61.0 / 240.0 * n3 - 103.0 / 140.0 * n4 + 15061.0 / 26880.0 * n5 + 167603.0 / 181440.0 * n6),
            (8.0, 49561.0 / 161280.0 * n4 - 179.0 / 168.0 * n5 + 6601661.0 / 7257600.0 * n6),
            // (10.0,                                                         34729.0/80640.0*n5 - 3418889.0/1995840.0*n6),
            // (12.0,                                                                          212378941.0/319334400.0*n6),
        ];

        // note beta is one-based array (6th order Krüger expressions) - have to use n == index+1
        #[rustfmt::skip]
            let beta = [
            (2.0, 1.0 / 2.0 * n - 2.0 / 3.0 * n2 + 37.0 / 96.0 * n3 - 1.0 / 360.0 * n4 - 81.0 / 512.0 * n5 + 96199.0 / 604800.0 * n6),
            (4.0, 1.0 / 48.0 * n2 + 1.0 / 15.0 * n3 - 437.0 / 1440.0 * n4 + 46.0 / 105.0 * n5 - 1118711.0 / 3870720.0 * n6),
            (6.0, 17.0 / 480.0 * n3 - 37.0 / 840.0 * n4 - 209.0 / 4480.0 * n5 + 5569.0 / 90720.0 * n6),
            (8.0, 4397.0 / 161280.0 * n4 - 11.0 / 504.0 * n5 - 830251.0 / 7257600.0 * n6),
            // (10.0,                                                       4583.0/161280.0*n5  - 108847.0/3991680.0*n6),
            // (12.0,                                                                         20648693.0/638668800.0*n6),
        ];

        Self {
            eccentricity,
            meridian_radius,
            alpha,
            beta,
        }
    }
}

pub trait UtmProjectable {
    fn to_utm(&self) -> Result<Utm, Error>;

    fn to_utm_extra(&self) -> Result<UtmExtra, Error>;

    fn to_utm_configured(&self, config: UtmConfig) -> Result<Utm, Error>;

    fn to_utm_extra_configured(&self, config: UtmConfig) -> Result<UtmExtra, Error>;

    fn to_relative_utm(&self, reference: &Utm) -> UtmRelative;
}
