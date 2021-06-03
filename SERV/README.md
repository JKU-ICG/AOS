# Search And Rescue Viewer

## Todos / Things encountered while testing

### Client
* [ ] WONTFIX - Bug: when zooming out to far (with mouse) I cannot zoom back. - probably won't fix. Happens when terrain disappears behind the far plane. Current complexity with strange coordinate system makes detecting this hard.
* [ ] UI: How to enable the orthographic projection? - with the `p`key. But changing back does not work as I struggle finding a proper algorithm to calculate the parameters for perspective projection. The only thing I could do right now is reset to initial view.

### Server
* [x] ToDo: compiling the server on the raspberry Pi. Remove the compilation of the `sar-viewer` (uses Vulkan libs an will not compile on the Pi) and only build the `sar-server`: No cargo provides the options to build server only with the option `--bin sar-server`

## Compiling

### Prerequisites

Install Rust by running `rustup` from https://rustup.org. Rust stable version
is OK. Minimal Rust version is 1.48


Required Linux packages: libx11-dev cmake build-essentials python-is-python3
On Windows only the 

I am actually not sure if build-essentials are required, but never worked on
a system where it does not exist. A C compiler and linker is definitely needed.

The shader compilation script uses python. It works with Python 2 and Python3,
on modern systems, aliasing those two is probably best.

The vulkansdk is only needed for compiling glsl to SPIR-V, validation layers
are optional for running the sar-viewer.

I installed the vulkansdk directly from LunarG / Khronos - extracted to
/opt/vulkansdk/current and did add /opt/vulkansdk/current/x86-64/bin to the
PATH.

Also set the environment variable `SHADERC` to `glslc`

### Building

Go to the root directory of this project and run

```
cargo build
```

For executing the unit tests (test coverage is relatively low):

```
cargo test
```

### Execution

Run the server with

```
cargo run --bin sar-server
```

Run the client with

```
cargo run --bin sar-viewer
```

The performance of the client will be much better when executed
with the release flag

```
cargo run --release --bin sar-viewer
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


## Python scripts

All python scripts that interact with the sever are located in the
`client_scripts` directory.

### setup_demo_data.py

Clears all data stored on the server and uploads all demo data.

### clear_server.py

Clears all data stored on the server

### filter_images.py

Allows uploading images and shows all possibilities to filter resources.

All resources have the exact same filtering capabilities and same
API structure. The filter_images script can serve as template for
handling all other resources.

### dem_script.py

Just some example script for coordinate conversion



## Developer log

Original idea for the SARViewer was to implement it as an Android application,
but I had many problems with getting 3d rendering work consistently on
emulator and on my phone. For UI development the emulation environment
was required as the screen of my phone is way too small for such an
application.

Also, UI layout was very unstable.

Later moved to C++ with OpenGL ES. This was only a short excursion as
I started seg-faulting the application when it was just a bit over
a thousand lines long and I had just rendered a few primitives and
a dummy UI using "Dear ImGUI". My C++ knowledge is not good enough
for a larger application.

The original C++ code never compiled and executed successfully on my
machine (Linux, AMD Zen2 and Navi10 GPU, or Vega21), so it was not
usable as template.

I decided to definitely use Rust as main development language
(see "Why Rust") and tried to find the best suited rendering and
UI library to use.

The first focus was to find any UI library that is

- compatible licence, in general only BSD, MIT or Mozilla Public Licence
  and similar are compatible with the project.
  No GPL, lGPL only with restriction of late binding, no unlicenced code
- portable (should support Linux, Windows, MacOS and Android, if possible)
- allows easy integration of any kind of hardware-accelerated 3d rendering
  - this one was astoundingly hard
  - I want to avoid rendering to a texture, copy it into main memory
    and update an "image widget" for every frame
- Good Rust API (no direct FFI with GTK or QT)
- Flexible
  - need to render UI elements on top of the 3d scene
  - want to be able to hide UI
- looks good
  - can scale
  - styling support
- somewhat stable API
- Touch support and scalable interface

The starting point for all this was the page https://www.areweguiyet.com/

### The following UI libraries were investigated:

#### ICED

The first Rust UI library I actively tried out.

Cloned their repo and started a short throw-away project for prototyping.
The basic architecture idea is really good and overall design looks very promising,
but the library is still too young and the API is neither stable nor polished
enough for using it in the project.

End of November 2020 a new version came out (0.2.0) and broke my demo entirely.
That made the decision easy to not use it for now.

Whenever ICED reaches a somewhat stable state, it may become the de-facto
standard for UIs for Rust.

It was my first introduction to WebGPU though.

#### KAS

The second Rust UI library was KAS.

Similar design philosophy as ICED but seemd a bit further in development.
It also supports completely custom widgets that can be rendered using `wgpu-rs`.

Unfortunately the API is strangely restrictive. It allows only one single
custom render pass (meaning, wgpu render pass) per application. Also all
render pipelines have to be defined statically during bootstrap.

Tried to work around that for over 20 hours, but did not a good strategy
to build the application on that. Where the 3d scene is the main focus and
all other UI is for support.


#### imgui-rust

Rather late, I discovered that there is a well-developed Rust binding
for "Dear ImGUI" that has a safe API and has integration with most rendering
APIs. So it would not influence the decision what rendering API should be used.

The imgui API is much more stable than the other APIs as the basic library
is stable and it ticks of all the other requirements as well.

Later, I found an actual tutorial with example code, how to integrate
it into a wgpu-rs based application and it compiled and worked after minutes,
even before I understood how to use wgpu at all.

It supports multiple "windows" that can be freely placed into the scene
and can also be moved around by the user.

Therefore `imgui-rs` is the UI library that will be used for the project.

### Rendering API

The original idea was to use OpenGL ES (or webgl) as it seemed to be the
most portable API around. Then I found out that Apple deprecated OpenGL
entirely and does not support OpenGL ES 2.0 at all. Only with compatibilty
layers that translate OpenGL calls to Metal.

Also, OpenGL is a rendering API that did not age well at all. It is the only
one I ever used effectively:
CG lab project and a 3d data visualization project that I never finished.

Rust also has a really good API for rendering with Vulkan: `vulkano`.
Vulkan with C++ is very hard to use. Everything has to be done manually
and the API consists of setting hundreds of values one-by-one. Forgetting
anything gives you a crashing application. Vulkano on Rust is much better,
for sensible defaults, there are macros that simplify generation of render
pipelines, uniform bindings and everything. Also all Vulkan types are mapped
to nice Rust structs that are easy to initialize, the IDE can give you
the template and the developer has to fill the blanks.

The really good Rust binding also solves all manual memory management problems.
Buffers have to be created manually, but they get freed automatically whenever
the handle gets out of scope. No need for any explicit destructors.

In my opinion, `vulkano` is actually easier to understand than OpenGL.

But there is a new player in the game: WebGPU and the first implementation
`wgpu-rs`. It is a completely new API that is currently in development and
should become a W3C standard. All larger industry players 
(for Web and Browser development) are involved: Google, Apple, Mozilla.

One of the major implementations of the drafts is wgpu-rs. The API is still
new and not stable. But it is good enough that most Rust UI libraries provide
a backend for wgpu already. Some wgpu-rs Rust examples can be compiled to
WASM and run on nightly Chrome. Simpler examples work on nightly Firefox
as well.

The design of WebGPU is similar to Vulkan, DX12 and Metal - therefore the
developer has direct control over the rendering pipeline by defining
everything explicitly and also rendering is performed by building command
buffers that are sent to the driver.

Right now the only supported shading language is SPIR-V (can be generated
from GLSL and HLSL). The WebGPU specific shading language is not fully defined
yet, so it cannot be used at all right now.

WebGPU only supports Vertex-, Fragment- and Compute-shaders.

WebGPU is definitely good enough for building applications. I consider
it slightly harder to use than `vulkano` as the library is relatively new
and the error handling is lacking. Errors on developer side cause crashes
that are hard to analyze without using a debugger. Errors in the shader
always crash hard.

## Application design

Not much, yet.

I try to not build a huge framework for this. It is hard to not do so as
I am a framework developer by trade. Rust is a relatively new language for
me, so over-engineering is a bad idea.

A few things are already semi-decided by me:

### Coordinate system

The world coordinates are in meters (as loaded from the map).

Camera location and all other models are directly constructed in world
coordinates. There won't be too many 3d objects in the scene that
need a render tree with managed model-matrix for that.


### Camera

There is one `camera` module that holds all current screen dimensions
and provides uniform buffers for the vertex shaders.

The camera also supports basic ray casting for mouse interaction and
provides some utilities for pixel-accurate drawing.

### drawing

I think, some utility to draw basic shapes onto the rendered terrain
would be nice. E.g. for showing drone flight paths, a legend, coordinate grids,
and highlight points.

The alternative would be, to draw those things onto a texture and project it
onto the map, but that gives somewhat ugly results and some things
are actually more correct when they hover over the terrain - e.g. drone paths.

The highlights for potential persons in the drone image will likely stay in the
texture though.

I started with creating a utility to draw primitives onto a 3D plane (lines,
points, poly-lines). The goal, is that all drawn lines have constant thickness
independent of viewing angle (similar to billboards).



  
