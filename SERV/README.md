# AOS/SERV: Search And Rescue Database Server
This is a Rust implementation for the database server used with Airborne Optical Sectioning.

### Requirements

Install Rust by running `rustup` from https://rustup.org. Rust stable version 1.48 has been tested.

Required Linux packages: libx11-dev cmake build-essentials python-is-python3.
On Windows only the Rust package and python3 is required

### Compilation

Open a command window or terminal and proceed to the current directory [AOS/SERV](./SERV) and run

```
cargo build --release
```

### Execution

Open a command window or terminal and proceed to the current directory [AOS/SERV](./SERV) and start the server with

```
cargo run --release --bin server
```

To enable logging set the environment variable `RUST_LOG`. e.g.
```
export RUST_LOG=info
cargo run --bin sar-server
```

## Server API

The server API follows the Representational state transfer (REST) principle. 

Uploaded resources are stored with there ids timestamped along with a randomsuffix. The format is
`YYYYMMDDTHHmmssSSS_rrrr`

Referenced files of a resource always have the same id but has an additional suffix.

Server stores AOS flight information in various folders:-

`/locations`:
Contains AOS flight location information (center and corner coordinates of the location) as a json file.
Other files such as polygon data, vertex data, GEO-TIFF images required for visualization and AOS are also stored with same location id.

`/drones`:
Details about the flying drone is stored as json. 

`/images`:
Single images captured during AOS flights are stored. Pose information of individual images are stored as json.

`/integrals`:
Integral images computed with AOS are stored here. Pose information of integral images and ids of individual images used for integration are stored as json.

`/labels`:
Labels representing the classification results performed on the integral images. GPS location of labels along with classification confidence are stored within the json file.

## Quick tutorial

```py
import asyncio
import aiohttp

async with aiohttp.ClientSession() as session:
  # upload data in a form a dictionary to a json file at upload location (for e.g. '\drones') in serveraddress
  async with session.request(
            "put", serveraddress + uploadlocation,
            data=json.dumps(data_dictionary),
            headers={"content-type": "application/json"}
    ) as resp:
  
  #download information of all json files present at downloadlocation (for e.g. '\drones') in serveraddress
  async with session.request(
                "get", serveraddress + downloadlocation
        ) as resp:
            info = await resp.json()
```

## More detailed usage
For a more detailed example on the performing experiments with the [SERVER](/SERV) look at the [serverupload](../DRONE/ServerUpload.py) and [utils](../DRONE/utils.py) program in [DRONE](/DRONE).



  
