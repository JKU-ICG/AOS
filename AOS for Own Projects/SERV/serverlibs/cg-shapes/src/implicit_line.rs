use cgmath::{Point3, ElementWise, InnerSpace, MetricSpace, EuclideanSpace};

pub struct ImplicitLine {
    /// Center point of the cline
    pub p: [f32;3],
    /// Normal vector to the plane the line exists on. Must have length = 1.0
    pub n: [f32;3],
    /// Distance to the center point where the line ends (squared, to avoid needing to calculate square roots)
    pub d2: f32,
    /// Line width
    pub w: f32,
}


impl ImplicitLine {
    pub fn new(p0: Point3<f32>, p1: Point3<f32>, w: f32, color: [f32; 4]) -> Self {
        let mut center: Point3<f32> = p0 + p1.to_vec();
        center.mul_assign_element_wise(0.5);
        let dir: cgmath::Vector3<f32> = p1 - p0;
        let normal = dir.cross(cgmath::Vector3::unit_z()).normalize();
        let d2 = center.distance2(p0);
        Self {
            p: center.into(),
            n: normal.into(),
            d2,
            w
        }
    }

}