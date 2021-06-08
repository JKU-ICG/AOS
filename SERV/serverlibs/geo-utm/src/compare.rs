pub trait CoordinateCompare<T> {
    fn is_eq_by(&self, other: &Self, delta: T) -> bool;

    fn is_eq(&self, other: &Self) -> bool;
}

pub(crate) trait SimpleFloatEq {
    fn delta_eq(self, other: Self) -> bool;

    fn var_delta_eq(self, other: Self, epsilon: Self) -> bool;
}

impl SimpleFloatEq for f32 {
    #[inline(always)]
    fn delta_eq(self, other: Self) -> bool {
        self.var_delta_eq(other, 0.0001)
    }

    #[inline(always)]
    fn var_delta_eq(self, other: Self, epsilon: Self) -> bool {
        (self - other).abs() < epsilon
    }
}

impl SimpleFloatEq for f64 {
    #[inline(always)]
    fn delta_eq(self, other: Self) -> bool {
        self.var_delta_eq(other, 0.0001)
    }

    #[inline(always)]
    fn var_delta_eq(self, other: Self, epsilon: Self) -> bool {
        (self - other).abs() < epsilon
    }
}
