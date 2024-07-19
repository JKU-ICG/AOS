// DroneSwarm_Wrapper.cpp : Defines the initialization routines for the DLL.
//
#include "pch.h"
#include "framework.h"
#include "DroneSwarm_Wrapper.h"

#include <windows.h> 
#include <memory.h>

#define SHMEMSIZE 130000000
#define SHMEMSLOTSIZE 12500000

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

namespace py = pybind11;


//
//TODO: If this DLL is dynamically linked against the MFC DLLs,
//		any functions exported from this DLL which call into
//		MFC must have the AFX_MANAGE_STATE macro added at the
//		very beginning of the function.
//
//		For example:
//
//		extern "C" BOOL PASCAL EXPORT ExportedFunction()
//		{
//			AFX_MANAGE_STATE(AfxGetStaticModuleState());
//			// normal function body here
//		}
//
//		It is very important that this macro appear in each
//		function, prior to any calls into MFC.  This means that
//		it must appear as the first statement within the
//		function, even before any object variable declarations
//		as their constructors may generate calls into the MFC
//		DLL.
//
//		Please see MFC Technical Notes 33 and 58 for additional
//		details.
//

// CDroneSwarmWrapperApp

BEGIN_MESSAGE_MAP(CDroneSwarmWrapperApp, CWinApp)
END_MESSAGE_MAP()


static HWND dlg = nullptr;

// CDroneSwarmWrapperApp construction

CDroneSwarmWrapperApp::CDroneSwarmWrapperApp()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance

}

static LPVOID lpvMem = NULL;      // pointer to shared memory
static HANDLE hMapObject = NULL;  // handle to file mapping
// The DLL entry-point function sets up shared memory using a 
// named file-mapping object. 

BOOL WINAPI DllMain(HINSTANCE hinstDLL,  // DLL module handle
    DWORD fdwReason,              // reason called 
    LPVOID lpvReserved)           // reserved 
{
    BOOL fInit, fIgnore;

    switch (fdwReason)
    {
            // DLL load due to process initialization or LoadLibrary
        case DLL_PROCESS_ATTACH:
            // Create a named file mapping object

            hMapObject = CreateFileMapping(
                INVALID_HANDLE_VALUE,   // use paging file
                NULL,                   // default security attributes
                PAGE_READWRITE,         // read/write access
                0,                      // size: high 32-bits
                SHMEMSIZE,              // size: low 32-bits
                TEXT("dllmemfilemap")); // name of map object
            if (hMapObject == NULL)
                return FALSE;

            // The first process to attach initializes memory

            fInit = (GetLastError() != ERROR_ALREADY_EXISTS);

            // Get a pointer to the file-mapped shared memory

            lpvMem = MapViewOfFile(
                hMapObject,     // object to map view of
                FILE_MAP_WRITE, // read/write access
                0,              // high offset:  map from
                0,              // low offset:   beginning
                0);             // default: map entire file
            if (lpvMem == NULL)
                return FALSE;

            // Initialize memory if this is the first process

            if (fInit)
                memset(lpvMem, '\0', SHMEMSIZE);

            break;

            // The attached process creates a new thread

        case DLL_THREAD_ATTACH:
            break;

            // The thread of the attached process terminates

        case DLL_THREAD_DETACH:
            break;

            // DLL unload due to process termination or FreeLibrary

        case DLL_PROCESS_DETACH:

            // Unmap shared memory from the process's address space

            fIgnore = UnmapViewOfFile(lpvMem);

            // Close the process's handle to the file-mapping object

            fIgnore = CloseHandle(hMapObject);

            break;

        default:
            break;
    }

    return TRUE;
    UNREFERENCED_PARAMETER(hinstDLL);
    UNREFERENCED_PARAMETER(lpvReserved);
}

// The one and only CDroneSwarmWrapperApp object

CDroneSwarmWrapperApp theApp;

// CDroneSwarmWrapperApp initialization

BOOL CDroneSwarmWrapperApp::InitInstance()
{
    CWinApp::InitInstance();

    return TRUE;
}

__declspec(dllexport) void InitWrapper(HWND dialog)
{
    uint64_t intp = reinterpret_cast<uint64_t>(dialog);
    memcpy(lpvMem, &intp, sizeof(uint64_t));
}

__declspec(dllexport) void* data2Server(int DroneNumber)
{
    int offset = (DroneNumber - 1) * SHMEMSLOTSIZE;
    return (uint8_t*)lpvMem + offset;
}

int isHWDecoderEnabled()
{
#define MEMOFFSET 3999000
    bool status = true;
    uint64_t temp;
    int len = 1;

    memcpy(&temp, lpvMem, sizeof(uint64_t));
    const uint64_t intp = temp;

    ((uint8_t*)lpvMem + 1 + MEMOFFSET)[0] = status;

    PostMessage((HWND)intp, WM_PYWRAPPER_ISHWDECODERENABLED, (WPARAM)nullptr, (LPARAM)nullptr);

    while (status)
    {
        uint8_t * st = (uint8_t*)lpvMem + 1 + MEMOFFSET;
        if (!st[0])
            break;
        Sleep(1);
    }
    return (int)((uint8_t*)lpvMem + MEMOFFSET)[0];
}

int sendWayPointData(const char* data, int DroneNumber)
{
    int ret;
    MSG msg = { 0 };
    int offset = (DroneNumber - 1) * SHMEMSLOTSIZE;
    uint64_t len = CString(data).GetLength();

    if (len <= 0)
        return 0;

    // first 8 bytes = memory address of dialog, next 8 bytes = len of waypoint data, 
    // byte 17 is status byte, at byte 18 Waypoint data starts 

    uint64_t temp;
    memcpy(&temp, lpvMem, sizeof(uint64_t));
    const uint64_t intp = temp;
    
    memcpy((uint8_t*)lpvMem + 9 + offset, &len, sizeof(uint64_t));
    bool status = true;
    
    ((uint8_t*)lpvMem + 17 + offset)[0] = status;
    memcpy((uint8_t*)lpvMem + 18 + offset, data, len);
    ret = PostMessage((HWND)intp, WM_PYWRAPPER_WAYPOINTS, (WPARAM)nullptr, (LPARAM)DroneNumber);

    while (status)
    {
        uint8_t* st = (uint8_t*)lpvMem + 17 + offset;
        if (!st[0])
            break;
        Sleep(5);
    }
    return ret;
}

py::array getImageAndTelemetryData(int DroneNumber)
{
    bool status = true;
    uint64_t temp;
    int offset = (DroneNumber - 1) * SHMEMSLOTSIZE;

    memcpy(&temp, lpvMem, sizeof(uint64_t));
    const uint64_t intp = temp;

    ((uint8_t*)lpvMem + 1033 + offset)[0] = status;

    PostMessage((HWND)intp, WM_PYWRAPPER_IMAGEANDTELEMETRYDATA, (WPARAM)nullptr, (LPARAM)DroneNumber);

    while (status)
    {
        uint8_t* st = (uint8_t*)lpvMem + 1033 + offset;
        if (!st[0])
            break;
        Sleep(5);
    }

    memcpy(&temp, (uint8_t*)lpvMem + 1025 + offset, sizeof(uint64_t));
    const uint64_t len1 = temp;

    memcpy(&temp, (uint8_t*)lpvMem + 1034 + len1 + offset, sizeof(uint64_t));
    const uint64_t len2 = temp;

    return py::array(py::buffer_info(
        (uint8_t*)lpvMem + 1034 + offset,
        sizeof(uint8_t),
        py::format_descriptor<uint8_t>::format(),
        len1 + len2 + 8, false));
}

PYBIND11_MODULE(ds_wrapper, m)
{
    m.doc() = "pybind11 DroneSwarmServer wrapper module";
    m.def("isHWDecoderEnabled", isHWDecoderEnabled, "This function asks if we are HW or SW decoding a drone video stream");
    m.def("sendWayPointData", sendWayPointData, "This function sends Waypoints to a drone");
    m.def("getImageAndTelemetryData", getImageAndTelemetryData, "This functions gets the Camera Image and Telemetry data from the drone");
}
