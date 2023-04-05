use criterion::{black_box, criterion_group, criterion_main, Criterion};
use cg_shapes::{BBox, Ray, RayIntersect, Triangle};
use cgmath::{Point3, Vector3};
use std::time::Duration;
use std::path::Path;
use std::fmt::Debug;
use std::fs::File;
use std::io::BufReader;
use anyhow::Context;
use rand::prelude::*;
use rayon::prelude::*;

/// make a shortcut, just get the first model in the file, throw away everything else
async fn load_model<P>(src: P) -> anyhow::Result<tobj::Model>
    where
        P: AsRef<Path> + Debug,
{
    let p = src.as_ref();
    let model_path = p.with_extension("model");
    if model_path.exists() {
        let file = File::open(model_path)?;
        let reader = BufReader::new(file);
        let ser: ModelSer = bincode::deserialize_from(reader)?;
        Ok(ser.0)
    } else {
        let result = tobj::load_obj(&src, false)
            .context(format!("Failed to load {:?}", src))?;

        let first_model = result.0.get(0).context("No model in file")?;

        Ok(first_model.clone())
    }
}


#[derive(serde::Serialize, serde::Deserialize)]
struct ModelSer(#[serde(with = "ModelDef")] tobj::Model);

#[derive(serde::Serialize, serde::Deserialize)]
#[serde(remote = "tobj::Model")]
pub struct ModelDef {
    #[serde(with = "MeshDef")]
    pub mesh: tobj::Mesh,
    pub name: String,
}

#[derive(serde::Serialize, serde::Deserialize)]
#[serde(remote = "tobj::Mesh")]
pub struct MeshDef {
    pub positions: Vec<f32>,
    pub normals: Vec<f32>,
    pub texcoords: Vec<f32>,
    pub indices: Vec<u32>,
    pub num_face_indices: Vec<u32>,
    pub material_id: Option<usize>,
}

pub struct TerrainData {
    model: tobj::Model,
    bbox: BBox,
}

impl RayIntersect for TerrainData {
    fn ray_intersect(&self, ray: &Ray) -> Option<f32> {
        if self.bbox.does_intersect(ray) {
            let positions = self.model.mesh.positions.as_slice();
            let indices = self.model.mesh.indices.as_slice();

            indices
                .par_chunks_exact(3)
                .map(|chunk| {
                    Triangle::indexed_tri(chunk[0], chunk[1], chunk[2], positions)
                })
                .find_map_any(|tri| tri.ray_intersect(ray))
        } else {
            None
        }
    }
}

pub struct ResolvedTerrainData {
    triangles: Vec<Triangle>,
    bbox: BBox,
}

impl ResolvedTerrainData {
    pub fn from_terrain(t: TerrainData) -> Self {
        let positions = t.model.mesh.positions.as_slice();
        let indices = t.model.mesh.indices.as_slice();

        let triangles = indices
            .par_chunks_exact(3)
            .map(|chunk| {
                Triangle::indexed_tri(chunk[0], chunk[1], chunk[2], positions)
            })
            .collect();

        Self {
            triangles,
            bbox: t.bbox.clone(),
        }
    }
}

impl RayIntersect for ResolvedTerrainData {
    fn ray_intersect(&self, ray: &Ray) -> Option<f32> {
        if self.bbox.does_intersect(ray) {
            self.triangles.par_chunks(256)
                .find_map_any(|ch| ch.iter().find_map(|tri| tri.ray_intersect(ray)))
        } else {
            None
        }
    }
}


fn criterion_benchmark(c: &mut Criterion) {
    let file = std::fs::File::open(
        "/home/andi/dev/SARViewer/data/Test20201022F1/LFR/dem.model",
    )
        .unwrap();
    let reader = std::io::BufReader::new(file);

    let model: ModelSer = bincode::deserialize_from(reader).unwrap();


    let bbox = BBox::for_index_list_par(
        model.0.mesh.positions.as_slice(),
        model.0.mesh.indices.as_slice(),
    );


    let data = TerrainData {
        model: model.0,
        bbox,
    };

    let mut rand = SmallRng::seed_from_u64(0);

    let rays: Vec<Ray> = (0..200)
        .into_iter()
        .map(|_| Ray {
            origin: Point3::new(
                rand.gen_range(-150.0, 150.0),
                rand.gen_range(-150.0, 150.0),
                rand.gen_range(-600.0, -400.0),
            ),
            direction: Vector3::new(
                rand.gen_range(-0.1, 0.1),
                rand.gen_range(-0.1, 0.1),
                1.0,
            ),
        })
        .collect();

    let ray = Ray {
        origin: Point3::new(-0.0, 0.0, -800.0),
        direction: Vector3::new(0.0, 0.0, 1.0),
    };
    c.bench_function("Terrain_intersect 0:0", |b| b.iter(|| data.ray_intersect(&ray)));

    let resolved = ResolvedTerrainData::from_terrain(data);
    c.bench_function("Terrain_intersect resolved 0:0", |b| b.iter(|| resolved.ray_intersect(&ray)));
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);