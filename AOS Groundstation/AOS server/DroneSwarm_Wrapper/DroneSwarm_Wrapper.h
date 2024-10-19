// DroneSwarm_Wrapper.h : main header file for the DroneSwarm_Wrapper DLL
//

#pragma once

#ifndef __AFXWIN_H__
	#error "include 'pch.h' before including this file for PCH"
#endif

#include "pch.h"
#include "Resource.h"		// main symbols
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/buffer_info.h>

#define WM_THREAD_TO_PYWRAPPER WM_USER+14
#define WM_THREAD_FROM_PYWRAPPER WM_USER+15
#define WM_PYWRAPPER_WAYPOINTS WM_USER+16
#define WM_FROM_PYWRAPPER WM_USER+17
#define WM_PYWRAPPER_IMAGEANDTELEMETRYDATA WM_USER+18
#define WM_PYWRAPPER_ENCODEDIMAGEDATA WM_USER+20
#define WM_PYWRAPPER_ISHWDECODERENABLED WM_USER+21


// CDroneSwarmWrapperApp
// See DroneSwarm_Wrapper.cpp for the implementation of this class
//

class CDroneSwarmWrapperApp : public CWinApp
{
public:
	CDroneSwarmWrapperApp();

// Overrides
public:
	virtual BOOL InitInstance();
	DECLARE_MESSAGE_MAP()
private:
	HWND Dialog;
protected:
	
};
