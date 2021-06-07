# AOS/SERV: Search And Rescue Database Server
This is a Rust implementation for the database server used with Airborne Optical Sectioning.

### Requirements

Install Rust by running `rustup` from https://rustup.org. Rust stable version
is OK. Minimal Rust version is 1.48

Required Linux packages: libx11-dev cmake build-essentials python-is-python3
On Windows only the Rust package is required

### Compile and Build

Go to the current directory [AOS/SERV](./SERV) and run

```
cargo build --release
```

### Execution

Run the server with

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

Resource IDs are timestamps with a random suffix. The format is
`YYYYMMDDTHHmmssSSS_rrrr`

Referenced files of a resource always have the same id but has an
additional suffix.

`/locations`:
Main locations referencing polygon data, holds vertex data, GEO-TIFF images
and the center and corner coordinates of the location

`/drones`:
Details about a single drone. 

`/images`:
A single image provided by a specific drone

`/integrals`:
An integral image computed with AOS.

`/labels`:
Markers representing the classification results performed on the integral images are bound to a specific location.

## Quick tutorial

#TODO:- Add demo script to upload and download the data demonstrating the usage of server
```py
import asyncio
import aiohttp

async with aiohttp.ClientSession() as session:
  # upload data in a form a dictionary to a json file at upload location in serveraddress
  async with session.request(
            "put", serveraddress + uploadlocation,
            data=json.dumps(data_dictionary),
            headers={"content-type": "application/json"}
    ) as resp:
  
  #download information of all json files present at downloadlocation in serveraddress
  async with session.request(
                "get", serveraddress + downloadlocation
        ) as resp:
            drones = await resp.json()
```

## More detailed usage
For a more detailed example on the performing experiments with the [SERVER](/SERV) look at the serverupload (/serverupload.py) and utils(/utils.py) program in [DRONE](/DRONE).



  