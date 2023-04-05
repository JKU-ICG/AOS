use std::ops::{Add, Sub};

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct Rad(pub f64);

impl Rad {
    pub fn to_degrees(self) -> Deg {
        Deg(self.0 * (180.0 / std::f64::consts::PI))
    }
}

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct Deg(pub f64);

impl Deg {
    #[inline(always)]
    pub fn to_radians(self) -> Rad {
        Rad(self.0 * (std::f64::consts::PI / 180.0))
    }
}

impl From<Deg> for f64 {
    fn from(d: Deg) -> Self {
        d.0
    }
}

impl Add for Deg {
    type Output = Deg;

    fn add(self, rhs: Self) -> Self::Output {
        Deg(self.0 + rhs.0)
    }
}

impl Sub for Deg {
    type Output = Deg;

    fn sub(self, rhs: Self) -> Self::Output {
        Deg(self.0 - rhs.0)
    }
}
