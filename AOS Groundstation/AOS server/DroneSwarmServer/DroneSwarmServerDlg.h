
// DroneSwarmServerDlg.h : header file
//

#include "UIAnimationWnd.h"
#include "Dialog1Dlg.h"
#include "Dialog2Dlg.h"
#include "Dialog3Dlg.h"

#pragma once


// CDroneSwarmServerDlg dialog
class CDroneSwarmServerDlg : public CDialogEx
{
// Construction
public:
	CDroneSwarmServerDlg(CWnd* pParent = nullptr);	// standard constructor

// Dialog Data
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_DRONESWARMSERVER_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support


// Implementation
protected:

	HICON m_hIcon;
	// Generated message map functions
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnActivateApp(BOOL bActive, DWORD hTask);
	DECLARE_MESSAGE_MAP()
private:
	void CreateMenuAnimation();
	CUIAnimationWnd m_wndAnimation;
};
