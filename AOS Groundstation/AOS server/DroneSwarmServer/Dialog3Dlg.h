#pragma once
#include "afxdialogex.h"
#include "ListCtrlEx.h"
#include <Packet32.h>
#include <vector>
#include <thread>
#include <Iphlpapi.h>

uint8_t rawData[] = {
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x08, 0x06, 0x00, 0x01, 0x08, 0x00, 0x06, 0x04, 0x00, 0x01, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

uint8_t myMAC[] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

#define WM_FROM_DLG3 WM_USER+19

typedef struct {
	LVITEM* plvi;
	CString sCol2;
	CString sCol3;
	CString sCol4;
} lvItem, * plvItem;


// CDialog3Dlg dialog

class CDialog3Dlg : public CDialogEx
{
	DECLARE_DYNAMIC(CDialog3Dlg)

public:
	CDialog3Dlg(CWnd* pParent = nullptr);   // standard constructor
	virtual ~CDialog3Dlg();

	// Dialog Data
	enum { IDD = IDD_DIALOG3 };

protected:
	HICON m_hIcon;
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	virtual BOOL OnInitDialog();

	CListCtrl* m_pDragList;		//Which ListCtrl we are dragging FROM
	CListCtrl* m_pDropList;		//Which ListCtrl we are dropping ON
	CImageList* m_pDragImage;	//For creating and managing the drag-image
	BOOL        m_bDragging;	//T during a drag operation
	int         m_nDragIndex;	//Index of selected item in the List we are dragging FROM
	int         m_nDropIndex;	//Index at which to drop item in the List we are dropping ON
	CWnd* m_pDropWnd;		//Pointer to window we are dropping on (will be cast to CListCtrl* type)

	void DropItemOnList(CListCtrl* pDragList, CListCtrl* pDropList);
	DECLARE_MESSAGE_MAP()
public:
	CListCtrlEx m_ListCtrl1;
	afx_msg void OnBnClickedButton2();
	afx_msg void OnBnClickedButton3();
	afx_msg void OnBegindragList(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnMouseMove(UINT nFlags, CPoint point);
	afx_msg void OnLButtonUp(UINT nFlags, CPoint point);
	afx_msg HCURSOR OnQueryDragIcon();

	BOOL StartThread();
	void StopThread();
	static UINT	WorkThread(LPVOID pParam);
	void ReceiveNetPackets(LPADAPTER dev, LPPACKET pPacket);
	void ParsePackets(LPPACKET lpPacket);
	CWinThread* pThread;
	volatile bool b_ThreadRuns;
	int netIndexMap[500][2]{ 0 };
	int IPsum;
private:
	BOOL InterfaceIdxToInterfaceIp(PMIB_IPADDRTABLE pIpAddrTable, DWORD dwIndex, char str[]);
	BOOL PhysAddrToString(BYTE PhysAddr[], DWORD PhysAddrLen, char str[]);
	DWORD GetNetworkDevices();
	void delayedListCtrlEntry(int index, in_addr addrs);
	//CArray <CLabelItem, CLabelItem> m_arLabels;
	int m_LabelCount;
	CButton m_ButtonCtrl2;
	CButton m_ButtonCtrl3;
	CComboBox m_ComboBox1;
	CProgressCtrl m_Progress1;
};
