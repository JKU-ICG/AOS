#pragma once
#include "DroneSwarmServer.h"
#include "afxwin.h"
#include "afxcmn.h"
extern "C"
{
#include "libavformat/avformat.h"
#include "libavformat/rtsp.h"
#include "libavcodec/avcodec.h"
#include "libavutil/avutil.h"
#include "libswscale/swscale.h"
#include "libavutil/imgutils.h"
#include "MQTTClient.h"
}

#define WM_THREAD_END      WM_USER+10
#define WM_THREAD_TEXT     WM_USER+11
#define WM_THREAD_DATA     WM_USER+12
#define WM_THREAD_RENDER   WM_USER+13
#define WM_THREAD_TO_PYWRAPPER WM_USER+14
#define WM_THREAD_FROM_PYWRAPPER WM_USER+15
#define WM_PYWRAPPER_WAYPOINTS WM_USER+16
#define WM_FROM_PYWRAPPER WM_USER+17
#define WM_PYWRAPPER_IMAGEANDTELEMETRYDATA WM_USER+18
#define WM_FROM_DLG3 WM_USER+19
#define WM_PYWRAPPER_ENCODEDIMAGEDATA WM_USER+20
#define WM_PYWRAPPER_ISHWDECODERENABLED WM_USER+21
#define WM_THREAD_STOP     100
#define IDT_TIMER  WM_USER + 200 

#define QoS0 0
#define QoS1 1
#define QoS2 2

// Stuff for Console 
static const WORD MAX_CONSOLE_LINES = 1500;
typedef BOOL(WINAPI* SetConsoleIconFunc)(HICON);
typedef volatile uint8_t* v_uint8_t;
SetConsoleIconFunc p_SetConsoleIcon;
FILE* stream[3];

int log_sel[] = { AV_LOG_QUIET, AV_LOG_PANIC, AV_LOG_FATAL, AV_LOG_ERROR, AV_LOG_WARNING, AV_LOG_INFO, AV_LOG_VERBOSE, AV_LOG_DEBUG, AV_LOG_TRACE };
int QoSsel[] = { QoS0 , QoS1 , QoS2 };

class CDialog1Dlg : public CDialogEx
{
	DECLARE_DYNAMIC(CDialog1Dlg)

public:
	CDialog1Dlg(CWnd* pParent = NULL);   // standard constructor
	virtual ~CDialog1Dlg();

	// Dialog Data
	enum { IDD = IDD_DIALOG1 };

protected:
	HICON m_hIcon;
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	virtual BOOL OnInitDialog();

	DECLARE_MESSAGE_MAP()
	afx_msg LRESULT EndUp(WPARAM mBytes, LPARAM zero);
	afx_msg LRESULT HandleThreadMsg(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT HandleTelemetryData(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT Renderer(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT SendWayPoint2Drone(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT GetImageAndTelemetryData(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT GetEncodedImageData(WPARAM wparam, LPARAM lParam);
	afx_msg LRESULT IsHWDecoderEnabled(WPARAM wParam, LPARAM lParam);
	afx_msg LRESULT SetIPArray(WPARAM wParam, LPARAM lParam);
	afx_msg void OnBnClickedButton1();
	afx_msg void OnBnClickedCheck1();
	afx_msg void OnCbnSelchangeCombo1();
	afx_msg void OnTRBNThumbPosChangingSlider1(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnDeltaposSpin2(NMHDR* pNMHDR, LRESULT* pResult);

public:
	int AVThread(int droneNumber);
	BOOL StartThread();
	void StopThread();
	static UINT	WorkThread(LPVOID pParam);
	CWinThread* pThread[10];
	CWinThread* pMqttThread;
	int isConnected[10];
	volatile bool b_ThreadRuns[10] = { false };
	volatile bool b_MqttThreadRuns = false;
	BITMAPFILEHEADER bmpheader;
	BITMAPINFO bmpinfo;
	void ShowFrameBMP(AVFrame* pFrame, int width, int height, int interlaced);
	void RedirectIOToConsole();
	int SendWayPoint2Drone2(int drone);
	int GetEncodedImageData2(int drone);
	static int MQTTmsgarrv(void* context, char* topicName, int topicLen, MQTTClient_message* message);
	static void MQTTmsgdeliv(void* context, MQTTClient_deliveryToken dt);
	static void MQTTconnlost(void* context, char* cause);
	AVFormatContext* pFormatCtx = nullptr;
	CString telemetryData[10];
	CString threadmsg[10];
	CString mainDlgmsg;
	CString IPperDrone[10];
	CString PortperDrone[10];
	int MQTTDrone_Number;
	int droneNum;
	int dNum;
	long interval;
	UINT Timeval;
	CSpinButtonCtrl m_Spin1;

private:
	CButton m_ButtonCtrl1;
	double getSystemScaleFactor();
	HANDLE fonthandle;
	CFont* font;
	CComboBox m_ComboBox1;
	CComboBox m_ComboBox2;
	CComboBox m_ComboBox3;
	CButton m_CheckBox1;
	CSliderCtrl m_Slider1;
	CIPAddressCtrl m_ipctrl;
	CEdit m_EditCtrl1;
	CEdit m_EditCtrl2;
	CEdit m_EditCtrl3;
	CEdit m_EditCtrl4;
	CEdit m_EditCtrl5;
	CEdit m_EditCtrl6;
	CEdit m_EditCtrl7;
	CEdit m_EditCtrl8;
	CEdit m_EditCtrl9;
	CEdit m_EditCtrl10;
	CEdit m_EditCtrl11;
	CEdit m_EditCtrl12;
	CEdit m_EditCtrl13;
	CEdit m_EditCtrl14;
	CEdit m_EditCtrl15;
	CEdit m_EditCtrl16;
	CStatic m_Static6;

};
