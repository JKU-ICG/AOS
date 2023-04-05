#[macro_export]
macro_rules! assert_eq_f32 {
    ($l:expr, $r:expr) => {{
        use $crate::float_eq::SimpleFloatEq;
        let v_l = $l;
        let v_r = $r;
        if !v_l.delta_eq(v_r) {
            panic!("Float values are not equal: {:?} != {:?}", v_l, v_r);
        }
    }}
}

pub trait SimpleFloatEq {
    fn delta_eq(self, other: Self) -> bool;
}

impl SimpleFloatEq for f32 {
    fn delta_eq(self, other: Self) -> bool {
        (self - other).abs() < 0.0001
    }
}

impl SimpleFloatEq for cgmath::Point3<f32> {
    fn delta_eq(self, other: Self) -> bool {
        self.x.delta_eq(other.x)
            && self.y.delta_eq(other.y)
            && self.z.delta_eq(other.z)
    }
}


#[cfg(test)]
mod test {
    use crate::float_eq::SimpleFloatEq;

    #[test]
    fn float_assertions() {
        assert_eq_f32!(1.0, 1.0);
        assert_eq_f32!(1.0, 1.000005);
        assert_eq_f32!(1.000005, 1.0);
        assert_eq_f32!(0.999995, 1.0);
        assert_eq_f32!(1.0, 0.999995);
    }

    #[test]
    fn blub() {
        assert_eq!(1.0f32.delta_eq(1.0002), false);
        assert_eq!(1.0f32.delta_eq(1.00005), true);
    }

    #[test]
    #[should_panic]
    fn failing_float_assertions_over() {
        assert_eq_f32!(1.0, 1.0002);
    }

    #[test]
    #[should_panic]
    fn failing_float_assertions_under() {
        assert_eq_f32!(1.0, 0.9998);
    }
}
