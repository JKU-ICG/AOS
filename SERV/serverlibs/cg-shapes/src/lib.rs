pub mod float_eq;
mod ray;
mod ray_intersect;
mod plane;
mod triangle;
mod bbox;
mod implicit_line;

pub use ray::Ray;
pub use ray_intersect::RayIntersect;
pub use plane::Plane;
pub use triangle::Triangle;
pub use bbox::BBox;


#[cfg(test)]
mod test {
    use cgmath::prelude::*;
    use cgmath::{Point3, Vector3};
    use crate::{Triangle, Ray, RayIntersect};

    type P = Point3<f32>;
    type V = Vector3<f32>;

    #[test]
    fn triangle_intersect_simple() {
        let tri = Triangle([
            P::new(-1.0, -1.0, 0.0),
            P::new(1.0, -1.0, 0.0),
            P::new(-1.0, 1.0, 0.0),
        ]);

        let ray = Ray {
            origin: P::new(0.0, 0.0, -3.0),
            direction: V::new(0.0, 0.0, 1.0),
        };

        assert_eq!(
            tri.ray_intersect(&ray).map(|d| ray.cast_distance(d)),
            Some(P::origin())
        );

        // intersection from the other side of the triangle
        let ray = Ray {
            origin: P::new(0.0, 0.0, 3.0),
            direction: V::new(0.0, 0.0, -1.0),
        };
        let int_p = tri.ray_intersect(&ray).map(|d| ray.cast_distance(d));
        assert_eq!(int_p, Some(P::origin()));

        // no intersection when origin at the same plane as the triangle
        let ray = Ray {
            origin: P::origin(),
            direction: V::new(0.0, 0.0, -1.0),
        };
        assert_eq!(tri.ray_intersect(&ray), None);

        // intersection with non-normalized ray direction
        let ray = Ray {
            origin: P::new(0.0, 0.0, 3.0),
            direction: V::new(0.0, 0.0, -100.0),
        };
        assert_eq!(
            tri.ray_intersect(&ray).map(|d| ray.cast_distance(d)),
            Some(P::origin())
        );

        // no intersection when ray parallel to triangle
        let ray = Ray {
            origin: P::new(0.0, 0.0, 3.0),
            direction: V::new(1.0, 1.0, 0.0),
        };
        assert_eq!(tri.ray_intersect(&ray), None);
    }
}
