use crate::Ray;
use cgmath::Point3;

/// Can be implemented by any 3d shape to allow ray-casting onto the shape
pub trait RayIntersect {
    /// Calculate the distance from the ray origin to the intersection point.
    ///
    /// Returns `None`, when the ray does not intersect the shape.
    /// Returns `Some(f)` when the ray intersects self.
    ///
    /// See [Self::cast_ray()] to get the intersection point by using [Ray::cast_distance]
    /// on the result
    fn ray_intersect(&self, ray: &Ray) -> Option<f32>;

    /// Returns `true` when `ray` intersects self.
    ///
    /// When the actual distance is not needed then this function should be used
    fn does_intersect(&self, ray: &Ray) -> bool {
        self.ray_intersect(ray).is_some()
    }

    /// Calculate the intersection point of self with `ray`
    ///
    /// Returns None when the ray does not intersect `self`
    #[inline]
    fn ray_intersection_point(&self, ray: &Ray) -> Option<Point3<f32>> {
        self.ray_intersect(ray).map(|d| ray.cast_distance(d))
    }
}
