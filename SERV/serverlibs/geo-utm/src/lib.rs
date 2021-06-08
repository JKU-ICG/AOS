/// Original code by Chris Veness 2014-2019
/// on https://github.com/chrisveness/geodesy/blob/master/utm.js

/// The Universal Transverse Mercator (UTM) system is a 2-dimensional Cartesian coordinate system
/// providing locations on the surface of the Earth.
///
/// UTM is a set of 60 transverse Mercator projections, normally based on the WGS-84 ellipsoid.
/// Within each zone, coordinates are represented as eastings and northings, measures in metres; e.g.
/// ‘31 N 448251 5411932’.
///
/// This method based on Karney 2011 ‘Transverse Mercator with an accuracy of a few nanometers’,
/// building on Krüger 1912 ‘Konforme Abbildung des Erdellipsoids in der Ebene’.
///
/// @module utm
///
#[macro_use]
extern crate lazy_static;

mod error;
mod angles;
mod compare;
mod datum;
mod band;
mod zone;
mod utm_relative;
mod with_height;
mod lat_lon;
mod utm;

pub use error::Error;
pub use angles::{Deg, Rad};
pub use datum::{Datum, WGS84, Precalc, UtmProjectable};
pub use lat_lon::{LatLon, LatLonDegrees};
pub use utm_relative::{UtmRelative, lat_lon_to_relative_utm};
pub use band::{Band, Hemisphere};
pub use zone::Zone;
pub use crate::utm::{Utm, LatLonUtm, UtmConfig, UtmExtra};

