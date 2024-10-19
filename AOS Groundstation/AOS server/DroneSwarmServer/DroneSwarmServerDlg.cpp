
// DroneSwarmServerDlg.cpp : implementation file
//

#include "pch.h"
#include "framework.h"
#include "DroneSwarmServer.h"
#include "DroneSwarmServerDlg.h"
#include "afxdialogex.h"
#include "expandedresources.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

// CAboutDlg dialog used for App About

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// Dialog Data
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_ABOUTBOX };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

// Implementation
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(IDD_ABOUTBOX)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CDroneSwarmServerDlg dialog



CDroneSwarmServerDlg::CDroneSwarmServerDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_DRONESWARMSERVER_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CDroneSwarmServerDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CDroneSwarmServerDlg, CDialogEx)
	ON_WM_ACTIVATEAPP()
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
END_MESSAGE_MAP()

// CDroneSwarmServerDlg message handlers

static DWORD CALLBACK
RCStreamInCallback(DWORD_PTR dwCookie, LPBYTE pbBuff, LONG cb, LONG* pcb)
{
	CFile* pFile = (CFile*)dwCookie;
	*pcb = pFile->Read(pbBuff, cb);
	return 0;
}

BOOL CDroneSwarmServerDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != nullptr)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	// TODO: Add extra initialization here
	CreateMenuAnimation();

	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CDroneSwarmServerDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CDroneSwarmServerDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

// The system calls this function to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CDroneSwarmServerDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

void CDroneSwarmServerDlg::OnActivateApp(BOOL bActive, DWORD hTask)
{
	//CDroneSwarmServerDlg::OnActivateApp(bActive, hTask);
	if (bActive)
	{
		//hasFocus = true;
	}
	else
	{
		//Dialog Losing Focus So Destroy It
		//DestroyWindow();
		//hasFocus = false;
	}
	
}

void CDroneSwarmServerDlg::CreateMenuAnimation()
{
	CWnd* pWnd = GetDlgItem(IDC_CONTROL_PLACE);
	if (pWnd->GetSafeHwnd() != NULL)
	{
		CRect rect;
		pWnd->GetWindowRect(rect);
		ScreenToClient(rect);
		pWnd->DestroyWindow();

		m_wndAnimation.Create(WS_CHILD | WS_VISIBLE | WS_TABSTOP, rect, this, IDC_CONTROL_PLACE);

		CRect rectDummy(0, 0, 1, 1);

		{
			CDialog2Dlg* pWnd = new CDialog2Dlg;
			pWnd->Create(CDialog2Dlg::IDD, &m_wndAnimation);
			theApp.m_pHWnd2 = pWnd->GetSafeHwnd();

			m_wndAnimation.AddControl(pWnd, _T("Create Waypoints with Google Maps"));
		}
		{
			CDialog1Dlg* pWnd = theApp.m_pDlg1 = new CDialog1Dlg;
			pWnd->Create(CDialog1Dlg::IDD, &m_wndAnimation);
			theApp.m_pHWnd1 = pWnd->GetSafeHwnd();

			m_wndAnimation.AddControl(pWnd, _T("Drone connection / Live video stream"));
		}
		{
			CDialog3Dlg* pWnd = new CDialog3Dlg;
			pWnd->Create(CDialog3Dlg::IDD, &m_wndAnimation);
			theApp.m_pHWnd3 = pWnd->GetSafeHwnd();

			m_wndAnimation.AddControl(pWnd, _T("Scan Network for connected Drones"));
		}
		/*
		{
			CMonthCalCtrl* pWnd = new CMonthCalCtrl;
			pWnd->Create(WS_CHILD | WS_TABSTOP | LVS_LIST | LVS_SHOWSELALWAYS, rectDummy, &m_wndAnimation, 3);

			m_wndAnimation.AddControl(pWnd, _T("Month Calendar"));
		}
		*/
		{
			CRichEditCtrl* pWnd = new CRichEditCtrl;
			pWnd->Create(WS_CHILD | WS_TABSTOP | WS_VSCROLL | ES_MULTILINE | ES_WANTRETURN | ES_AUTOVSCROLL, rectDummy, &m_wndAnimation, 4);
			pWnd->SetAutoURLDetect(TRUE);
			HINSTANCE hInstance = AfxFindResourceHandle(MAKEINTRESOURCE(IDR_RTF1), _T("RTF"));
			if (hInstance != NULL)
			{
				HRSRC hResource = ::FindResource(hInstance, MAKEINTRESOURCE(IDR_RTF1), _T("RTF"));
				if (hResource != NULL)
				{
					DWORD nSize = ::SizeofResource(hInstance, hResource);
					HGLOBAL hGlobal = ::LoadResource(hInstance, hResource);
					if (hGlobal != NULL)
					{
						CMemFile mf((LPBYTE)::LockResource(hGlobal), nSize);

						EDITSTREAM es;
						es.dwCookie = (DWORD_PTR)&mf;
						es.pfnCallback = (EDITSTREAMCALLBACK)RCStreamInCallback;
						pWnd->StreamIn(SF_RTF, es);

						::UnlockResource(hGlobal);
					}
					::FreeResource(hResource);
				}
			}

			m_wndAnimation.AddControl(pWnd, _T("Documentation"));
		}
	}
	DWORD type = 0x0011;
	m_wndAnimation.SetAnimationDuration(CUIAnimationWnd::e_AnimationSelect, 0.7);
	m_wndAnimation.SetAnimationType(CUIAnimationWnd::e_AnimationSelect, type);

}
