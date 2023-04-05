use cgmath::{Point3, Vector3};

/// Describes a ray by an origin point and a direction vector.
///
/// The direction vector MUST have a length, but does not need to be a unit-vector
#[derive(Debug, Clone)]
pub struct Ray {
    /// ray origin
    pub origin: Point3<f32>,
    /// ray direction, not normalized
    pub direction: Vector3<f32>,
}

impl Ray {

    /// Calculate the point that when moving distance*direction away from origin.
    ///
    /// ```
    /// # use cg_shapes::Ray;
    /// # use cgmath::{Point3, Vector3};
    /// let ray = Ray {
    ///         origin: Point3::new(0.0, 0.0, 0.0),
    ///         direction: Vector3::new(1.0, 0.5, 0.0)
    /// };
    ///
    /// assert_eq!(ray.cast_distance(0.0), Point3::new(0.0, 0.0, 0.0));
    /// assert_eq!(ray.cast_distance(1.0), Point3::new(1.0, 0.5, 0.0));
    /// assert_eq!(ray.cast_distance(-5.0), Point3::new(-5.0, -2.5, 0.0));
    /// ```
    pub fn cast_distance(&self, distance: f32) -> Point3<f32> {
        self.origin + self.direction * distance
    }
}