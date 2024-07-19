
// DroneSwarmServer.h : main header file for the PROJECT_NAME application
//

#pragma once

#ifndef __AFXWIN_H__
	#error "include 'pch.h' before including this file for PCH"
#endif

#include "resource.h"		// main symbols
#include "Dialog1Dlg.h"

// CDroneSwarmServerApp:
// See DroneSwarmServer.cpp for the implementation of this class
//

class CDroneSwarmServerApp : public CWinAppEx
{
public:
	CDroneSwarmServerApp();
	HWND m_pHWnd1;
	HWND m_pHWnd2;
	HWND m_pHWnd3;
	CDialog1Dlg* m_pDlg1;
// Overrides
public:
	virtual BOOL InitInstance();

// Implementation

	DECLARE_MESSAGE_MAP()
};

extern CDroneSwarmServerApp theApp;
