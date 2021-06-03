use std::num::NonZeroU32;
use crate::{Deg, Rad, Error};
use std::ops::{Add, AddAssign, SubAssign};

#[derive(Copy, Clone, Debug, Eq, PartialEq, serde::Serialize, serde::Deserialize)]
#[serde(transparent)]
pub struct Zone {
    z: NonZeroU32,
}

impl Zone {
    pub fn to_degrees(self) -> Deg {
        Deg(((self.z.get() - 1) * 6) as f64 - 180.0 + 3.0)
    }

    pub fn to_radians(self) -> Rad {
        self.to_degrees().to_radians()
    }

    #[inline(always)]
    fn modulo_zone(num: i32) -> Zone {
        let z = ((num - 1) % 60) as u32;
        Zone {
            z: NonZeroU32::new(z + 1).unwrap(),
        }
    }

    #[inline(always)]
    pub fn get(self) -> u32 {
        self.z.get()
    }
}

impl Add<i32> for Zone {
    type Output = Zone;

    fn add(self, rhs: i32) -> Self::Output {
        let z = self.z.get() as i32 + rhs;
        Self::modulo_zone(z)
    }
}

impl AddAssign<i32> for Zone {
    fn add_assign(&mut self, rhs: i32) {
        *self = Self::modulo_zone(self.z.get() as i32 + rhs);
    }
}

impl SubAssign<i32> for Zone {
    fn sub_assign(&mut self, rhs: i32) {
        *self = Self::modulo_zone(self.z.get() as i32 - rhs);
    }
}

impl From<Zone> for u8 {
    fn from(z: Zone) -> Self {
        z.z.get() as u8
    }
}

impl From<Zone> for u32 {
    fn from(z: Zone) -> Self {
        z.z.get()
    }
}

impl From<Zone> for f64 {
    fn from(z: Zone) -> Self {
        z.z.get() as f64
    }
}

impl Zone {
    pub fn new(zone: u32) -> Result<Zone, Error> {
        if zone <= 0 || zone > 60 {
            Err(Error::InvalidZone)
        } else {
            Ok(Zone {
                z: NonZeroU32::new(zone).unwrap(),
            })
        }
    }

    pub const unsafe fn new_unchecked(zone: u32) -> Zone {
        Zone { z: NonZeroU32::new_unchecked(zone) }
    }
}
