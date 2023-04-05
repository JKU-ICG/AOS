use crate::file_db::FileObject;
use serde::Deserialize;
use sar_types::MyFilter;

pub trait LocationHolder {
    fn get_location_id(&self) -> Option<&str>;
}

pub trait DroneHolder {
    fn get_drone_id(&self) -> Option<&str>;
}


pub trait Filterable {
    fn matches(&self, filter: &MyFilter) -> bool;
}


#[inline]
pub fn filter_by_id(o: &impl FileObject, filter: &MyFilter) -> bool {
    filter.min_id.as_deref().map_or(true, |min_id| o.get_id() >= min_id)
}

#[inline]
pub fn filter_by_drone_id(o: &impl DroneHolder, filter: &MyFilter) -> bool {
    match (filter.drone_id.as_deref(), o.get_drone_id()) {
        (None, _) => true,
        (_, None) => false,
        (Some(expected), Some(given)) => given == expected,
    }
}

#[inline]
pub fn filter_by_location_id(o: &impl LocationHolder, filter: &MyFilter) -> bool {
    match (filter.location_id.as_deref(), o.get_location_id()) {
        (None, _) => true,
        (_, None) => false,
        (Some(expected), Some(given)) => given == expected,
    }
}

#[inline]
pub(crate) fn do_filter<T: FileObject + DroneHolder + LocationHolder>(
    o: &T,
    filter: &MyFilter,
) -> bool {
    filter_by_drone_id(o, filter) && filter_by_location_id(o, filter) && filter_by_id(o, filter)
}


#[cfg(test)]
mod test {
    use crate::filter::MyFilter;

    #[test]
    fn test_filter() {
        println!("{}", std::mem::size_of::<MyFilter>())
    }
}
