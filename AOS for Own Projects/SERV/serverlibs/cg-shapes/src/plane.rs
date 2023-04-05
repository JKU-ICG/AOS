use cgmath::prelude::*;
use cgmath::{Point3, Vector3};
use crate::{RayIntersect, Ray};

/// A 3d plane described as a point within the plane and a normal vector.
#[derive(Debug, Clone)]
pub struct Plane {
    pub point: Point3<f32>,
    // plane normal vector, should be normalized
    pub normal: Vector3<f32>,
}

impl Plane {
    /// Plane that is parallel to the x-y plane.
    ///
    /// ```
    /// # use crate::cg_shapes::Plane;
    /// # use cgmath::{Point3, Vector3};
    ///
    /// let plane = Plane::xy_plane(5.0);
    ///
    /// assert_eq!(plane.point, Point3::new(0.0, 0.0, 5.0));
    /// assert_eq!(plane.normal, Vector3::new(0.0, 0.0, 1.0));
    /// ```
    pub fn xy_plane(z_coord: f32) -> Plane {
        Plane {
            point: Point3::new(0.0, 0.0, z_coord),
            normal: Vector3::new(0.0, 0.0, 1.0),
        }
    }

    /// Normalizes the normal vector of the plane
    ///
    /// ```
    /// # use crate::cg_shapes::Plane;
    /// # use cgmath::{Point3, Vector3};
    /// # use cgmath::prelude::*;
    ///
    /// let mut plane = Plane {
    ///    point: Point3::new(1.0, 2.0, 4.0),
    ///    normal: Vector3::new(3.0, 5.0, 1.0),
    /// };
    ///
    /// plane.normalize();
    ///
    /// assert!((plane.normal.magnitude() - 1.0).abs() < 0.0001);
    /// ```
    pub fn normalize(&mut self) {
        self.normal = self.normal.normalize()
    }
}

impl RayIntersect for Plane {
    // Calculate the distance to the passed plane
    // in multiples of self.direction.length
    fn ray_intersect(&self, ray: &Ray) -> Option<f32> {
        let nom = self.normal.dot(self.point - ray.origin);
        let denom = self.normal.dot(ray.direction);
        if denom != 0.0 {
            Some(nom / denom)
        } else {
            None
        }
    }
}
