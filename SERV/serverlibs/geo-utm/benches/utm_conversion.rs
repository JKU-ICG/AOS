#[macro_use]
extern crate criterion;

use criterion::Criterion;
use geo_utm::*;
use rand::Rng;
use std::ops::Deref;

fn criterion_benchmark(c: &mut Criterion) {
    let gps_base = LatLon {
        lat: Deg(48.31956),
        lon: Deg(14.43972),
    };

    let coordinates: Vec<LatLon> = (0..10000)
        .into_iter()
        .map(|_| LatLon {
            lat: Deg(gps_base.lat.0 + rand::thread_rng().gen::<f64>() * 0.01),
            lon: Deg(gps_base.lon.0 + rand::thread_rng().gen::<f64>() * 0.01),
        })
        .collect();

    let mut group = c.benchmark_group("GPS to UTM conversion");

    group.bench_with_input("single_coord utm", &gps_base, |bh, input| {
        bh.iter(|| input.to_utm().unwrap())
    });
    group.bench_with_input("single_coord utm extra", &gps_base, |bh, input| {
        bh.iter(|| input.to_utm_extra().unwrap())
    });
    // let cfg = UtmConfig {
    //     ellipsoidal: WGS84.deref(),
    //     zone_override: None,
    //     band_override: None,
    // };
    // group.bench_with_input(
    //     "single_coord utm extra configured all_none",
    //     &gps_base,
    //     |bh, input| bh.iter(|| input.to_utm_extra_configured(cfg).unwrap()),
    // );
    //
    // let cfg = UtmConfig {
    //     ellipsoidal: WGS84.deref(),
    //     zone_override: Some(Zone::new(33).unwrap()),
    //     band_override: Some(Band::U),
    // };
    //
    // group.bench_with_input(
    //     "single_coord utm extra configured all_some",
    //     &gps_base,
    //     |bh, input| bh.iter(|| input.to_utm_extra_configured(cfg).unwrap()),
    // );

    let base = gps_base.to_utm().unwrap();

    group.bench_with_input("relative_coord", coordinates.get(1).unwrap(), |b, input| {
        b.iter(|| input.to_relative_utm(&base))
    });

    group.bench_with_input("relative_coord vec 1000", &coordinates[..], |b, input| {
        b.iter(|| {
            input
                .into_iter()
                .map(|c| c.to_relative_utm(&base))
                .collect::<Vec<UtmRelative>>()
        })
    });

    group.finish();
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
