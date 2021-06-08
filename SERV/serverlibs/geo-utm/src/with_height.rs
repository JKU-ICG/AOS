use std::fmt::{Display, Formatter};
use crate::utm::Utm;
use geo_types::Coordinate;
use serde::{Serialize, Serializer, Deserialize, Deserializer};
use serde::ser::SerializeTupleStruct;
use serde::de::{Visitor, SeqAccess};
use crate::zone::Zone;
use crate::band::Band;

#[derive(Clone, Debug, PartialEq)]
pub struct UtmHeight {
    pub pos: Utm,
    pub height: f32,
}

impl Display for UtmHeight {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} {} h", self.pos, self.height)
    }
}

impl Serialize for UtmHeight {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error> where
        S: Serializer {
        let mut seq_writer = serializer.serialize_tuple_struct("UtmHeight", 5)?;
        seq_writer.serialize_field(&self.pos.easting)?;
        seq_writer.serialize_field(&self.pos.northing)?;
        seq_writer.serialize_field(&self.pos.zone)?;
        seq_writer.serialize_field(&self.pos.band)?;
        seq_writer.serialize_field(&self.height)?;
        seq_writer.end()
    }
}

impl<'de> Deserialize<'de> for UtmHeight {
    fn deserialize<D>(deserializer: D) -> Result<Self, <D as Deserializer<'de>>::Error> where
        D: Deserializer<'de> {
        deserializer.deserialize_tuple_struct("UtmHeight", 5, UtmHeightVisitor)
        // deserializer.deserialize_seq(UtmHeightVisitor)
    }
}

struct UtmHeightVisitor;

impl<'de> Visitor<'de> for UtmHeightVisitor {
    type Value = UtmHeight;

    fn expecting<'a>(&self, f: &mut Formatter<'a>) -> std::fmt::Result {
        write!(f, "UtmHeight")
    }


    fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
        where
            A: SeqAccess<'de>,
    {
        use serde::de::Error;
        let easting: f64 = seq.next_element()?.ok_or(Error::missing_field("easting"))?;
        let northing: f64 = seq.next_element()?.ok_or(Error::missing_field("northing"))?;
        let zone: Zone = seq.next_element()?.ok_or(Error::missing_field("zone"))?;
        let band: Band = seq.next_element()?.ok_or(Error::missing_field("band"))?;
        let height: f32 = seq.next_element()?.ok_or(Error::missing_field("height"))?;

        Ok(UtmHeight {
            pos: Utm {
                easting,
                northing,
                zone,
                band,
            },
            height,
        })
    }
}


#[derive(Clone, Debug, PartialEq, serde::Deserialize, serde::Serialize)]
pub struct LonLatHeight {
    pub pos: Coordinate<f64>,
    pub height: f32,
}

impl Display for LonLatHeight {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} {} {}", self.pos.x, self.pos.y, self.height)
    }
}


#[cfg(test)]
mod test {
    use crate::with_height::{LonLatHeight, UtmHeight};
    use geo_types::Coordinate;
    use crate::utm::Utm;
    use crate::zone::Zone;
    use crate::band::Band;
    use std::ops::Deref;

    #[test]
    fn display() {
        let r = LonLatHeight {
            pos: Coordinate::zero(),
            height: 10.0,
        }.to_string();

        assert_eq!(&r, "0 0 10");
    }

    lazy_static! {
        static ref UTM1: UtmHeight = UtmHeight {
            pos: Utm {
                zone: Zone::new(33).unwrap(),
                band: Band::U,
                easting: 458464.0,
                northing: 5351971.0,
            },
            height: 100.5
        };
    }

    #[test]
    fn ser_de_UtmHeight() {
        let ser = serde_json::to_string(UTM1.deref()).unwrap();
        assert_eq!(ser, "[458464.0,5351971.0,33,\"U\",100.5]");
        let de: UtmHeight = serde_json::from_str(&ser).unwrap();
        assert_eq!(&de, UTM1.deref());
    }
}