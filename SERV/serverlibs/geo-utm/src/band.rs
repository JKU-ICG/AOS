use crate::Error;
use std::convert::TryFrom;

#[allow(unused)]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd)]
#[derive(num_enum::TryFromPrimitive, serde::Deserialize, serde::Serialize)]
#[repr(u8)]
pub enum Band {
    C = 0,
    D = 1,
    E = 2,
    F = 3,
    G = 4,
    H = 5,
    J = 6,
    K = 7,
    L = 8,
    M = 9,
    N = 10,
    P = 11,
    Q = 12,
    R = 13,
    S = 14,
    T = 15,
    U = 16,
    V = 17,
    W = 18,
    X = 19,
}

impl Band {
    pub fn from_char(ch: char) -> Result<Band, Error> {
        match ch {
            'C'..='H' => Ok(Band::try_from(ch as u8 - 'C' as u8).unwrap()),
            'J'..='N' => Ok(Band::try_from(ch as u8 - 'C' as u8 - 1).unwrap()),
            'P'..='X' => Ok(Band::try_from(ch as u8 - 'C' as u8 - 2).unwrap()),
            _ => Err(Error::ParseError),
        }
    }
}

impl From<Band> for Hemisphere {
    fn from(b: Band) -> Self {
        if b < Band::N {
            Hemisphere::S
        } else {
            Hemisphere::N
        }
    }
}


#[derive(Copy, Clone, Debug, Eq, PartialEq)]
pub enum Hemisphere {
    N,
    S,
}