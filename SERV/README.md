# Search And Rescue Database Server

## Compiling

### Prerequisites

Install Rust by running `rustup` from https://rustup.org. Rust stable version
is OK. Minimal Rust version is 1.48

Required Linux packages: libx11-dev cmake build-essentials python-is-python3
On Windows only the 

### Building

Go to the current directory and run

```
cargo build
```

### Execution

Run the server with

```
cargo run --bin server
```
The performance of the server will be much better when executed
with the release flag

```
cargo run --release --bin server
```

To enable logging set the environment variable `RUST_LOG`. e.g.
```
export RUST_LOG=info
cargo run --bin sar-server
```


## Server API

The server API follows the REST principle. 

For all resources the data types are defined in `sar-types/src/lib.rs`

Exact serialization format is best visible by checking the contents
of the `serverData` directory after executing `client_scripts/setup_demo_data.py`


Resource IDs are timestamps with a random suffix. The format is
`YYYYMMDDTHHmmssSSS_rrrr`

Referenced files of a resource always have the same id but has an
additional suffix.

`/locations`:
Main locations referencing polygon data, holds vertex data, GEO-TIFF images
and the center and corner coordinates of the location

`/drones`:
Details about a single drone. Mostly camera properties but may 
hold additional properties in the future

`/images`:
A single image provided by one specific drone

`/integrals`:
an integral image.

The integral image has an optional reference to a drone, but it is
best practice to actually make the drone reference explicit as it
does define the properties of the camera so that the image can be
correctly projected onto the terrain. When no reference is defined
then some hard-coded default values for the camera projection are used.

`/labels`:
Markers bound to a specific location.

The location_id in the label is required.

`/flight_paths`
Planned, or already performed flight paths.



  
