// Dialog1Dlg.cpp : implementation file
//

#include "pch.h"

#include <io.h>
#include <ios>
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <thread>
#include <utility>
#include <mutex>

#include "DroneSwarmServer.h"
#include "Dialog1Dlg.h"
// CDialog1Dlg dialog

IMPLEMENT_DYNAMIC(CDialog1Dlg, CDialogEx)

using namespace std;

auto flag = std::make_unique<std::once_flag>();

CDialog1Dlg::CDialog1Dlg(CWnd* pParent /*=NULL*/)
	: CDialogEx(CDialog1Dlg::IDD, pParent)
{
#ifndef _WIN32_WCE
	EnableActiveAccessibility();
#endif
	droneNum = 1;
	interval = 1;
	memset(&isConnected, 0, sizeof(isConnected));
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

CDialog1Dlg::~CDialog1Dlg()
{
	FreeConsole();
	delete font;
}

void CDialog1Dlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);

	DDX_Control(pDX, IDC_COMBO1, m_ComboBox1);
	DDX_Control(pDX, IDC_COMBO2, m_ComboBox2);
	DDX_Control(pDX, IDC_COMBO3, m_ComboBox3);
	DDX_Control(pDX, IDC_CHECK1, m_CheckBox1);
	DDX_Control(pDX, IDC_SLIDER1, m_Slider1);
	DDX_Control(pDX, IDC_IPADDRESS1, m_ipctrl);
	DDX_Control(pDX, IDC_BUTTON1, m_ButtonCtrl1);
	DDX_Control(pDX, IDC_EDIT1, m_EditCtrl1);
	DDX_Control(pDX, IDC_EDIT2, m_EditCtrl2);
	DDX_Control(pDX, IDC_EDIT3, m_EditCtrl3);
	DDX_Control(pDX, IDC_EDIT4, m_EditCtrl4);
	DDX_Control(pDX, IDC_EDIT5, m_EditCtrl5);
	DDX_Control(pDX, IDC_EDIT6, m_EditCtrl6);
	DDX_Control(pDX, IDC_EDIT7, m_EditCtrl7);
	DDX_Control(pDX, IDC_EDIT8, m_EditCtrl8);
	DDX_Control(pDX, IDC_EDIT9, m_EditCtrl9);
	DDX_Control(pDX, IDC_EDIT10, m_EditCtrl10);
	DDX_Control(pDX, IDC_EDIT11, m_EditCtrl11);
	DDX_Control(pDX, IDC_EDIT12, m_EditCtrl12);
	DDX_Control(pDX, IDC_EDIT13, m_EditCtrl13);
	DDX_Control(pDX, IDC_EDIT14, m_EditCtrl14);
	DDX_Control(pDX, IDC_EDIT15, m_EditCtrl15);
	DDX_Control(pDX, IDC_EDIT16, m_EditCtrl16);
	DDX_Control(pDX, IDC_STATIC6, m_Static6);
	DDX_Control(pDX, IDC_SPIN2, m_Spin1);
}


BEGIN_MESSAGE_MAP(CDialog1Dlg, CDialogEx)
	ON_WM_CLOSE()
	ON_WM_TIMER()
	ON_MESSAGE(WM_THREAD_END, &CDialog1Dlg::EndUp)
	ON_MESSAGE(WM_THREAD_TEXT, &CDialog1Dlg::HandleThreadMsg)
	ON_MESSAGE(WM_THREAD_DATA, &CDialog1Dlg::HandleTelemetryData)
	ON_MESSAGE(WM_THREAD_RENDER, &CDialog1Dlg::Renderer)
	ON_MESSAGE(WM_PYWRAPPER_WAYPOINTS, &CDialog1Dlg::SendWayPoint2Drone)
	ON_MESSAGE(WM_PYWRAPPER_IMAGEANDTELEMETRYDATA, &CDialog1Dlg::GetImageAndTelemetryData)
	ON_MESSAGE(WM_PYWRAPPER_ENCODEDIMAGEDATA, &CDialog1Dlg::GetEncodedImageData)
	ON_MESSAGE(WM_PYWRAPPER_ISHWDECODERENABLED, &CDialog1Dlg::IsHWDecoderEnabled)
	ON_MESSAGE(WM_FROM_DLG3, &CDialog1Dlg::SetIPArray)
	ON_BN_CLICKED(IDC_BUTTON1, &CDialog1Dlg::OnBnClickedButton1)
	ON_BN_CLICKED(IDC_CHECK1, &CDialog1Dlg::OnBnClickedCheck1)
	ON_CBN_SELCHANGE(IDC_COMBO1, &CDialog1Dlg::OnCbnSelchangeCombo1)
	ON_NOTIFY(TRBN_THUMBPOSCHANGING, IDC_SLIDER1, &CDialog1Dlg::OnTRBNThumbPosChangingSlider1)
	ON_NOTIFY(UDN_DELTAPOS, IDC_SPIN2, &CDialog1Dlg::OnDeltaposSpin2)
END_MESSAGE_MAP()

void InitWrapper(HWND dialog);
void* data2Server(int DroneNumber);


void custom_log(void* ptr, int level, const char* fmt, va_list vl) {

	//To TXT file
	FILE* fp = fopen("av_log.txt", "a+");
	if (fp) {
		vfprintf(fp, fmt, vl);
		fflush(fp);
		fclose(fp);
	}
}

BOOL CDialog1Dlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	HINSTANCE hLib = NULL;

	hLib = LoadLibrary("KERNEL32.DLL");

	if (hLib == NULL) {
		return FALSE;
	}

	p_SetConsoleIcon = (SetConsoleIconFunc)GetProcAddress(hLib, "SetConsoleIcon");

	m_EditCtrl2.SetWindowTextA("8554");
	m_ComboBox1.SetCurSel(5);
	m_ComboBox2.SetCurSel(0);
	m_ComboBox3.SetCurSel(0);

	m_Slider1.SetRange(200, 255);

	// Load Font from Resource
	HINSTANCE hResInstance = AfxGetResourceHandle();
	HRSRC hRes = FindResource(hResInstance, MAKEINTRESOURCE(IDR_FONT1), _T("BINARY"));
	DWORD dwSize = SizeofResource(NULL, hRes);
	HGLOBAL MemoryHandle = LoadResource(NULL, hRes);
	void* data = LockResource(MemoryHandle);

	DWORD nFonts;
	fonthandle = AddFontMemResourceEx(data, dwSize, NULL, &nFonts);

	font = new CFont;
	VERIFY(font->CreateFont(13, 0, 0, 0, FW_NORMAL, 0, 0, 0, ANSI_CHARSET, OUT_CHARACTER_PRECIS, CLIP_CHARACTER_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_MODERN, _T("Consolas")));
	font->FromHandle((HFONT)fonthandle);

	UnlockResource(MemoryHandle);

	m_EditCtrl1.SetFont(font, TRUE);
	m_EditCtrl1.LimitText(0);

	InitWrapper(this->m_hWnd);
	
	return TRUE;
}

double CDialog1Dlg::getSystemScaleFactor()				// returns 1.0 for no scaling
{
	// some simple caching to speed things up

	static int		calculatedScale = FALSE;
	static double	scale = 0;

	if (calculatedScale)
		return scale;

	// get DPI for the system

	HDC		hdc;

	hdc = ::GetDC(NULL);

	UINT	dpiX = 96;		// default DPI

	dpiX = GetDeviceCaps(hdc, LOGPIXELSX);

	scale = static_cast<double>(dpiX / 96.0);
	if (scale < 1.0)
		scale = 1.0;		// prevent funny business with super large monitors returning very low DPI values

	::ReleaseDC(NULL, hdc);

	calculatedScale = TRUE;
	return scale;
}

LRESULT CDialog1Dlg::EndUp(WPARAM mBytes, LPARAM drone)
{
	CString Out;
	Out.Format("Drone: %lld Stop Playing Frames..\r\n", drone);
	m_EditCtrl1.SetSel(m_EditCtrl1.GetWindowTextLength(), m_EditCtrl1.GetWindowTextLength(), FALSE);
	m_EditCtrl1.ReplaceSel(Out);
	TRACE("Thread stopped\n");

	return 0;
}

BOOL CDialog1Dlg::StartThread()
{
	b_ThreadRuns[droneNum - 1] = true;
	pThread[droneNum - 1] = AfxBeginThread(WorkThread, this, THREAD_PRIORITY_HIGHEST);
	TRACE("Thread started\n");

	return TRUE;
}

void CDialog1Dlg::StopThread()
{
	b_ThreadRuns[droneNum - 1] = false;
	//pThread[droneNum - 1]->SuspendThread();
	//pThread[droneNum - 1]->Delete();
}

UINT CDialog1Dlg::WorkThread(LPVOID pParam)
{
	CDialog1Dlg* pDlg = static_cast<CDialog1Dlg*>(pParam);
	pDlg->AVThread(pDlg->droneNum);

	return 0;
}

LRESULT CDialog1Dlg::HandleThreadMsg(WPARAM iParam, LPARAM strParam)
{
	CString Out;
	std::shared_ptr <std::string>* Msg = reinterpret_cast<std::shared_ptr<std::string>*>(iParam);
	Out.Format("%s\r\n", Msg->get()->c_str());
	m_EditCtrl1.SetSel(m_EditCtrl1.GetWindowTextLength(), m_EditCtrl1.GetWindowTextLength(), FALSE);
	m_EditCtrl1.ReplaceSel(Out);
	Msg->reset();

	return 0;
}

int CDialog1Dlg::count_colon(std::string s) {
	int count = 0;

	for (int i = 0; i < s.size(); i++)
		if (s[i] == ':') count++;

	return count;
}

LRESULT CDialog1Dlg::HandleTelemetryData(WPARAM wParam, LPARAM lParam)
{
	CString telemetry;
	void** tmp = (void**)wParam;
	char* str = (char*)tmp[0];
	int* dronenr = (int*)tmp[1];

	if (dronenr[0] == droneNum)
	{
		telemetry.SetString((char*)str, (int)lParam);
		int nTokenPos = 0;

		int count = count_colon(telemetry.GetString());
		if (count < 14) {
			return 0;
		}

		m_EditCtrl3.SetSel(0, m_EditCtrl3.GetWindowTextLength(), FALSE);
		m_EditCtrl3.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos).Left(10));
		m_EditCtrl4.SetSel(0, m_EditCtrl4.GetWindowTextLength(), FALSE);
		m_EditCtrl4.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos).Left(10));
		m_EditCtrl5.SetSel(0, m_EditCtrl5.GetWindowTextLength(), FALSE);
		m_EditCtrl5.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos).Left(5));
		m_EditCtrl6.SetSel(0, m_EditCtrl6.GetWindowTextLength(), FALSE);
		m_EditCtrl6.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl7.SetSel(0, m_EditCtrl7.GetWindowTextLength(), FALSE);
		m_EditCtrl7.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl8.SetSel(0, m_EditCtrl8.GetWindowTextLength(), FALSE);
		m_EditCtrl8.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl9.SetSel(0, m_EditCtrl9.GetWindowTextLength(), FALSE);
		m_EditCtrl9.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl10.SetSel(0, m_EditCtrl10.GetWindowTextLength(), FALSE);
		m_EditCtrl10.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl11.SetSel(0, m_EditCtrl11.GetWindowTextLength(), FALSE);
		m_EditCtrl11.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl12.SetSel(0, m_EditCtrl12.GetWindowTextLength(), FALSE);
		m_EditCtrl12.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl13.SetSel(0, m_EditCtrl13.GetWindowTextLength(), FALSE);
		m_EditCtrl13.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl14.SetSel(0, m_EditCtrl14.GetWindowTextLength(), FALSE);
		m_EditCtrl14.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl15.SetSel(0, m_EditCtrl15.GetWindowTextLength(), FALSE);
		m_EditCtrl15.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
		m_EditCtrl16.SetSel(0, m_EditCtrl16.GetWindowTextLength(), FALSE);
		m_EditCtrl16.ReplaceSel(telemetry.Tokenize(_T(":"), nTokenPos));
	}

	return 0;
}

LRESULT CDialog1Dlg::Renderer(WPARAM wParam, LPARAM lParam)
{
	static unsigned long t = 0;
	void** tmp = (void**)wParam;
	AVFrame* pFrameRGB = (AVFrame*)tmp[0];
	AVCodecContext* pCodecCtx = (AVCodecContext*)tmp[1];

	if (droneNum == (int)lParam && isConnected[(int)lParam - 1])
	{
		if (interval++ % 4 != 0) 
		{
			ShowFrameBMP(pFrameRGB, pCodecCtx->width, pCodecCtx->height, pFrameRGB->interlaced_frame);
		}
	}
	return 0;
}

int CDialog1Dlg::AVThread(int droneNumber)
{
	AVFormatContext* pFormatCtx = nullptr;
	AVCodecContext* pCodecCtx = nullptr;
	const AVCodec* pCodec = nullptr;
	AVFrame* pFrame = nullptr;
	AVFrame* pFrameRGB = nullptr;
	int videoStream = 0;
	BYTE field1, field2, field3, field4;
	AVPacket *packet = nullptr;
	uint8_t* buffer = nullptr;
	void* pAVStore[2] = { nullptr, nullptr };
	void* pTelemetry[2] = { nullptr, nullptr };

	m_ipctrl.GetAddress(field1, field2, field3, field4);

	const char* url = "rtsp://video:video@%d.%d.%d.%d:%d/live";

	CString url_final, port;
	m_EditCtrl2.GetWindowTextA(port);
	url_final.Format(url, field1, field2, field3, field4, atoi(port.GetBuffer()));

	pCodecCtx = avcodec_alloc_context3(pCodec);
	pFormatCtx = avformat_alloc_context();

	//av_log_set_level(log_sel[5]);
	av_log_set_flags(AV_LOG_SKIP_REPEATED);

	CString avcodec_ver, avformat_ver, avutil_ver;

	avcodec_ver.Format("avcodec version=%d.%d.%d %s", (avcodec_version() >> 16) & 0xffff, (avcodec_version() >> 8) & 0x00ff, (avcodec_version()) & 0x00ff, avcodec_license());
	avformat_ver.Format("avformat version=%d.%d.%d %s", (avformat_version() >> 16) & 0xffff, (avformat_version() >> 8) & 0x00ff, (avformat_version()) & 0x00ff, avformat_license());

	pFormatCtx->probesize = 30000000;
	pFormatCtx->max_analyze_duration = 30000;
	//pFormatCtx->flags |= AVFMT_FLAG_NOBUFFER | AVFMT_FLAG_FLUSH_PACKETS;

	AVDictionary* opts = 0;
	av_dict_set(&opts, "rtsp_transport", "udp", 0);
	av_dict_set(&opts, "preset", "ultrafast", 0);
	av_dict_set(&opts, "tune", "zerolatency", 0);
	//av_dict_set(&opts, "g", "30", 0);

	if (avformat_open_input(&pFormatCtx, url_final.GetBuffer(), NULL, &opts) != 0)
		goto end;

	//av_log_set_callback(custom_log);

	if (avformat_find_stream_info(pFormatCtx, NULL) < 0)
		goto end; // Couldn't find stream information

	// Dump information about file onto standard error
	av_dump_format(pFormatCtx, 0, url_final.GetBuffer(), false);

	// Find the first video stream
	for (int i = 0; i < (int)pFormatCtx->nb_streams; i++)
	{
		if (pFormatCtx->streams[i]->codecpar->codec_type == AVMEDIA_TYPE_VIDEO)
		{
			// Store the index of the video stream
			videoStream = i;
			// Set stream info hints if there is no size information yet
			if (pFormatCtx->streams[videoStream]->codecpar->width == 0)
			{
				pFormatCtx->streams[videoStream]->codecpar->width = 1920;
				pFormatCtx->streams[videoStream]->codecpar->height = 1080;
			}
			break;
		}
	}
	if (pCodecCtx)
	{
		CString decoder;
		m_ComboBox2.GetLBText(m_ComboBox2.GetCurSel(), decoder);
		pCodec = avcodec_find_decoder_by_name(decoder.GetBuffer());// (pCodecCtx->codec_id);
	}
	else
	{
		threadmsg[droneNumber - 1].Format("Drone: %d No suitable codec type found!", droneNumber);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(threadmsg[droneNumber - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		goto end;
	}

	pCodecCtx->thread_count = 4;
	pCodecCtx->thread_type = FF_THREAD_FRAME;

	pCodecCtx->flags |= AV_CODEC_FLAG_LOW_DELAY;
	pCodecCtx->flags2 |= AV_CODEC_FLAG2_FAST;

	//pCodecCtx->flags |= AV_CODEC_FLAG_OUTPUT_CORRUPT;
	//pCodecCtx->flags2 |= AV_CODEC_FLAG2_SHOW_ALL;

	pCodecCtx->flags |= AV_CODEC_FLAG_DROPCHANGED;

	//pCodecCtx->flags |= AV_CODEC_FLAG2_LOCAL_HEADER;

	// Report decoding errors to allow us to request a key frame
	pCodecCtx->err_recognition = AV_EF_EXPLODE;

	if (avcodec_open2(pCodecCtx, pCodec, NULL) < 0)
		goto end; // Could not open codec

	packet = av_packet_alloc();

	pFrame = av_frame_alloc();

	pFrameRGB = av_frame_alloc();

	if (int ret = avcodec_parameters_to_context(pCodecCtx, pFormatCtx->streams[videoStream]->codecpar) < 0)
	{
		threadmsg[droneNumber - 1].Format("Drone: %d Error %d copy codec parameter", droneNumber, ret);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(threadmsg[droneNumber - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}
	
	// Determine required buffer size and allocate buffer
	int numBytes = av_image_get_buffer_size(AV_PIX_FMT_RGB24, pFormatCtx->streams[videoStream]->codecpar->width,
		pFormatCtx->streams[videoStream]->codecpar->height, 16);
	buffer = static_cast<uint8_t*>(av_malloc(numBytes * sizeof(uint8_t)));

	if (numBytes < 0)
	{
		threadmsg[droneNumber - 1].Format("Drone: %d Error %d get image buffer size", droneNumber, numBytes);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(threadmsg[droneNumber - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		goto end;
	}

	// Assign appropriate parts of buffer to image planes in pFrameRGB
	av_image_fill_arrays(pFrameRGB->data, pFrameRGB->linesize, buffer, AV_PIX_FMT_RGB24,
		pFormatCtx->streams[videoStream]->codecpar->width, pFormatCtx->streams[videoStream]->codecpar->height, 16);
	
	pAVStore[0] = pFrameRGB;
	pAVStore[1] = pCodecCtx;

	while (av_read_frame(pFormatCtx, packet) >= 0)
	{
		BOOL bRet;
		MSG msg = { 0 };
		int frameFinished = 1;

		bRet = PeekMessage(&msg, NULL, 0, 0, PM_REMOVE);
		if (bRet != 0)
		{
			switch (msg.message)
			{
				case WM_THREAD_STOP:
					goto end;
					break;
				case WM_PYWRAPPER_IMAGEANDTELEMETRYDATA:
					if ((int)msg.lParam == droneNumber)
					{
						int nBytes = av_image_get_buffer_size(AV_PIX_FMT_NV12, pFormatCtx->streams[videoStream]->codecpar->width, pFormatCtx->streams[videoStream]->codecpar->height, 16);
						RTSPState* rtsp_state = (RTSPState*)pFormatCtx->priv_data;
						RTSPStream* rtsp_stream = rtsp_state->rtsp_streams[0];
						RTPDemuxContext* rtp_demux_context = (RTPDemuxContext*)rtsp_stream->transport_priv;
						void* sharedMem = data2Server(droneNumber);
						uint64_t temp = nBytes;
						memcpy((uint8_t*)sharedMem + 1025, &temp, sizeof(uint64_t));
						if (m_ComboBox2.GetCurSel() == 0) { //NV12
							memcpy((uint8_t*)sharedMem + 1034, pFrame->data[0], pFrame->linesize[0] * pFrame->height);
							memcpy((uint8_t*)sharedMem + 1034 + (pFrame->linesize[0] * pFrame->height), pFrame->data[1], pFrame->linesize[1] * pFrame->height / 2);
						}
						else // YUV420P
						{
							memcpy((uint8_t*)sharedMem + 1034, pFrame->data[0], pFrame->linesize[0] * pFrame->height);
							memcpy((uint8_t*)sharedMem + 1034 + (pFrame->linesize[0] * pFrame->height), pFrame->data[1], pFrame->linesize[1] * pFrame->height / 2);
							memcpy((uint8_t*)sharedMem + 1034 + (pFrame->linesize[0] * pFrame->height) + (pFrame->linesize[1] * pFrame->height / 2), pFrame->data[2], pFrame->linesize[2] * pFrame->height / 2);
						}
						if (telemetryData[droneNumber - 1].GetLength() <= 0)
							telemetryData[droneNumber - 1] = "0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0.000000:0";
						telemetryData[droneNumber - 1] = telemetryData[droneNumber - 1].Mid(0, telemetryData[droneNumber - 1].Find('\0', 0));
						temp = telemetryData[droneNumber - 1].GetLength();
						memcpy((uint8_t*)sharedMem + 1034 + (nBytes), &temp, sizeof(uint64_t));
						memcpy((uint8_t*)sharedMem + 1042 + (nBytes), telemetryData[droneNumber - 1].GetBuffer(), telemetryData[droneNumber - 1].GetLength());
						((v_uint8_t)sharedMem + 1033)[0] = false;
						break;
					}
					DispatchMessage(&msg);
					break;
				default:
					DispatchMessage(&msg);
			}
		}

		// Does this packet contain the video stream to decode it?
		if (packet->stream_index == videoStream)
		{
			// Decode video frame
			if (avcodec_send_packet(pCodecCtx, reinterpret_cast<const AVPacket*>(packet)) < 0) {
					threadmsg[droneNumber - 1].Format("Drone: %d AVcodec: send video packet failed", droneNumber);
					std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(threadmsg[droneNumber - 1].GetString()));
					PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
			}
			frameFinished = avcodec_receive_frame(pCodecCtx, pFrame);
		}
		else
		{
			// Anything other than the video stream is incoming Telemetry data!
			telemetryData[droneNumber - 1].SetString(reinterpret_cast<const char*>(packet->data), packet->size);
			pTelemetry[0] = telemetryData[droneNumber - 1].GetBuffer();
			pTelemetry[1] = &droneNumber;
			PostMessage(WM_THREAD_DATA, (WPARAM)pTelemetry, (LPARAM)telemetryData[droneNumber - 1].GetLength());
			continue;
		}

		av_packet_unref(packet);
		packet = av_packet_alloc();

		if (pFrame->key_frame == TRUE)
		{
			call_once(
				*flag, [this, droneNumber]() {
					threadmsg[droneNumber - 1].Format("Drone: %d Decoded frame is keyframe!", droneNumber);
					std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(threadmsg[droneNumber - 1].GetString()));
					PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
				});
		}
		// Did we get a video frame?
		if (frameFinished == 0 && droneNum == droneNumber && pFrame->linesize[0] > 0)
		{
			// Convert the image from its native format to RGB
			struct SwsContext* context = sws_getContext(pCodecCtx->width, pCodecCtx->height,
				pCodecCtx->pix_fmt, pCodecCtx->width, pCodecCtx->height,
				AV_PIX_FMT_BGR24, SWS_FAST_BILINEAR, NULL, NULL, NULL);
		
			sws_scale(context, pFrame->data, pFrame->linesize, 0, pCodecCtx->height, pFrameRGB->data, pFrameRGB->linesize);

			sws_freeContext(context);

			pFrameRGB->coded_picture_number = pFrame->coded_picture_number;
			pFrameRGB->interlaced_frame = pFrame->interlaced_frame;
			pFrameRGB->repeat_pict = pFrame->repeat_pict;
			pFrameRGB->top_field_first = pFrame->top_field_first;
			// Show the frame on the Dialog
			PostMessage(WM_THREAD_RENDER, (WPARAM)pAVStore, (LPARAM)droneNumber);
		}
	}
end:
	// Free the packet that was allocated by av_read_frame
	if (pFormatCtx)
		avformat_close_input(&pFormatCtx);
	av_packet_unref(packet);
	if (pFrame)
		av_free(pFrame);
	if (pFrameRGB)
		av_free(pFrameRGB);
	if (buffer)
		av_free(buffer);
	if (pCodecCtx)
		avcodec_close(pCodecCtx);
	if (pFormatCtx)
		avformat_free_context(pFormatCtx);


	SendMessage(WM_THREAD_END, NULL, droneNumber);
	b_ThreadRuns[droneNumber - 1] = false;
	return 0;
}

void CDialog1Dlg::ShowFrameBMP(AVFrame* pFrame, int width, int height, int interlaced)
{
	int bpp = 24;

	bmpheader.bfType = ('M' << 8) | 'B';
	bmpheader.bfReserved1 = 0;
	bmpheader.bfReserved2 = 0;
	bmpheader.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
	bmpheader.bfSize = bmpheader.bfOffBits + width * height * bpp / 8;

	bmpinfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
	bmpinfo.bmiHeader.biWidth = width;
	bmpinfo.bmiHeader.biHeight = -height;
	bmpinfo.bmiHeader.biPlanes = 1;
	bmpinfo.bmiHeader.biBitCount = bpp;
	bmpinfo.bmiHeader.biCompression = BI_RGB;
	bmpinfo.bmiHeader.biSizeImage = width * height * bpp / 8;
	bmpinfo.bmiHeader.biXPelsPerMeter = 0;
	bmpinfo.bmiHeader.biYPelsPerMeter = 0;
	bmpinfo.bmiHeader.biClrUsed = 0;
	bmpinfo.bmiHeader.biClrImportant = 0;

	CClientDC dc(this);

	int ret = SetStretchBltMode(dc.m_hDC, COLORONCOLOR);

	if(pFrame->linesize[0] > 0)
		ret = StretchDIBits(dc.m_hDC, 20 * getSystemScaleFactor(), 26 * getSystemScaleFactor(), 714 * getSystemScaleFactor(), 396 * getSystemScaleFactor(), 0, 0, width, height, (LPVOID)pFrame->data[0], (LPBITMAPINFO)&bmpinfo, DIB_RGB_COLORS, SRCCOPY);

	DeleteDC(dc);

	return;
}

void CDialog1Dlg::RedirectIOToConsole()
{
	CONSOLE_SCREEN_BUFFER_INFO coninfo = { 0 };

	// allocate a console for this app
	AllocConsole();
	SetConsoleTitle("DroneSwarmServer ffmpeg console log");
	HMENU hm = ::GetSystemMenu(GetConsoleWindow(), false);
	DeleteMenu(hm, SC_CLOSE, MF_BYCOMMAND);
	p_SetConsoleIcon(m_hIcon);
	// set the screen buffer to be big enough to let us scroll text
	GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &coninfo);
	coninfo.dwSize.Y = 0;
	SetConsoleScreenBufferSize(GetStdHandle(STD_OUTPUT_HANDLE), coninfo.dwSize);
	BOOL ret = SetConsoleMode(GetConsoleWindow(), ENABLE_MOUSE_INPUT | ENABLE_INSERT_MODE | ENABLE_QUICK_EDIT_MODE | ENABLE_EXTENDED_FLAGS | ENABLE_WINDOW_INPUT);

	CWnd* hWnd = FromHandle(GetConsoleWindow());
	CDC* pDC = hWnd->GetDC();

	freopen_s(&stream[0], "CONIN$", "r", stdin);   // reopen stdin handle as console window input
	freopen_s(&stream[1], "CONOUT$", "w", stdout);  // reopen stout handle as console window output
	freopen_s(&stream[2], "CONOUT$", "w", stderr); // reopen stderr handle as console window output

	std::ios::sync_with_stdio();
}

void CDialog1Dlg::OnBnClickedButton1()
{
	CString caption;
	m_ButtonCtrl1.GetWindowTextA(caption);
	if (caption == _T("Connect"))
	{
		Sleep(100);
		StartThread();
		m_ButtonCtrl1.SetWindowTextA(_T("Disconnect"));
		isConnected[droneNum - 1] = 1;
		m_ipctrl.GetWindowTextA(IPperDrone[droneNum - 1]);
		m_EditCtrl2.GetWindowTextA(PortperDrone[droneNum - 1]);
		m_ComboBox2.EnableWindow(FALSE);
		m_ComboBox3.EnableWindow(FALSE);
	}
	else
	{
		if (b_ThreadRuns[droneNum - 1])
		{
			BOOL ret = pThread[droneNum - 1]->PostThreadMessageA(WM_THREAD_STOP, 0, 0);
			StopThread();
		}
		isConnected[droneNum - 1] = 0;
		m_ButtonCtrl1.SetWindowTextA(_T("Connect"));
		m_ComboBox2.EnableWindow(TRUE);
		m_ComboBox3.EnableWindow(TRUE);
		flag = std::make_unique<std::once_flag>();
	}
}

void CDialog1Dlg::OnBnClickedCheck1()
{
	if (m_CheckBox1.GetCheck())
		RedirectIOToConsole();
	else
	{
		fclose(stream[0]);
		fclose(stream[1]);
		fclose(stream[2]);
		FreeConsole();
	}
}

void CDialog1Dlg::OnCbnSelchangeCombo1()
{
	av_log_set_level(log_sel[m_ComboBox1.GetCurSel()]);
}

void CDialog1Dlg::OnTRBNThumbPosChangingSlider1(NMHDR* pNMHDR, LRESULT* pResult)
{
	// This feature requires Windows Vista or greater.
	// The symbol _WIN32_WINNT must be >= 0x0600.
	NMTRBTHUMBPOSCHANGING* pNMTPC = reinterpret_cast<NMTRBTHUMBPOSCHANGING*>(pNMHDR);
	// TODO: Add your control notification handler code here

	CWnd* hWnd = nullptr;
	hWnd = FromHandle(GetConsoleWindow());

	if (hWnd)
	{
		CDC* pDC = hWnd->GetDC();

		COLORREF crBkgnd = pDC->GetBkColor();
		// do this everytime you want to change the transparency value
		hWnd->SetLayeredWindowAttributes(crBkgnd, m_Slider1.GetPos() /*transparency from 0 (transparent) to 255 (opaque)*/, LWA_ALPHA);
	}
	*pResult = 0;
}

void CDialog1Dlg::OnDeltaposSpin2(NMHDR* pNMHDR, LRESULT* pResult)
{
	LPNMUPDOWN pNMUpDown = reinterpret_cast<LPNMUPDOWN>(pNMHDR);

	static int pos = 0, npos = 0;
	// TODO: Add your control notification handler code here
	if (pos * -1 < 9 && pos * -1 >= 0 || pos == -9 && pNMUpDown->iDelta == 1)
	{
		if (pos == 0 && pNMUpDown->iDelta == 1)
			return;
		pos += pNMUpDown->iDelta;
		npos = pos * -1;
		CString droneNr;
		droneNr.Format("Drone Nr. %d", npos + 1);
		m_Static6.SetWindowText(droneNr);
		droneNum = npos + 1;
		dNum = npos;

		if (IPperDrone[dNum - pNMUpDown->iDelta == -1 ? 1 : 0] != "" && pNMUpDown->iDelta == -1 && IPperDrone[dNum] == "" && !isConnected[dNum])
		{
			m_ipctrl.ClearAddress();
			m_ipctrl.SetFieldFocus(0xFF);
		}
		else
		{
			if (IPperDrone[dNum] != "")
				m_ipctrl.SetWindowTextA(IPperDrone[dNum]);
		}

		if (PortperDrone[dNum - pNMUpDown->iDelta == -1 ? 1 : 0] != "" && pNMUpDown->iDelta == -1 && PortperDrone[dNum] == "" && !isConnected[dNum])
			;
		else
		{
			if (PortperDrone[dNum] != "")
				m_EditCtrl2.SetWindowTextA(PortperDrone[dNum]);
		}

		if (!isConnected[dNum])
			m_ButtonCtrl1.SetWindowTextA(_T("Connect"));
		else
			m_ButtonCtrl1.SetWindowTextA(_T("Disonnect"));

		m_ButtonCtrl1.UpdateWindow();
	}
	*pResult = 0;
}

#define CLIENTID    "MQTTDroneSwarm"
#define TOPIC       "MQTTWayPoints"
#define TIMEOUT     10000L

int CDialog1Dlg::MQTTmsgarrv(void* context, char* topicName, int topicLen, MQTTClient_message* message)
{
#define MEMOFFSET 4000000
	CDialog1Dlg* dlg1 = theApp.m_pDlg1;

	// Are we get the echo of our string or do we get image png data
	if (((uint8_t*)message->payload + 1)[0] != 0x50 && ((uint8_t*)message->payload + 2)[0] != 0x4E && ((uint8_t*)message->payload + 3)[0] != 0x47)
		return 1;

	int droneNr = ((uint8_t*)context)[0];

	dlg1->mainDlgmsg[droneNr - 1].Format("Drone: %d Message arrived topic: %s, with data size:%d\n", droneNr, topicName, message->payloadlen);
	std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(dlg1->mainDlgmsg[droneNr - 1].GetString()));
	::PostMessage(dlg1->GetSafeHwnd(), WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);

	void* temp = data2Server(droneNr);

	// Store image size into second 64bit long memory block
	uint64_t tLength = message->payloadlen;
	memcpy((uint8_t*)temp + MEMOFFSET + 9, &tLength, sizeof(uint64_t));

	memcpy((uint8_t*)temp + MEMOFFSET + 18, message->payload, message->payloadlen);

	v_uint8_t st = (v_uint8_t)temp + 17 + MEMOFFSET;

	MQTTClient_freeMessage(&message);
	MQTTClient_free(topicName);

	st[0] = false;

	return 1;
}

void CDialog1Dlg::MQTTmsgdeliv(void* context, MQTTClient_deliveryToken dt)
{
	CDialog1Dlg* dlg1 = theApp.m_pDlg1;
	int droneNr = ((uint8_t*)context)[0];
	dlg1->mainDlgmsg[droneNr - 1].Format("Drone: %d MQTT Message with delivery token %d sent\n", droneNr, dt);
	std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(dlg1->mainDlgmsg[droneNr - 1].GetString()));
	::PostMessage(dlg1->GetSafeHwnd(), WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
}

void CDialog1Dlg::MQTTconnlost(void* context, char* cause)
{
	CDialog1Dlg* dlg1 = theApp.m_pDlg1;
	int droneNr = ((uint8_t*)context)[0];
	dlg1->mainDlgmsg[droneNr - 1].Format("Drone: %d MQTT Connection lost %s\n", droneNr, cause);
	std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(dlg1->mainDlgmsg[droneNr - 1].GetString()));
	::PostMessage(dlg1->GetSafeHwnd(), WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
}

LRESULT CDialog1Dlg::SendWayPoint2Drone(WPARAM wParam, LPARAM lParam)
{
	int drone = (int)lParam;
	std::thread t(&CDialog1Dlg::SendWayPoint2Drone2, this, drone);
	t.detach();

	return 0;
}

int CDialog1Dlg::SendWayPoint2Drone2(int drone)
{
	MQTTClient client;
	MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
	MQTTClient_message pubmsg = MQTTClient_message_initializer;
	MQTTClient_deliveryToken token = 0;
	int rc;

	void* tmp = data2Server(drone);

	uint64_t temp;
	memcpy(&temp, (uint8_t*)tmp + 9, sizeof(uint64_t));
	const uint64_t len = temp;
	uint8_t* data = (uint8_t*)tmp + 18;
	v_uint8_t st = (v_uint8_t)tmp + 17;

	if (drone > 10 || drone < 1)
	{
		mainDlgmsg[drone - 1].Format("Drone number %d is not supported!", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		st[0] = false;
		return 1;
	}

	if (isConnected[drone - 1] == 0)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d is not connected, WayPointData not send!", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		st[0] = false;
		return 1;
	}

	const char* url = "tcp://%s:1883";
	CString finalUrl;
	finalUrl.Format(url, IPperDrone[drone - 1].GetBuffer());

	if ((rc = MQTTClient_create(&client, finalUrl.GetBuffer(), CLIENTID, MQTTCLIENT_PERSISTENCE_NONE, NULL)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to create client, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		st[0] = false;
		return rc;
	}

	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to connect, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		MQTTClient_destroy(&client);
		st[0] = false;
		return rc;
	}
	else
	{
		mainDlgmsg[drone - 1].Format("Drone: %d MQTT connected", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}

	pubmsg.payload = data;
	pubmsg.payloadlen = len;
	pubmsg.qos = m_ComboBox3.GetCurSel();
	pubmsg.retained = 0;

	if ((rc = MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to publish message, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		MQTTClient_destroy(&client);
		goto cleanup;
	}
	int ttoken = token;
	rc = -1;
	rc = MQTTClient_waitForCompletion(client, ttoken, TIMEOUT);
	if (rc == MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Message with delivery token %d delivered", drone, token);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}

cleanup:

	if ((rc = MQTTClient_disconnect(client, 10000)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone].Format("Drone: %d Failed to disconnect, code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}

	MQTTClient_destroy(&client);

	st[0] = false;

	return rc;
}

LRESULT CDialog1Dlg::GetImageAndTelemetryData(WPARAM wParam, LPARAM lParam)
{
	int drone = (int)lParam;

	if (isConnected[drone - 1] == 0)
	{
		void* sharedMem = data2Server(drone);
		((uint8_t*)sharedMem + 1033)[0] = false;
		mainDlgmsg[drone - 1].Format("Drone: %d is not connected, no image data to optain!", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		return 0;
	}

	mainDlgmsg[drone - 1].Format("Drone: %d image data aquired to Python", drone);
	std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
	PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);

	pThread[drone - 1]->PostThreadMessageA(WM_PYWRAPPER_IMAGEANDTELEMETRYDATA, wParam, lParam);

	return 1;
}

LRESULT CDialog1Dlg::GetEncodedImageData(WPARAM wparam, LPARAM lParam)
{
	int drone = (int)lParam;
	std::thread t(&CDialog1Dlg::GetEncodedImageData2, this, drone);
	// Detach the function from it's main process so we are not blocking any Dialog drawing
	t.detach();

	return 0;
}

int CDialog1Dlg::GetEncodedImageData2(int drone)
{
#define MEMOFFSETIMG 4000000
	using namespace std::chrono;

	int rc;
	MQTTDrone_Number = drone;
	MQTTClient client;
	MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
	MQTTClient_message pubmsg = MQTTClient_message_initializer;
	MQTTClient_deliveryToken token = 0;
	std::string t;

	void* tmp = data2Server(drone);

	uint64_t temp;
	memcpy(&temp, (uint8_t*)tmp + 9 + MEMOFFSETIMG, sizeof(uint64_t));
	const uint64_t len = temp;
	uint8_t* data = (uint8_t*)tmp + 18 + MEMOFFSETIMG;
	v_uint8_t st = (v_uint8_t)tmp + 17 + MEMOFFSETIMG;

	if (drone > 10 || drone < 1)
	{
		mainDlgmsg[drone - 1].Format("Drone number %d is not supported!", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		st[0] = false;
		return 1;
	}

	if (isConnected[drone - 1] == 0)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d is not connected, Drone CMD not send!", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		st[0] = false;
		return 1;
	}

	CString finalUrl;
	finalUrl.Format("tcp://%s:1883", IPperDrone[drone - 1].GetBuffer());

	if ((rc = MQTTClient_create(&client, finalUrl.GetBuffer(), CLIENTID, MQTTCLIENT_PERSISTENCE_NONE, NULL)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to create client, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		st[0] = false;
		return rc;
	}

	if ((rc = MQTTClient_setCallbacks(client, &MQTTDrone_Number, &CDialog1Dlg::MQTTconnlost, &CDialog1Dlg::MQTTmsgarrv, &CDialog1Dlg::MQTTmsgdeliv)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to set callbacks, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		MQTTClient_destroy(&client);
		st[0] = false;
		return rc;
	}

	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to connect, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		MQTTClient_destroy(&client);
		st[0] = false;
		return rc;
	}
	else
	{
		mainDlgmsg[drone - 1].Format("Drone: %d MQTT connected", drone);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}

	if ((rc = MQTTClient_subscribe(client, TOPIC, m_ComboBox3.GetCurSel())) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to subscribe, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		goto cleanup;
	}

	t = std::to_string(chrono::duration_cast<chrono::milliseconds>(chrono::system_clock::now().time_since_epoch()).count());

	// When passing RTT from Python a round trip time test is performed, this also has to be enabled in AOS App
	if (strcmp((const char*)data, "RTT") == 0)
	{
		pubmsg.payload = (void*)t.c_str();
		pubmsg.payloadlen = static_cast<int>(t.length());
	}
	else
	{
		pubmsg.payload = data;
		pubmsg.payloadlen = len;
	}
	pubmsg.qos = m_ComboBox3.GetCurSel();
	pubmsg.retained = 0;

	if ((rc = MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to publish message, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
		goto cleanup;
	}

	while (st[0])
		;

cleanup:

	if ((rc = MQTTClient_unsubscribe(client, TOPIC)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to unsubscribe, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}

	if ((rc = MQTTClient_disconnect(client, 10000)) != MQTTCLIENT_SUCCESS)
	{
		mainDlgmsg[drone - 1].Format("Drone: %d Failed to disconnect, return code %d", drone, rc);
		std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[drone - 1].GetString()));
		PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);
	}

	MQTTClient_destroy(&client);

	st[0] = false;

	return rc;
}

LRESULT CDialog1Dlg::IsHWDecoderEnabled(WPARAM wParam, LPARAM lParam)
{
#define MEMOFFSETHWD 3999000
	bool HWdecoder = m_ComboBox2.GetCurSel();

	void* tmp = data2Server(1);

	((v_uint8_t)tmp)[MEMOFFSETHWD] = !HWdecoder;
	((v_uint8_t)tmp)[MEMOFFSETHWD + 1] = 0;

	mainDlgmsg[0].Format("DroneSwarmServer: info to Python, HW decoder is turned %s", HWdecoder ? "OFF" : "ON");
	std::shared_ptr <std::string>* Msg = new std::shared_ptr<std::string>(std::make_shared<std::string>(mainDlgmsg[0].GetString()));
	PostMessage(WM_THREAD_TEXT, reinterpret_cast<WPARAM>(Msg), NULL);

	return 1;
}

LRESULT CDialog1Dlg::SetIPArray(WPARAM wParam, LPARAM lParam)
{
	int x = 0, y = 20;
	IPperDrone[lParam] = reinterpret_cast<char*>(wParam);
	if (lParam == 0)
	{
		m_ipctrl.SetWindowTextA(IPperDrone[lParam]);
		for (int i = 0; i < 10; i++) {
			::SendMessage(m_Spin1.GetSafeHwnd(), WM_LBUTTONDOWN, MK_LBUTTON, MAKELPARAM(x, y));
			Sleep(1);
			::SendMessage(m_Spin1.GetSafeHwnd(), WM_LBUTTONUP, MK_LBUTTON, MAKELPARAM(x, y));
			Sleep(1);
			if(i != 0)
				IPperDrone[i] = "";
		}
	}

	return 1;
}
