#![allow(unused_imports)]

mod drone_images;
mod drone_info;
mod file_blob;
mod file_db;
mod filter;
mod flight_paths;
mod integral_images;
mod labels;
mod location_infos;

use crate::drone_images::{DBImage, ImagesTable};
use crate::drone_info::{DBDroneInfo, DroneInfos};
use crate::file_blob::Blobs;
use crate::file_db::{make_dir, DBError, FileTable, ObjState};
use crate::flight_paths::{DBFlightPath, FlightPathTable};
use crate::integral_images::{DBIntegralImage, IntegralImageTable};
use crate::labels::{DBLabel, LabelTable};
use crate::location_infos::{DBLocationInfo, LocationInfos};
use actix_web::dev::Service;
use actix_web::{
    error, guard, middleware, web, App, Error, HttpRequest, HttpResponse, HttpServer, Responder,
};
use anyhow::*;
use regex::Regex;
use sar_types::{FlightPath, MyFilter};
use serde::Serialize;
use std::path::{Path, PathBuf};
use std::sync::Arc;

#[actix_web::main]
async fn main() -> anyhow::Result<()> {
    // std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();
    let data = AppData::new();
    data.init_fs()
        .context("Failed to initialize data storage")?;
    data.load_all_data().await?;
    let data = web::Data::new(data);

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .wrap(middleware::Logger::default())
            .data(web::JsonConfig::default().limit(4096))
            .configure(configure_routes)
    })
    .workers(2)
    .keep_alive(300) // (in seconds) 5 sec default is too slow for the Pi!
    .bind("0.0.0.0:80")?
    .run()
    .await
    .context("Failed to init Actix server")
}

fn configure_routes(cfg: &mut web::ServiceConfig) {
    // Drones
    let is_png = || guard::Header("content-type", "image/png");
    cfg.service(
        web::resource("/drones")
            .route(web::get().to(list_drones))
            .route(web::post().to(register_drone)),
    )
    .service(
        web::resource("/drones/{drone_id}")
            .route(web::get().to(get_drone))
            .route(web::put().to(store_drone))
            .route(web::delete().to(delete_drone)),
    )
    .service(web::resource("/drones/{drone_id}/images").route(web::get().to(list_images_by_drone)))
    // Terrains
    .service(
        web::resource("/locations")
            .route(web::post().to(create_location))
            .route(web::get().to(list_locations)),
    )
    .service(
        web::resource("/locations/{location_id}.obj")
            .route(web::get().to(get_location_obj))
            .route(web::put().to(store_location_obj))
            .route(web::delete().to(delete_location_obj)),
    )
    .service(
        web::resource("/locations/{location_id}_shading.png")
            .route(web::get().to(get_location_shading_image))
            .route(web::put().guard(is_png()).to(store_location_shading_image))
            .route(web::delete().to(delete_location_shading_image)),
    )
    .service(
        web::resource("/locations/{location_id}_satellite.png")
            .route(
                web::put()
                    .guard(is_png())
                    .to(store_location_satellite_image),
            )
            .route(web::get().to(get_location_satellite_image))
            .route(web::delete().to(delete_location_satellite_image)),
    )
    .service(
        web::resource("/locations/{location_id}.model")
            .route(web::put().to(store_location_geometry))
            .route(web::get().to(get_location_geometry))
            .route(web::delete().to(delete_location_geometry)),
    )
    .service(
        web::resource("/locations/{location_id}.tiff")
            .route(web::put().to(store_location_tiff))
            .route(web::get().to(get_location_tiff))
            .route(web::delete().to(delete_location_tiff)),
    )
    .service(
        web::resource("/locations/{location_id}")
            .route(web::get().to(get_location))
            .route(web::put().to(store_location))
            .route(web::delete().to(delete_location)),
    )
    // Images
    .service(
        web::resource("/images")
            .route(web::get().to(list_images))
            .route(web::post().to(create_image)),
    )
    .service(
        web::resource("/images/{image_id}.png")
            .route(web::get().to(get_image_png))
            .route(web::put().guard(is_png()).to(store_image_png))
            .route(web::delete().to(delete_image_png)),
    )
    .service(
        web::resource("/images/{image_id}")
            .route(web::get().to(get_image))
            .route(web::put().guard(is_png()).to(store_image))
            .route(web::delete().to(delete_image)),
    )
    // pre-assigned images
    .service(
        web::resource("/locations/{location_id}/images")
            .route(web::get().to(list_images_per_location)),
    )
    .service(
        web::resource("/locations/{location_id}/drones/{drone_id}/images")
            .route(web::get().to(list_images_by_location_and_drone)),
    )
    // Integral images
    .service(
        web::resource("/integrals/{integral_id}.png")
            .route(web::put().guard(is_png()).to(store_integral_png))
            .route(web::get().to(get_integral_image_png))
            .route(web::delete().to(delete_integral_image_png)),
    )
    .service(
        web::resource("/integrals/{integral_id}")
            .route(web::get().to(get_integral_image))
            .route(web::put().to(store_integral_image))
            .route(web::delete().to(delete_integral_image)),
    )
    .service(
        web::resource("/integrals")
            .route(web::get().to(list_integral_images))
            .route(web::post().to(create_integral_image)),
    )
    .service(
        web::resource("/labels")
            .route(web::get().to(list_labels))
            .route(web::post().to(create_label)),
    )
    .service(
        web::resource("/labels/{label_id}")
            .route(web::put().to(store_label))
            .route(web::get().to(get_label))
            .route(web::delete().to(delete_label)),
    )
    .service(
        web::resource("/flight_paths")
            .route(web::get().to(list_flight_paths))
            .route(web::post().to(create_flight_path)),
    )
    .service(
        web::resource("/flight_paths/{id}")
            .route(web::put().to(store_flight_path))
            .route(web::get().to(get_flight_path))
            .route(web::delete().to(delete_flight_path)),
    );
}

type DBResponse = Result<HttpResponse, DBError>;

/// Lock order is always top to bottom of declaration order
#[derive(Clone)]
pub struct AppData {
    root_path: PathBuf,
    drones: Arc<DroneInfos>,
    locations: Arc<LocationInfos>,
    images: Arc<ImagesTable>,
    integral_images: Arc<IntegralImageTable>,
    labels: Arc<LabelTable>,
    flight_paths: Arc<FlightPathTable>,

    id_regex: Regex,
    image_ref_regex: Regex,
}

impl AppData {
    fn new() -> AppData {
        Self::with_root_path(&PathBuf::from("serverData"))
    }

    fn with_root_path(root: &Path) -> AppData {
        let drones_path = root.join("drones");
        let location_path = root.join("locations");
        let images_path = root.join("images");
        let integral_images_path = root.join("integral_images");
        let labels_path = root.join("labels");
        let locations = Arc::new(LocationInfos::new(location_path, "/locations/"));
        let drones = Arc::new(DroneInfos::new(drones_path, "/drones/"));
        let mut images = ImagesTable::new(images_path, "/images/");
        images.location_reference.init(locations.clone());
        images.drone_reference.init(drones.clone());

        let images = Arc::new(images);

        let mut labels = LabelTable::new(labels_path, "/labels/");
        labels.location_reference.init(locations.clone());

        let mut i_images = IntegralImageTable::new(integral_images_path, "/integrals/");
        i_images.location_reference.init(locations.clone());
        i_images.images_reference.init(images.clone());

        let mut flight_paths = FlightPathTable::new(root.join("flight_paths"), "/flight_paths/");
        flight_paths.location_ref.init(locations.clone());
        flight_paths.drone_ref.init(drones.clone());

        AppData {
            root_path: root.to_path_buf(),
            drones,
            locations,
            images,
            integral_images: Arc::new(i_images),
            labels: Arc::new(labels),
            flight_paths: Arc::new(flight_paths),
            id_regex: Regex::new(r#"^(\w|_|-)+$"#).unwrap(),
            image_ref_regex: Regex::new(r#"^/images/((?:\w|_|-)+)\.png"#).unwrap(),
        }
    }

    async fn load_all_data(&self) -> anyhow::Result<()> {
        let f1 = self.locations.load_all();
        let f2 = self.drones.load_all();
        let f3 = self.images.load_all();
        let f4 = self.integral_images.load_all();
        let f5 = self.labels.load_all();
        let f6 = self.flight_paths.load_all();

        let f = futures::future::try_join(f5, f6);

        futures::future::try_join5(f1, f2, f3, f4, f)
            .await
            .map_err(anyhow::Error::from)?;

        Ok(())
    }

    fn init_fs(&self) -> std::io::Result<()> {
        let abs_path = if self.root_path.is_absolute() {
            self.root_path.clone()
        } else {
            PathBuf::from(std::env::current_dir().unwrap()).join(&self.root_path)
        };
        log::info!("Initializing data directory at {}", abs_path.display());

        make_dir(&self.root_path)?;
        self.drones.init_directory()?;
        self.locations.init_directory()?;
        self.images.init_directory()?;
        self.integral_images.init_directory()?;
        self.labels.init_directory()?;
        self.flight_paths.init_directory()?;
        Ok(())
    }
}

async fn list_drones(data: web::Data<AppData>) -> DBResponse {
    data.drones.get_all().await.map(as_json)
}

async fn get_drone(drone_id: web::Path<String>, data: web::Data<AppData>) -> DBResponse {
    data.drones.get(drone_id.as_str()).await.map(as_json)
}

async fn register_drone(
    data: web::Data<AppData>,
    drone: web::Json<sar_types::DroneInfo>,
) -> DBResponse {
    data.drones
        .create(DBDroneInfo { data: drone.0 })
        .await
        .map(into_location_header)
}

async fn store_drone(
    data: web::Data<AppData>,
    drone_id: web::Path<String>,
    drone: web::Json<DBDroneInfo>,
) -> DBResponse {
    data.drones
        .insert_or_update(drone_id.as_str(), drone.0)
        .await
        .map(into_store_response)
}

async fn delete_drone(data: web::Data<AppData>, drone_id: web::Path<String>) -> DBResponse {
    data.drones
        .delete(drone_id.as_str())
        .await
        .map(|_| HttpResponse::NoContent().finish())
}

async fn list_locations(data: web::Data<AppData>) -> impl Responder {
    data.locations.get_all().await.map(as_json)
}

async fn create_location(
    data: web::Data<AppData>,
    location: web::Json<sar_types::LocationInfo>,
) -> impl Responder {
    data.locations
        .create(DBLocationInfo { data: location.0 })
        .await
        .map(into_location_header)
}

async fn get_location(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.locations.get(id.as_str()).await.map(as_json)
}

async fn store_location(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Json<sar_types::LocationInfo>,
) -> DBResponse {
    data.locations
        .insert_or_update(id.as_str(), DBLocationInfo { data: obj.0 })
        .await
        .map(into_store_response)
}

async fn delete_location(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.locations
        .delete(id.as_str())
        .await
        .map(as_empty_content)
}

async fn store_location_obj(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Payload,
) -> DBResponse {
    data.locations
        .store_related(location_infos::Relation::ObjFile, id.as_str(), obj)
        .await
        .map(into_store_response)
}

async fn get_location_obj(
    request: HttpRequest,
    data: web::Data<AppData>,
    id: web::Path<String>,
) -> Result<HttpResponse, Error> {
    data.locations
        .obj_files
        .id_to_actix_file(id.as_str())
        .and_then(|f| f.into_response(&request))
}

async fn delete_location_obj(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.locations
        .delete_related(location_infos::Relation::ObjFile, id.as_str())
        .await
        .map(as_empty_content)
}

async fn store_location_geometry(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Payload,
) -> DBResponse {
    data.locations
        .store_related(location_infos::Relation::Geometry, id.as_str(), obj)
        .await
        .map(into_store_response)
}

async fn get_location_geometry(
    data: web::Data<AppData>,
    id: web::Path<String>,
    req: web::HttpRequest,
) -> impl Responder {
    data.locations
        .geometry_files
        .id_to_actix_file(id.as_str())
        .and_then(|f| f.into_response(&req))
}

async fn delete_location_geometry(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.locations
        .delete_related(location_infos::Relation::Geometry, id.as_str())
        .await
        .map(as_empty_content)
}

async fn store_location_satellite_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Payload,
) -> DBResponse {
    data.locations
        .store_related(location_infos::Relation::SatelliteImage, id.as_str(), obj)
        .await
        .map(into_store_response)
}

async fn get_location_satellite_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
    req: web::HttpRequest,
) -> Result<HttpResponse, Error> {
    data.locations
        .satellite_images
        .id_to_actix_file(id.as_str())
        .and_then(|f| f.into_response(&req))
}

async fn delete_location_satellite_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
) -> DBResponse {
    data.locations
        .delete_related(location_infos::Relation::SatelliteImage, id.as_str())
        .await
        .map(as_empty_content)
}

async fn store_location_shading_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Payload,
) -> DBResponse {
    data.locations
        .store_related(location_infos::Relation::ShadingImage, id.as_str(), obj)
        .await
        .map(into_store_response)
}

async fn get_location_shading_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
    req: web::HttpRequest,
) -> Result<HttpResponse, Error> {
    data.locations
        .shading_images
        .id_to_actix_file(id.as_str())
        .and_then(|f| f.into_response(&req))
}

async fn delete_location_shading_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
) -> DBResponse {
    data.locations
        .delete_related(location_infos::Relation::ShadingImage, id.as_str())
        .await
        .map(as_empty_content)
}

async fn store_location_tiff(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Payload,
) -> DBResponse {
    data.locations
        .store_related(location_infos::Relation::GeoTiffFile, id.as_str(), obj)
        .await
        .map(into_store_response)
}

async fn get_location_tiff(
    data: web::Data<AppData>,
    id: web::Path<String>,
    req: web::HttpRequest,
) -> impl Responder {
    data.locations
        .geo_tiff_files
        .id_to_actix_file(id.as_str())
        .and_then(|f| f.into_response(&req))
}

async fn delete_location_tiff(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.locations
        .delete_related(location_infos::Relation::GeoTiffFile, id.as_str())
        .await
        .map(as_empty_content)
}

async fn create_image(data: web::Data<AppData>, image: web::Json<sar_types::Image>) -> DBResponse {
    data.images
        .create(DBImage { data: image.0 })
        .await
        .map(into_location_header)
}

async fn list_images(data: web::Data<AppData>, filter: web::Query<MyFilter>) -> DBResponse {
    data.images.get_filtered2(filter.0).await.map(as_json)
}

async fn list_images_per_location(
    data: web::Data<AppData>,
    location_id: web::Path<String>,
    filter: web::Query<MyFilter>,
) -> DBResponse {
    let mut filter = filter.0;
    filter.location_id = Some(location_id.0);

    data.images.get_filtered2(filter).await.map(as_json)
}

async fn list_images_by_drone(
    data: web::Data<AppData>,
    drone_id: web::Path<String>,
    filter: web::Query<MyFilter>,
) -> DBResponse {
    let mut filter = filter.0;
    filter.drone_id = Some(drone_id.0);

    data.images.get_filtered2(filter).await.map(as_json)
}

async fn list_images_by_location_and_drone(
    data: web::Data<AppData>,
    location_id: web::Path<String>,
    drone_id: web::Path<String>,
    filter: web::Query<MyFilter>,
) -> DBResponse {
    let mut filter = filter.0;
    filter.drone_id = Some(drone_id.0);
    filter.location_id = Some(location_id.0);

    data.images.get_filtered2(filter).await.map(as_json)
}

async fn get_image(data: web::Data<AppData>, id: web::Path<String>) -> impl Responder {
    data.images.get(id.as_str()).await.map(as_json)
}

async fn store_image(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Json<sar_types::Image>,
) -> DBResponse {
    data.images
        .insert_or_update(id.as_str(), DBImage { data: obj.0 })
        .await
        .map(into_store_response)
}

async fn delete_image(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.images.delete(id.as_str()).await.map(as_empty_content)
}

async fn get_image_png(
    request: HttpRequest,
    data: web::Data<AppData>,
    id: web::Path<String>,
) -> Result<HttpResponse, Error> {
    if !data.id_regex.is_match(id.as_str()) {
        log::info!("Invalid png image id: {}", id.as_str());
        return Err(error::ErrorNotFound("invalid image id"));
    }

    data.images
        .image_files
        .id_to_actix_file(id.as_str())
        .and_then(|file| file.into_response(&request))
}

async fn store_image_png(
    data: web::Data<AppData>,
    id: web::Path<String>,
    payload: web::Payload,
) -> DBResponse {
    data.images
        .store_image_png(id.as_str(), payload)
        .await
        .map(into_store_response)
}

async fn delete_image_png(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.images
        .delete_image_png(id.as_str())
        .await
        .map(as_empty_content)
}

async fn list_integral_images(
    data: web::Data<AppData>,
    filter: web::Query<MyFilter>,
) -> DBResponse {
    data.integral_images
        .get_filtered2(filter.0)
        .await
        .map(as_json)
}

async fn create_integral_image(
    data: web::Data<AppData>,
    obj: web::Json<DBIntegralImage>,
) -> DBResponse {
    data.integral_images
        .create(obj.0)
        .await
        .map(into_location_header)
}

async fn store_integral_png(
    data: web::Data<AppData>,
    integral_id: web::Path<String>,
    obj: web::Payload,
) -> DBResponse {
    data.integral_images
        .store_image_png(integral_id.as_str(), obj)
        .await
        .map(into_store_response)
}

async fn get_integral_image_png(
    data: web::Data<AppData>,
    integral_id: web::Path<String>,
    req: web::HttpRequest,
) -> impl Responder {
    data.integral_images
        .image_blob
        .id_to_actix_file(integral_id.as_str())
        .and_then(|f| f.into_response(&req))
}

async fn delete_integral_image_png(
    data: web::Data<AppData>,
    integral_id: web::Path<String>,
) -> impl Responder {
    data.integral_images
        .delete_integral_png(&integral_id)
        .await
        .map(as_empty_content)
}

async fn store_integral_image(
    data: web::Data<AppData>,
    integral_id: web::Path<String>,
    obj: web::Json<DBIntegralImage>,
) -> DBResponse {
    data.integral_images
        .insert_or_update(integral_id.as_str(), obj.0)
        .await
        .map(into_store_response)
}

async fn get_integral_image(
    data: web::Data<AppData>,
    integral_id: web::Path<String>,
) -> DBResponse {
    data.integral_images
        .get(integral_id.as_str())
        .await
        .map(as_json)
}

async fn delete_integral_image(
    data: web::Data<AppData>,
    integral_id: web::Path<String>,
) -> DBResponse {
    data.integral_images
        .delete(integral_id.as_str())
        .await
        .map(as_empty_content)
}

async fn list_labels(data: web::Data<AppData>, filter: web::Query<MyFilter>) -> DBResponse {
    data.labels.get_filtered2(filter.0).await.map(as_json)
}

async fn create_label(data: web::Data<AppData>, label: web::Json<sar_types::Label>) -> DBResponse {
    data.labels
        .create(DBLabel { data: label.0 })
        .await
        .map(into_location_header)
}

async fn store_label(
    data: web::Data<AppData>,
    id: web::Path<String>,
    label: web::Json<sar_types::Label>,
) -> DBResponse {
    data.labels
        .insert_or_update(id.as_str(), DBLabel { data: label.0 })
        .await
        .map(into_store_response)
}

async fn get_label(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.labels.get(id.as_str()).await.map(as_json)
}

async fn delete_label(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.labels.delete(id.as_str()).await.map(as_empty_content)
}

async fn list_flight_paths(data: web::Data<AppData>, filter: web::Query<MyFilter>) -> DBResponse {
    data.flight_paths.get_filtered2(filter.0).await.map(as_json)
}

async fn create_flight_path(data: web::Data<AppData>, obj: web::Json<FlightPath>) -> DBResponse {
    data.flight_paths
        .create(DBFlightPath(obj.0))
        .await
        .map(into_location_header)
}

async fn store_flight_path(
    data: web::Data<AppData>,
    id: web::Path<String>,
    obj: web::Json<FlightPath>,
) -> DBResponse {
    data.flight_paths
        .insert_or_update(id.as_str(), DBFlightPath(obj.0))
        .await
        .map(into_store_response)
}

async fn get_flight_path(data: web::Data<AppData>, filter: web::Query<MyFilter>) -> DBResponse {
    data.flight_paths.get_filtered2(filter.0).await.map(as_json)
}

async fn delete_flight_path(data: web::Data<AppData>, id: web::Path<String>) -> DBResponse {
    data.flight_paths
        .delete(id.as_str())
        .await
        .map(as_empty_content)
}

fn into_store_response(state: ObjState<String>) -> HttpResponse {
    if state.is_created() {
        into_location_header(state.into_inner())
    } else {
        HttpResponse::NoContent()
            .header("Location", state.into_inner())
            .finish()
    }
}

fn into_location_header(reference: String) -> HttpResponse {
    HttpResponse::Created()
        .header("Location", reference)
        .finish()
}

fn as_json<T: Serialize>(data: T) -> HttpResponse {
    HttpResponse::Ok().json(data)
}

fn as_empty_content<T>(_: T) -> HttpResponse {
    HttpResponse::NoContent().finish()
}

// #[cfg(test)]
// pub mod test_server {
//     use crate::{configure_routes, AppData};
//     use actix_web::dev::Server;
//     use actix_web::{middleware, web, HttpServer};
//     use anyhow::{Context, bail};
//     use std::path::Path;
//
//     #[derive(Debug)]
//     #[non_exhaustive]
//     pub enum TestBinding<'a> {
//         Tcp(&'a str),
//         Uds(&'a Path),
//     }
//
//     #[derive(Debug)]
//     pub struct TestServerConfig<'a> {
//         data_path: &'a Path,
//         binding: TestBinding<'a>,
//         threads: Option<u32>,
//     }
//
//     pub struct TestServer {
//         pub server: Server,
//     }
//
//     pub async fn create_test_server(config: &TestServerConfig<'_>) -> anyhow::Result<TestServer> {
//         env_logger::init();
//         let data = AppData::with_root_path(config.data_path);
//         data.init_fs()
//             .context("Failed to initialize data storage")?;
//         data.load_all_data().await?;
//         let data = web::Data::new(data);
//
//         let mut server_builder = HttpServer::new(move || {
//             actix_web::App::new()
//                 .app_data(data.clone())
//                 .wrap(middleware::Logger::default())
//                 .data(web::JsonConfig::default().limit(4096))
//                 .configure(configure_routes)
//         });
//
//         let server_builder = server_builder.workers(config.threads.unwrap_or(1) as usize);
//         let server_builder = match &config.binding {
//             TestBinding::Tcp(b) => server_builder.bind(b).context("Failed to bind")?,
//             TestBinding::Uds(p) => server_builder.bind_uds(p).context("Failed to bind UDS")?,
//             binding => bail!("Note implemented for {:?}", binding),
//         };
//
//         Ok(TestServer {
//             server: server_builder.run(),
//         })
//     }
// }
