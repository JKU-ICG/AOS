use crate::{RayIntersect, Ray};
use cgmath::Point3;

/// A Triangle described by 3 points
///
/// Is a newtype for `[Point3<f32; 3]`
pub struct Triangle(pub [Point3<f32>; 3]);

impl Triangle {
    /// Create a triangle from a vertex list and 3 indexes.
    /// The vertex list is a flat slice of `f32` where 3 consecutive `f32` are interpreted
    /// as a single vertex.
    ///
    /// # Example:
    ///
    /// ```
    /// # use cg_shapes::Triangle;
    /// # use cgmath::Point3;
    ///
    /// let positions: Vec<f32> = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0];
    ///
    /// let triangle = Triangle::indexed_tri(0, 2, 1, &positions);
    /// assert_eq!(triangle.0,
    ///     [Point3::new(1.0, 2.0, 3.0),
    ///      Point3::new(7.0, 8.0, 9.0),
    ///      Point3::new(4.0, 5.0, 6.0)]
    /// );
    /// ```
    #[inline(always)]
    pub fn indexed_tri(i0: u32, i1: u32, i2: u32, positions: &[f32]) -> Triangle {
        positions.chunks_exact(3);
        let i0 = i0 as usize * 3;
        let i1 = i1 as usize * 3;
        let i2 = i2 as usize * 3;
        Triangle([
            Point3::new(positions[i0 + 0], positions[i0 + 1], positions[i0 + 2]),
            Point3::new(positions[i1 + 0], positions[i1 + 1], positions[i1 + 2]),
            Point3::new(positions[i2 + 0], positions[i2 + 1], positions[i2 + 2]),
        ])
    }
}

/// Basic ray intersection for the triangle.
///
/// The algorithm is based on Möller-Trumbore triangle intersection
///
/// # Exmples
///
/// ```
/// # use cg_shapes::{Ray, Triangle, RayIntersect};
/// # use cgmath::{Point3, Vector3};
/// use cg_shapes::assert_eq_f32;
///
/// let triangle = Triangle([
///         Point3::new(-1.0, 1.0, 0.0),
///         Point3::new(-1.0, -1.0, 0.0),
///         Point3::new(1.0, 1.0, 0.0)]);
///
/// let ray = Ray {
///     origin: Point3::new(0.0, 0.0, -1.0),
///     direction: Vector3::new(0.0, 0.0, 1.0),
/// };
///
/// assert_eq!(triangle.does_intersect(&ray), true);
/// assert_eq_f32!(triangle.ray_intersect(&ray).unwrap(), 1.0);
///
/// let pt: Point3<f32> = triangle.ray_intersection_point(&ray).unwrap();
/// assert_eq_f32!(pt, Point3::new(0.0, 0.0, 0.0));
/// ```
///
/// ## No intersection when ray points into the other direction
/// ```
/// # use cg_shapes::{Ray, Triangle, RayIntersect};
/// # use cgmath::{Point3, Vector3};
/// # use cg_shapes::assert_eq_f32;
///
/// let triangle = Triangle([
///         Point3::new(-1.0, 1.0, 0.0),
///         Point3::new(-1.0, -1.0, 0.0),
///         Point3::new(1.0, 1.0, 0.0)]);
///
/// let ray = Ray {
///     origin: Point3::new(0.0, 0.0, -1.0),
///     direction: Vector3::new(0.0, 0.0, -1.0),
/// };
///
/// assert_eq!(triangle.does_intersect(&ray), false);
/// assert_eq!(triangle.ray_intersect(&ray), None);
/// assert_eq!(triangle.ray_intersection_point(&ray), None);
/// ```
impl RayIntersect for Triangle {

    ///
    /// Only calculate the distance factor - not the actual point
    #[inline(always)]
    fn ray_intersect(&self, ray: &Ray) -> Option<f32> {
        use cgmath::prelude::*;
        const EPSILON: f32 = 0.00001;
        let edge1 = &self.0[1] - &self.0[0];
        let edge2 = &self.0[2] - &self.0[0];
        let s = ray.origin - &self.0[0];

        let h = ray.direction.cross(edge2);
        let a = edge1.dot(h);
        if a > -EPSILON && a < EPSILON {
            // parallel to triangle
            return None;
        }

        let f = 1.0 / a;

        let u = f * s.dot(h);
        if u < 0.0 || u > 1.0 {
            return None;
        }

        let q = s.cross(edge1);
        let v = f * ray.direction.dot(q);
        if v < 0.0 || u + v > 1.0 {
            return None;
        }
        let t = f * edge2.dot(q);
        if t > EPSILON {
            Some(t)
        } else {
            None
        }
    }
}