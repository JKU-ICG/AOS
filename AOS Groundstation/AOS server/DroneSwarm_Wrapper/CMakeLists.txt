project(DroneSwarmWrapper)
cmake_minimum_required(VERSION 3.10)

add_subdirectory(thirdparty/pybind11)
add_definitions(-D_AFXDLL)
set(CMAKE_MFC_FLAG 2)

pybind11_add_module(ds_wrapper DroneSwarm_Wrapper.cpp pch.cpp)
