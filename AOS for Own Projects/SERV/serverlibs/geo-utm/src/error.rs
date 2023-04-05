use std::fmt::{Display, Formatter};

#[derive(Copy, Clone, Debug, PartialEq)]
pub enum Error {
    InvalidZone,
    NaN,
    ZoneOutOfRange,
    IncompatibleZone,
    ParseError,
}

impl Display for Error {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        std::fmt::Debug::fmt(self, f)
    }
}

impl std::error::Error for Error {

}
