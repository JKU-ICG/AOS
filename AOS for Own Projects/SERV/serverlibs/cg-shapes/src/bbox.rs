use cgmath::Vector3;
use crate::{RayIntersect, Ray};

/// Bounding Box implementation based on http://people.csail.mit.edu/amy/papers/box-jgt.pdf
#[derive(Debug, Clone)]
pub struct BBox {
    min: Vector3<f32>,
    max: Vector3<f32>,
}

impl BBox {
    pub fn new(min: Vector3<f32>, max: Vector3<f32>) -> Self {
        assert!(min.x <= max.x && min.y <= max.y && min.z <= max.z);
        Self { min, max }
    }

    pub fn for_vertexes_par(verts: &[Vector3<f32>]) -> Option<Self> {
        use rayon::prelude::*;
        let result: BBox = verts
            .par_chunks_exact(3) // should use the fold operation
            .map(BBox::for_vertexes) // but should work
            .reduce(Self::no_box, Self::combine);

        if result.valid_box() {
            Some(result)
        } else {
            None
        }
    }

    pub fn for_index_list_par<I: Into<u32> + Send + Sync + Copy>(
        vert_list: &[f32],
        indexes: &[I],
    ) -> Self {
        use rayon::prelude::*;
        let result: BBox = indexes
            .par_chunks(1024)
            .map(|i| Self::for_index_list(vert_list, i))
            .reduce(Self::no_box, Self::combine);

        result
    }

    /// maybe useless to make this generic over u16 and u32 index type
    /// but it is really neat and less complicated as I expected.
    ///
    /// The index type I has to be any type that implements the Into<usize> trait.
    /// Meaning: it can be used as a vector index.
    #[inline(always)]
    pub fn for_index_list<I: Into<u32> + Copy>(
        vert_list: &[f32],
        indexes: &[I],
    ) -> Self {
        assert!(indexes.len() > 0);

        let result = indexes
            .iter()
            .map(|i| {
                let offset = (*i).into() as usize * 3;
                Vector3::new(
                    vert_list[offset + 0],
                    vert_list[offset + 1],
                    vert_list[offset + 2],
                )
            })
            .fold(Self::no_box(), Self::including_vert);
        debug_assert!(result.valid_box());
        result
    }

    pub fn for_vertexes(verts: &[Vector3<f32>]) -> Self {
        assert!(verts.len() > 0);
        let result = verts
            .iter()
            .cloned()
            .fold(Self::no_box(), Self::including_vert);
        debug_assert!(result.valid_box());
        result
    }

    #[inline(always)]
    fn including_vert(self, vert: Vector3<f32>) -> Self {
        Self {
            min: Vector3::new(
                self.min.x.min(vert.x),
                self.min.y.min(vert.y),
                self.min.y.min(vert.z),
            ),
            max: Vector3::new(
                self.max.x.max(vert.x),
                self.max.y.max(vert.y),
                self.max.z.max(vert.z),
            ),
        }
    }

    #[inline(always)]
    pub fn combine(self, other: Self) -> Self {
        Self {
            min: Vector3 {
                x: self.min.x.min(other.min.x),
                y: self.min.y.min(other.min.y),
                z: self.min.z.min(other.min.z),
            },
            max: Vector3 {
                x: self.max.x.max(other.max.x),
                y: self.max.y.max(other.max.y),
                z: self.max.z.max(other.min.z),
            },
        }
    }

    #[inline(always)]
    fn no_box() -> Self {
        Self {
            min: Vector3::new(f32::MAX, f32::MAX, f32::MAX),
            max: Vector3::new(f32::MIN, f32::MIN, f32::MIN),
        }
    }

    #[inline(always)]
    fn valid_box(&self) -> bool {
        self.min.x <= self.max.x
            && self.min.y <= self.max.y
            && self.min.z <= self.max.z
    }
}

impl RayIntersect for BBox {

    fn ray_intersect(&self, ray: &Ray) -> Option<f32> {
        if intersection(self, ray) {
            Some(1.0)
        } else {
            None
        }
    }
}

/// normal improved version described in http://people.csail.mit.edu/amy/papers/box-jgt.pdf
#[allow(dead_code)]
fn intersection_old(bbox: &BBox, ray: &Ray) -> Option<f32> {
    let div_r = 1.0 / ray.direction;
    let (txmin, txmax) = if div_r.x > 0.0 {
        (
            (bbox.min.x - ray.origin.x) * div_r.x,
            (bbox.max.x - ray.origin.x) * div_r.x,
        )
    } else {
        (
            (bbox.max.x - ray.origin.x) * div_r.x,
            (bbox.min.x - ray.origin.x) * div_r.x,
        )
    };

    let (tymin, tymax) = if div_r.y >= 0.0 {
        (
            (bbox.min.y - ray.origin.y) * div_r.y,
            (bbox.max.y - ray.origin.y) * div_r.y,
        )
    } else {
        (
            (bbox.max.y - ray.origin.y) * div_r.y,
            (bbox.min.y - ray.origin.y) * div_r.y,
        )
    };

    if txmin > tymax || tymin > txmax {
        return None;
    }

    let tmin = tymin.max(txmin);
    let tmax = tymax.min(txmax);

    let (tzmin, tzmax) = if div_r.z >= 0.0 {
        (
            (bbox.min.z - ray.origin.z) * div_r.z,
            (bbox.max.z - ray.origin.z) * div_r.z,
        )
    } else {
        (
            (bbox.max.z - ray.origin.z) * div_r.z,
            (bbox.min.z - ray.origin.z) * div_r.z,
        )
    };

    if tmin > tzmax || tzmin > tmax {
        return None;
    }

    let tmin = tmin.max(tzmin);
    let tmax = tmax.min(tzmax);

    if tmin < 1000.0 && tmax > 0.0 {
        Some(1.0)
    } else {
        None
    }
}

/// source: https://tavianator.com/2015/ray_box_nan.html
fn intersection(b: &BBox, ray: &Ray) -> bool {
    // TODO nach slides fragen

    let r_inv: Vector3<f32> = 1.0 / ray.direction;
    let mut t1 = (b.min.x - ray.origin.x) * r_inv.x;
    let mut t2 = (b.max.x - ray.origin.x) * r_inv.x;

    let mut tmin = t1.min(t2);
    let mut tmax = t1.max(t2);

    for i in 1..3 {
        t1 = (b.min[i] - ray.origin[i]) * r_inv[i];
        t2 = (b.max[i] - ray.origin[i]) * r_inv[i];

        tmin = tmin.max(t1.min(t2).min(tmax));
        tmax = tmax.min(t1.max(t2).max(tmin));
    }


    tmax > tmin.max(0.0)
}

#[cfg(test)]
mod test {
    use cgmath::{Vector3, Point3};
    use crate::{BBox, Ray};
    use crate::bbox::intersection;

    #[test]
    fn bbox_intersect_basic() {
        let bbox = BBox {
            min: Vector3::new(-1.0, -1.0, -1.0),
            max: Vector3::new(1.0, 1.0, 1.0),
        };

        let mut ray = Ray {
            origin: Point3::new(0.0, 0.0, -10.0),
            direction: Vector3::new(0.0, 0.0, 1.0),
        };

        assert!(intersection(&bbox, &ray));

        ray.origin.x = 0.9999999;
        assert!(intersection(&bbox, &ray));

        ray.origin.y = 0.999999;
        assert!(intersection(&bbox, &ray));

        ray.origin.x = -0.99999;
        assert!(intersection(&bbox, &ray));

        ray.origin.y = -0.99999;
        assert!(intersection(&bbox, &ray));
    }
}