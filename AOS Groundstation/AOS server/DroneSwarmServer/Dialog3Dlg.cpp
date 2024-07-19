// Dialog4Dlg.cpp : implementation file
//

#include "pch.h"
#include "DroneSwarmServer.h"
#include "afxdialogex.h"
#include "Dialog3Dlg.h"


// CDialog3Dlg dialog

IMPLEMENT_DYNAMIC(CDialog3Dlg, CDialogEx)

CDialog3Dlg::CDialog3Dlg(CWnd* pParent /*=nullptr*/)
    : CDialogEx(IDD_DIALOG3, pParent)
{
    m_LabelCount = 0;
    b_ThreadRuns = false;
    pThread = nullptr;
}

CDialog3Dlg::~CDialog3Dlg()
{
    WSACleanup();
}

void CDialog3Dlg::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
    DDX_Control(pDX, IDC_LIST1, m_ListCtrl1);
    DDX_Control(pDX, IDC_BUTTON2, m_ButtonCtrl2);
    DDX_Control(pDX, IDC_BUTTON3, m_ButtonCtrl3);
    DDX_Control(pDX, IDC_COMBO4, m_ComboBox1);
    DDX_Control(pDX, IDC_PROGRESS1, m_Progress1);
}


BEGIN_MESSAGE_MAP(CDialog3Dlg, CDialogEx)
    ON_WM_CLOSE()
    ON_WM_TIMER()
    ON_WM_MOUSEMOVE()
    ON_WM_LBUTTONUP()
    ON_WM_QUERYDRAGICON()
    ON_NOTIFY(LVN_BEGINDRAG, IDC_LIST1, &CDialog3Dlg::OnBegindragList)
    ON_BN_CLICKED(IDC_BUTTON2, &CDialog3Dlg::OnBnClickedButton2)
    ON_BN_CLICKED(IDC_BUTTON3, &CDialog3Dlg::OnBnClickedButton3)
END_MESSAGE_MAP()


// CDialog3Dlg message handlers

BOOL CDialog3Dlg::OnInitDialog()
{
    CDialogEx::OnInitDialog();

    WSADATA wsaData;
    DWORD dwSize = 0, dwNetSize = 0;
    DWORD dwRetVal = 0;
    PIP_INTERFACE_INFO pInfo = NULL;
    int e = 0;

    WORD wVersionRequested = MAKEWORD(2, 2);
    if (WSAStartup(wVersionRequested, &wsaData) != 0)
        AfxMessageBox("Initialization of Winsock failed!");

    CRect rect;
    m_ListCtrl1.GetClientRect(&rect);
    int nColWid = (rect.Width() / 4); //account for scroll bar

    m_ListCtrl1.InsertColumn(0, "Internet Address", LVCFMT_LEFT, nColWid);
    m_ListCtrl1.InsertColumn(1, "Hostname", LVCFMT_LEFT, nColWid);
    m_ListCtrl1.InsertColumn(2, "Physical Address", LVCFMT_LEFT, nColWid);
    m_ListCtrl1.InsertColumn(3, "Type", LVCFMT_LEFT, nColWid);

    // Configure the look & feel.
    m_ListCtrl1.SetExtendedStyle(m_ListCtrl1.GetExtendedStyle() | LVS_EX_DOUBLEBUFFER | LVS_EX_HEADERDRAGDROP | LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES | LVS_EX_CHECKBOXES);
    SetWindowTheme(m_ListCtrl1.m_hWnd, L"Explorer", NULL);
    m_ListCtrl1.SetColumnSorting(2, CListCtrlEx::Auto, CListCtrlEx::MacAddress);
 
    dwRetVal = GetInterfaceInfo(NULL, &dwSize);
    if (dwRetVal == ERROR_INSUFFICIENT_BUFFER) {
        pInfo = (IP_INTERFACE_INFO*)malloc(dwSize);
        if (pInfo == nullptr) {
            return FALSE;
        }
    }
    dwRetVal = GetInterfaceInfo(pInfo, &dwSize);
    if (dwRetVal == NO_ERROR) {
        for (int32_t i = 0; i < pInfo->NumAdapters; i++) {
            netIndexMap[i][0] = i;
            netIndexMap[i][1] = pInfo->Adapter[i].Index;
        }
    }
    else if (dwRetVal == ERROR_NO_DATA) {
        AfxMessageBox("There are no network adapters with IPv4 enabled on the local system");
    }
    else {
        CString out;
        out.Format("GetInterfaceInfo failed with error: %d\n", dwRetVal);
        AfxMessageBox(out);
    }

    if (pInfo) {
        free(pInfo);
        pInfo = nullptr;
    }

    PMIB_IF_TABLE2 ftable;
    MIB_IF_ROW2 subtable;
    GetIfTable2(&ftable);

    for (uint32_t i = 0; i < ftable->NumEntries; i++)
    {
        subtable = ftable->Table[i];
        if (subtable.InterfaceIndex == netIndexMap[e][1])
        {
            m_ComboBox1.InsertString(e, CString(subtable.Description));
            e++;
        }
    }
    if (e > 0)
        m_ComboBox1.SetCurSel(0);

    m_ButtonCtrl3.EnableWindow(FALSE);

    m_bDragging = false;
    m_nDragIndex = -1;
    m_nDropIndex = -1;
    m_pDragImage = NULL;

    return TRUE;
}

HCURSOR CDialog3Dlg::OnQueryDragIcon()
{
    return (HCURSOR)m_hIcon;
}

BOOL CDialog3Dlg::StartThread()
{
    b_ThreadRuns = true;
    pThread = AfxBeginThread(WorkThread, this, THREAD_PRIORITY_NORMAL);
    TRACE("Thread started\n");

    return TRUE;
}

void CDialog3Dlg::StopThread()
{
    b_ThreadRuns = false;
    TRACE("Thread stopped\n");
}

UINT CDialog3Dlg::WorkThread(LPVOID pParam)
{
    CDialog3Dlg* pDlg = static_cast<CDialog3Dlg*>(pParam);
    pDlg->GetNetworkDevices();
    return 0;
}

BOOL CDialog3Dlg::InterfaceIdxToInterfaceIp(PMIB_IPADDRTABLE pIpAddrTable, DWORD dwIndex, char str[])
{
    struct in_addr inadTmp;
    char* szIpAddr;
    DWORD dwIdx;

    if (pIpAddrTable == nullptr || str == nullptr)
        return FALSE;

    str[0] = '\0';
    int test = sizeof(str);

    for (dwIdx = 0; dwIdx < pIpAddrTable->dwNumEntries; dwIdx++)
    {
        if (dwIndex == pIpAddrTable->table[dwIdx].dwIndex)
        {
            inadTmp.s_addr = pIpAddrTable->table[dwIdx].dwAddr;
            szIpAddr = inet_ntoa(inadTmp);
            if (szIpAddr)
            {
                strcpy_s(str, 512, szIpAddr);
                return TRUE;
            }
            else
                return FALSE;
        }
    }
    return FALSE;
}

BOOL CDialog3Dlg::PhysAddrToString(BYTE PhysAddr[], DWORD PhysAddrLen, char str[])
{
    DWORD dwIdx;

    if (PhysAddr == nullptr || PhysAddrLen == 0 || str == nullptr)
        return FALSE;

    str[0] = '\0';

    for (dwIdx = 0; dwIdx < PhysAddrLen; dwIdx++)
    {
        if (dwIdx == PhysAddrLen - 1)
            sprintf_s(str + (dwIdx * 3), sizeof(str + (dwIdx * 3)), "%02X", ((int)PhysAddr[dwIdx]) & 0xff);
        else
            sprintf_s(str + (dwIdx * 3), sizeof(str + (dwIdx * 3)), "%02X-", ((int)PhysAddr[dwIdx]) & 0xff);
    }
    return TRUE;
}

#define PACKET_BUFFER_SIZE 512000
DWORD CDialog3Dlg::GetNetworkDevices()
{
    PMIB_IPADDRTABLE pIPAddrTable = nullptr;
    PMIB_IPNETTABLE pIpNetTable = nullptr;
    PIP_INTERFACE_INFO pInfo = nullptr;
    PIP_ADAPTER_INFO pAdptInfo = nullptr, tmp_pAdptInfo = nullptr;
    DWORD dwSize = 0, dwNetSize = 0;
    DWORD dwRetVal = 0;
    IN_ADDR IPAddr;
    BOOL fOrder = FALSE;
    BOOL foundAddr = FALSE;
    DWORD status = NO_ERROR;
    DWORD statusRetry = NO_ERROR;
    DWORD dwCurrIndex;
    struct in_addr inadTmp;
    char szPrintablePhysAddr[512]{ 0 };
    char szType[512]{ 0 };
    char szIpAddr[512]{ 0 };
    LPVOID lpMsgBuf;
    CString IntfName;
    struct in_addr ipaddress { 0 }, subnetmask{ 0 };


    dwRetVal = GetInterfaceInfo(nullptr, &dwSize);
    if (dwRetVal == ERROR_INSUFFICIENT_BUFFER)
    {
        pInfo = (IP_INTERFACE_INFO*)malloc(dwSize);
        if (pInfo == nullptr)
        {
            return 1;
        }
    }

    dwRetVal = GetInterfaceInfo(pInfo, &dwSize);
    if (dwRetVal == NO_ERROR)
    {
        for (int i = 0; i < pInfo->NumAdapters; i++)
        {
            if (pInfo->Adapter[i].Index == netIndexMap[m_ComboBox1.GetCurSel()][1])
                IntfName = pInfo->Adapter[i].Name;
        }
    }

    if (pInfo)
    {
        free(pInfo);
        pInfo = nullptr;
    }

    dwSize = 0;

    dwRetVal = GetAdaptersInfo(nullptr, &dwSize);
    if (dwRetVal == ERROR_BUFFER_OVERFLOW)
    {
        tmp_pAdptInfo = pAdptInfo = (IP_ADAPTER_INFO*)malloc(dwSize);
        if (pAdptInfo == nullptr)
        {
            return 1;
        }
    }

    dwRetVal = GetAdaptersInfo(pAdptInfo, &dwSize);
    if (dwRetVal == NO_ERROR)
    {
        while (pAdptInfo)
        {
            if (netIndexMap[m_ComboBox1.GetCurSel()][1] == pAdptInfo->Index)
            {
                memcpy(rawData + 6, pAdptInfo->Address, pAdptInfo->AddressLength);
                memcpy(rawData + 22, pAdptInfo->Address, pAdptInfo->AddressLength);
                memcpy(myMAC, pAdptInfo->Address, pAdptInfo->AddressLength);
            }
            pAdptInfo = pAdptInfo->Next;
        }
    }

    if (tmp_pAdptInfo)
        free(tmp_pAdptInfo);

    dwSize = 0;

    pIPAddrTable = (MIB_IPADDRTABLE*)malloc(sizeof(MIB_IPADDRTABLE));

    if (pIPAddrTable)
    {
        if (GetIpAddrTable(pIPAddrTable, &dwSize, fOrder) == ERROR_INSUFFICIENT_BUFFER)
        {
            free(pIPAddrTable);
            pIPAddrTable = (MIB_IPADDRTABLE*)malloc(dwSize);

            if ((dwRetVal = GetIpAddrTable(pIPAddrTable, &dwSize, fOrder)) != NO_ERROR) {
                CString out;
                out.Format("GetIpAddrTable failed with error %d\n", dwRetVal);
                AfxMessageBox(out);
                if (FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS, NULL, dwRetVal, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),       // Default language
                    (LPTSTR)&lpMsgBuf, 0, NULL)) {
                    out.Format("\tError: %s", (LPTSTR)lpMsgBuf);
                    AfxMessageBox(out);
                    LocalFree(lpMsgBuf);
                }
                return dwRetVal;
            }
        }
        if (pIPAddrTable == NULL)
        {
            AfxMessageBox("Memory allocation failed for GetIpAddrTable");
            return ERROR_INSUFFICIENT_BUFFER;
        }
    }

    for (int i = 0; i < (int)pIPAddrTable->dwNumEntries; i++)
    {
        if (netIndexMap[m_ComboBox1.GetCurSel()][1] == pIPAddrTable->table[i].dwIndex)
        {
            IPAddr.S_un.S_addr = (u_long)pIPAddrTable->table[i].dwAddr;
            ipaddress = IPAddr;
            IPAddr.S_un.S_addr = (u_long)pIPAddrTable->table[i].dwMask;
            subnetmask = IPAddr;
            uint32_t senderIP = ntohl(ipaddress.S_un.S_addr);
            rawData[28] = (senderIP >> 24) & 0xFF;
            rawData[29] = (senderIP >> 16) & 0xFF;
            rawData[30] = (senderIP >> 8) & 0xFF;
            rawData[31] = senderIP & 0xFF;
            foundAddr = TRUE;
        }
    }

    char* version = (char*)PacketGetVersion();
    char* driverVersion = (char*)PacketGetDriverVersion();

    // Open the Adapter to send our ARP packages
    IntfName.Replace("TCPIP_", "NPF_");
    LPADAPTER dev = PacketOpenAdapter(IntfName.GetBuffer());

    if (PacketSetHwFilter(dev, NDIS_PACKET_TYPE_PROMISCUOUS) == FALSE)
    {
        TRACE("Warning: unable to set broadcast mode!\n");
    }

    // set a 512K buffer in the driver
    if (PacketSetBuff(dev, PACKET_BUFFER_SIZE) == FALSE)
    {
        TRACE("Unable to set the kernel buffer!\n");
        b_ThreadRuns = false;
        return -1;
    }

    // set a 100 ms read timeout
    if (PacketSetReadTimeout(dev, 100) == FALSE)
    {
        TRACE("Warning: unable to set the read tiemout!\n");
    }

    LPPACKET pPacket = PacketAllocatePacket();
    LPPACKET pPacket2 = PacketAllocatePacket();

    uint8_t* pktBuffer = (uint8_t*)malloc(PACKET_BUFFER_SIZE);

    PacketInitPacket(pPacket, (void*)&rawData, sizeof(rawData));
    PacketInitPacket(pPacket2, (void*)pktBuffer, PACKET_BUFFER_SIZE);

    int ret = PacketSetNumWrites(dev, 1);

    if (!foundAddr)
        goto end;

    {
        std::thread t(&CDialog3Dlg::ReceiveNetPackets, this, dev, pPacket2);
        t.detach();
    }

    // Empty the ARP cache
    FlushIpNetTable2(AF_INET, netIndexMap[m_ComboBox1.GetCurSel()][1]);

    uint32_t first_ip = ntohl(ipaddress.s_addr & subnetmask.s_addr);
    uint32_t last_ip = ntohl(ipaddress.s_addr | ~(subnetmask.s_addr));

    m_Progress1.SetRange32(first_ip, last_ip);

    // Calculate all possible IP's
    for (uint32_t iter = 0, ip = first_ip; ip <= last_ip; ++ip, iter++)
    {
        m_Progress1.SetPos(ip);
        uint32_t theip = htonl(ip);
        if (((theip >> 24) & 0xFF) != 0 && ((theip >> 24) & 0xFF) != 255)
        {
            ((uint8_t*)pPacket->Buffer)[38] = theip & 0xFF;
            ((uint8_t*)pPacket->Buffer)[39] = (theip >> 8) & 0xFF;
            ((uint8_t*)pPacket->Buffer)[40] = (theip >> 16) & 0xFF;
            ((uint8_t*)pPacket->Buffer)[41] = (theip >> 24) & 0xFF;
        }
        else
            continue;

        ret = PacketSendPacket(dev, pPacket, FALSE);

        if (iter % 2 == 0)
            Sleep(1);
    }

    while (b_ThreadRuns) {

        pIpNetTable = (PMIB_IPNETTABLE)malloc(sizeof(PMIB_IPNETTABLE));

        // query for buffer size needed
        status = GetIpNetTable(pIpNetTable, &dwNetSize, fOrder);

        if (status == ERROR_INSUFFICIENT_BUFFER)
        {
            // need more space
            free(pIpNetTable);
            pIpNetTable = (PMIB_IPNETTABLE)malloc(dwNetSize);
            assert(pIpNetTable);
            statusRetry = GetIpNetTable(pIpNetTable, &dwNetSize, fOrder);

            if (statusRetry != NO_ERROR)
            {
                AfxMessageBox("Couldn't retrieve IP net table");
            }
        }

        dwCurrIndex = pIpNetTable->table[0].dwIndex;
        if (InterfaceIdxToInterfaceIp(pIPAddrTable, dwCurrIndex, szIpAddr))
        {
            TRACE("\nInterface: %s on Interface 0x%X\n", szIpAddr, dwCurrIndex);
        }
        else
        {
            TRACE("Error: Could not convert Interface number 0x%X to IP Address.\n", pIpNetTable->table[0].dwIndex);
            continue;
        }

        for (uint32_t i = 0; i < pIpNetTable->dwNumEntries; ++i)
        {
            if (pIpNetTable->table[i].dwIndex != dwCurrIndex)
            {
                dwCurrIndex = pIpNetTable->table[i].dwIndex;
                if (InterfaceIdxToInterfaceIp(pIPAddrTable, dwCurrIndex, szIpAddr))
                {
                    TRACE("Interface: %s on Interface 0x%X\n", szIpAddr, dwCurrIndex);
                }
                else
                {
                    TRACE("Error: Could not convert Interface number 0x%X to IP address.\n", pIpNetTable->table[0].dwIndex);
                    continue;
                }
            }
            // Only get IP Table from current selected Network Interface
            if (pIpNetTable->table[i].dwIndex != netIndexMap[m_ComboBox1.GetCurSel()][1])
                continue;
            PhysAddrToString(pIpNetTable->table[i].bPhysAddr, pIpNetTable->table[i].dwPhysAddrLen, szPrintablePhysAddr);
            inadTmp.s_addr = pIpNetTable->table[i].dwAddr;
            switch (pIpNetTable->table[i].dwType)
            {
            case 1:
            {
                m_ListCtrl1.InsertItem(m_LabelCount, inet_ntoa(inadTmp));

                std::thread te(&CDialog3Dlg::delayedListCtrlEntry, this, m_LabelCount, inadTmp);
                te.detach();

                m_ListCtrl1.SetItemText(m_LabelCount, 2, _T(szPrintablePhysAddr));
                m_ListCtrl1.SetItemText(m_LabelCount, 3, _T("Other"));
                m_ListCtrl1.SetCheck(m_LabelCount, 0);
                m_ListCtrl1.Invalidate();
                m_LabelCount++;
                break;
            }
            case 2:
                // Invalidated is unhandled
                break;
            case 3:
            {
                m_ListCtrl1.InsertItem(m_LabelCount, inet_ntoa(inadTmp));

                std::thread te(&CDialog3Dlg::delayedListCtrlEntry, this, m_LabelCount, inadTmp);
                te.detach();

                m_ListCtrl1.SetItemText(m_LabelCount, 2, _T(szPrintablePhysAddr));
                m_ListCtrl1.SetItemText(m_LabelCount, 3, _T("Dynamic"));
                m_ListCtrl1.SetCheck(m_LabelCount, 0);
                m_ListCtrl1.Invalidate();
                m_LabelCount++;
                break;
            }
            case 4:
            {
                m_ListCtrl1.InsertItem(m_LabelCount, inet_ntoa(inadTmp));

                std::thread te(&CDialog3Dlg::delayedListCtrlEntry, this, m_LabelCount, inadTmp);
                te.detach();

                m_ListCtrl1.SetItemText(m_LabelCount, 2, _T(szPrintablePhysAddr));
                m_ListCtrl1.SetItemText(m_LabelCount, 3, _T("Static"));
                m_ListCtrl1.SetCheck(m_LabelCount, 0);
                m_ListCtrl1.Invalidate();
                m_LabelCount++;
                break;
            }
            default:
                strcpy_s(szType, sizeof(szType), "InvalidType");
            }
        }
        if (pIpNetTable)
            free(pIpNetTable);
        pIpNetTable = nullptr;
        dwNetSize = 0;
        m_LabelCount = 0;
        b_ThreadRuns = false;
    }
end:
    if (pIpNetTable)
        free(pIpNetTable);
    if (pIPAddrTable)
        free(pIPAddrTable);

    b_ThreadRuns = false;
    m_LabelCount = 0;
    OnBnClickedButton2();

    PacketFreePacket(pPacket);
    PacketFreePacket(pPacket2);
    PacketCloseAdapter(dev);
    free(pktBuffer);

    return NO_ERROR;
}

void CDialog3Dlg::ReceiveNetPackets(LPADAPTER dev, LPPACKET pPacket)
{
    while (1)
    {
        // capture the packets
        if (PacketReceivePacket(dev, pPacket, TRUE) == FALSE) {
            // We should reach here, if there is no package available anymore
            TRACE("Error: PacketReceivePacket failed");
            break;
        }
        // Another method to escape the while loop would be to check on the bytes readed
        //if (pPacket->ulBytesReceived <= 0)
        //    break;
        if (!b_ThreadRuns)
            break;
        ParsePackets(pPacket);
    }
}

void CDialog3Dlg::ParsePackets(LPPACKET lpPacket)
{
    ULONG	i, j, ulLines, ulen, ulBytesReceived;
    uint8_t* pChar, * pLine, * base;
    uint8_t* buf;
    u_int off = 0;
    u_int tlen, tlen1;
    struct bpf_hdr* hdr = nullptr;

    MIB_IPNET_ROW2 IpNetRow2 = { 0 };
    PMIB_IPNET_ROW2 pIpNetRow2 = &IpNetRow2;
    ulBytesReceived = lpPacket->ulBytesReceived;

    buf = (uint8_t*)lpPacket->Buffer;

    off = 0;

    // The identification bytes for a ARP package
    uint8_t ARPProto[] = { 0x08, 0x06 };
    char result[INET_ADDRSTRLEN]{ 0 };

    while (off < ulBytesReceived) {
        hdr = (struct bpf_hdr*)(buf + off);
        tlen1 = hdr->bh_datalen;
        tlen = hdr->bh_caplen;
        off += hdr->bh_hdrlen;

        ulLines = (tlen + 15) / 16;

        pChar = (uint8_t*)(buf + off);
        base = pChar;
        off = Packet_WORDALIGN(off + tlen);

        for (i = 0; i < ulLines; i++)
        {
            pLine = pChar;

            ulen = tlen;
            ulen = (ulen > 16) ? 16 : ulen;
            tlen -= ulen;

            for (j = 0; j < ulen; j++)
            {
                // Am I the destination address and is the package of type ARP
                if (j == 0 && memcmp((uint8_t*)pChar, (uint8_t*)myMAC, 6) == 0 && memcmp((uint8_t*)pChar + 12, (uint8_t*)ARPProto, 2) == 0)
                {
                    static uint8_t net = 0;
                    // Skip any double IP parsing
                    if (net == pChar[31])
                        continue;
                    inet_ntop(AF_INET, (void*)(pChar + 28), result, sizeof result);
                    net = pChar[31];
                    TRACE("Found IP:%s\n", result);
                    struct in_addr inaddr;
                    SOCKADDR_IN sin;
                    SOCKADDR_INET netaddr;
                    inet_pton(AF_INET, result, &inaddr);
                    sin.sin_addr = inaddr;
                    netaddr.Ipv4 = sin;
                    netaddr.si_family = AF_INET;
                    IpNetRow2.Address = netaddr;
                    memcpy(IpNetRow2.PhysicalAddress, pChar + 6, 6);
                    IpNetRow2.PhysicalAddressLength = 6;
                    IpNetRow2.InterfaceIndex = netIndexMap[m_ComboBox1.GetCurSel()][1];
                    IpNetRow2.State = NlnsReachable;
                    DWORD ret = CreateIpNetEntry2(pIpNetRow2);
                    TRACE("Setting ARP entry %02x %02x %02x %02x %02x %02x 0x%x\n", IpNetRow2.PhysicalAddress[0], IpNetRow2.PhysicalAddress[1], IpNetRow2.PhysicalAddress[2], IpNetRow2.PhysicalAddress[3], IpNetRow2.PhysicalAddress[4], IpNetRow2.PhysicalAddress[5], ret);
                    switch (ret) {
                    case ERROR_ACCESS_DENIED:
                        TRACE("ERROR_ACCESS_DENIED\n");
                        break;
                    case ERROR_INVALID_PARAMETER:
                        TRACE("ERROR_INVALID_PARAMETER\n");
                        break;
                    case ERROR_NOT_FOUND:
                        TRACE("ERROR_NOT_FOUND\n");
                        break;
                    case ERROR_NOT_SUPPORTED:
                        TRACE("ERROR_NOT_SUPPORTED\n");
                        break;
                    case NO_ERROR:
                        TRACE("No Error\n");
                        break;
                    default:
                        TRACE("Error on Setting ARP entry %02x %02x %02x %02x %02x %02x 0x%x\n", IpNetRow2.PhysicalAddress[0], IpNetRow2.PhysicalAddress[1], IpNetRow2.PhysicalAddress[2], IpNetRow2.PhysicalAddress[3], IpNetRow2.PhysicalAddress[4], IpNetRow2.PhysicalAddress[5], ret);
                    }
                }
                pChar++;
            }
            pChar = pLine;
        }
    }
}

void CDialog3Dlg::delayedListCtrlEntry(int index, in_addr addrs)
{
    struct hostent* remoteHost = NULL;
    remoteHost = gethostbyaddr((char*)&addrs, 4, AF_INET);
    if (remoteHost)
        m_ListCtrl1.SetItemText(index, 1, _T(remoteHost->h_name));
}

void CDialog3Dlg::OnBnClickedButton2()
{
    CString caption;
    m_ButtonCtrl2.GetWindowTextA(caption);
    if (caption == _T("Scan"))
    {
        Sleep(100);
        b_ThreadRuns = true;
        StartThread();
        m_ListCtrl1.SetRedraw(FALSE);
        m_ListCtrl1.DeleteAllItems();
        m_ListCtrl1.SetRedraw(TRUE);
        m_ButtonCtrl2.SetWindowTextA(_T("Scanning"));
        m_ButtonCtrl2.EnableWindow(FALSE);
        m_ComboBox1.EnableWindow(FALSE);
    }
    else
    {
        if (b_ThreadRuns)
        {
            b_ThreadRuns = false;
            StopThread();
        }
        m_ButtonCtrl2.SetWindowTextA(_T("Scan"));
        m_ButtonCtrl2.EnableWindow(TRUE);
        m_ButtonCtrl3.EnableWindow(TRUE);
        m_ComboBox1.EnableWindow(TRUE);
    }
}

void CDialog3Dlg::OnBnClickedButton3()
{
    int e = 0;
    HWND hWnd = theApp.m_pHWnd1;
    m_ButtonCtrl3.EnableWindow(FALSE);
    m_ButtonCtrl3.SetWindowTextA(_T("Wait.."));
    for (int i = 0; i < m_ListCtrl1.GetItemCount(); i++) {
        if (m_ListCtrl1.GetCheck(i)) {
            CString tmp = m_ListCtrl1.GetItemText(i, 0);
            ::SendMessage(hWnd, WM_FROM_DLG3, reinterpret_cast<WPARAM>(tmp.GetBuffer()), e);
            Sleep(10);
            e++;
        }
    }
    Sleep(150);
    m_ButtonCtrl3.EnableWindow(TRUE);
    m_ButtonCtrl3.SetWindowTextA(_T("SendTo->"));
}

void CDialog3Dlg::OnBegindragList(NMHDR* pNMHDR, LRESULT* pResult)
{
    NM_LISTVIEW* pNMListView = (NM_LISTVIEW*)pNMHDR;

    // Save the index of the item being dragged in m_nDragIndex
    // This will be used later for retrieving the info dragged
    m_nDragIndex = pNMListView->iItem;

    // Create a drag image
    POINT pt;
    int nOffset = -10; //offset in pixels for drag image (positive is up and to the left; neg is down and to the right)
    if (m_ListCtrl1.GetSelectedCount() > 1) //more than one item is selected
        pt.x = nOffset;
    pt.y = nOffset;

    m_pDragImage = m_ListCtrl1.CreateDragImage(m_nDragIndex, &pt);
    ASSERT(m_pDragImage); //make sure it was created
    // We will call delete later (in LButtonUp) to clean this up

    CBitmap bitmap;
    if (m_ListCtrl1.GetSelectedCount() > 1) //more than 1 item in list is selected
        //bitmap.LoadBitmap(IDB_BITMAP_MULTI);
        bitmap.LoadBitmap(IDB_BITMAP2);
    else
        bitmap.LoadBitmap(IDB_BITMAP3);
    //m_pDragImage->Replace(0, &bitmap, &bitmap);

    // Change the cursor to the drag image
    m_pDragImage->BeginDrag(0, CPoint(nOffset, nOffset - 4));
    m_pDragImage->DragEnter(GetDesktopWindow(), pNMListView->ptAction);

    // Set dragging flag and others
    m_bDragging = TRUE;	//we are in a drag and drop operation
    m_nDropIndex = -1;	//we don't have a drop index yet
    m_pDragList = &m_ListCtrl1; //make note of which list we are dragging from
    m_pDropWnd = &m_ListCtrl1;	//at present the drag list is the drop list

    // Capture all mouse messages
    SetCapture();

    *pResult = 0;
}

void CDialog3Dlg::OnMouseMove(UINT nFlags, CPoint point)
{
    // If we are in a drag/drop procedure (m_bDragging is true)
    if (m_bDragging)
    {
        // Move the drag image
        CPoint pt(point);	//get our current mouse coordinates
        ClientToScreen(&pt); //convert to screen coordinates
        m_pDragImage->DragMove(pt); //move the drag image to those coordinates
        // Unlock window updates (this allows the dragging image to be shown smoothly)
        m_pDragImage->DragShowNolock(false);

        // Get the CWnd pointer of the window that is under the mouse cursor
        CWnd* pDropWnd = WindowFromPoint(pt);
        ASSERT(pDropWnd); //make sure we have a window

        // If we drag outside current window we need to adjust the highlights displayed
        if (pDropWnd != m_pDropWnd)
        {
            if (m_nDropIndex != -1) //If we drag over the CListCtrl header, turn off the hover highlight
            {
                TRACE("m_nDropIndex is -1\n");
                CListCtrl* pList = (CListCtrl*)m_pDropWnd;
                VERIFY(pList->SetItemState(m_nDropIndex, 0, LVIS_DROPHILITED));
                // redraw item
                VERIFY(pList->RedrawItems(m_nDropIndex, m_nDropIndex));
                pList->UpdateWindow();
                m_nDropIndex = -1;
            }
            else //If we drag out of the CListCtrl altogether
            {
                TRACE("m_nDropIndex is not -1\n");
                CListCtrl* pList = (CListCtrl*)m_pDropWnd;
                int i = 0;
                int nCount = pList->GetItemCount();
                for (i = 0; i < nCount; i++)
                {
                    pList->SetItemState(i, 0, LVIS_DROPHILITED);
                }
                pList->RedrawItems(0, nCount);
                pList->UpdateWindow();
            }
        }

        // Save current window pointer as the CListCtrl we are dropping onto
        m_pDropWnd = pDropWnd;

        // Convert from screen coordinates to drop target client coordinates
        pDropWnd->ScreenToClient(&pt);

        //If we are hovering over a CListCtrl we need to adjust the highlights
        if (pDropWnd->IsKindOf(RUNTIME_CLASS(CListCtrl)))
        {
            //Note that we can drop here
            SetCursor(LoadCursor(NULL, IDC_ARROW));
            UINT uFlags;
            CListCtrl* pList = (CListCtrl*)pDropWnd;

            // Turn off hilight for previous drop target
            pList->SetItemState(m_nDropIndex, 0, LVIS_DROPHILITED);
            // Redraw previous item
            pList->RedrawItems(m_nDropIndex, m_nDropIndex);

            // Get the item that is below cursor
            m_nDropIndex = ((CListCtrl*)pDropWnd)->HitTest(pt, &uFlags);
            // Highlight it
            pList->SetItemState(m_nDropIndex, LVIS_DROPHILITED, LVIS_DROPHILITED);
            // Redraw item
            pList->RedrawItems(m_nDropIndex, m_nDropIndex);
            pList->UpdateWindow();
        }
        else
        {
            //If we are not hovering over a CListCtrl, change the cursor
            // to note that we cannot drop here
            SetCursor(LoadCursor(NULL, IDC_NO));
        }
        // Lock window updates
        m_pDragImage->DragShowNolock(true);
    }

    CDialog::OnMouseMove(nFlags, point);
}


void CDialog3Dlg::OnLButtonUp(UINT nFlags, CPoint point)
{
    //If we are in a drag and drop operation (otherwise we don't do anything)
    if (m_bDragging)
    {
        // Release mouse capture, so that other controls can get control/messages
        ReleaseCapture();

        // Note that we are NOT in a drag operation
        m_bDragging = FALSE;

        // End dragging image
        m_pDragImage->DragLeave(GetDesktopWindow());
        m_pDragImage->EndDrag();
        delete m_pDragImage; //must delete it because it was created at the beginning of the drag

        CPoint pt(point); //Get current mouse coordinates
        ClientToScreen(&pt); //Convert to screen coordinates
        // Get the CWnd pointer of the window that is under the mouse cursor
        CWnd* pDropWnd = WindowFromPoint(pt);
        ASSERT(pDropWnd); //make sure we have a window pointer
        // If window is CListCtrl, we perform the drop
        if (pDropWnd->IsKindOf(RUNTIME_CLASS(CListCtrl)))
        {
            m_pDropList = (CListCtrl*)pDropWnd; //Set pointer to the list we are dropping on
            DropItemOnList(m_pDragList, m_pDropList); //Call routine to perform the actual drop
        }
    }

    CDialog::OnLButtonUp(nFlags, point);
}

void CDialog3Dlg::DropItemOnList(CListCtrl* pDragList, CListCtrl* pDropList)
{
    // Unhilight the drop target
    pDropList->SetItemState(m_nDropIndex, 0, LVIS_DROPHILITED);

    // Set up the LV_ITEM for retrieving item from pDragList and adding the new item to the pDropList
    char szLabel[256];
    LVITEM lviT;
    LVITEM* plvitem;

    ZeroMemory(&lviT, sizeof(LVITEM)); //allocate and clear memory space for LV_ITEM
    lviT.iItem = m_nDragIndex;
    lviT.mask = LVIF_TEXT;
    lviT.pszText = szLabel;
    lviT.cchTextMax = 255;

    lvItem* pItem;
    lvItem lvi;
    lvi.plvi = &lviT;
    lvi.plvi->iItem = m_nDragIndex;
    lvi.plvi->mask = LVIF_TEXT;
    lvi.plvi->pszText = szLabel;
    lvi.plvi->cchTextMax = 255;

    if (pDragList->GetSelectedCount() == 1)
    {
        // Get item that was dragged
        pDragList->GetItem(lvi.plvi);
        lvi.sCol2 = pDragList->GetItemText(lvi.plvi->iItem, 1);
        lvi.sCol3 = pDragList->GetItemText(lvi.plvi->iItem, 2);
        lvi.sCol4 = pDragList->GetItemText(lvi.plvi->iItem, 3);

        if (pDragList == pDropList)
        {
            pDragList->DeleteItem(m_nDragIndex);
            if (m_nDragIndex < m_nDropIndex) m_nDropIndex--; //decrement drop index to account for item
            //being deleted above it
        }

        lvi.plvi->iItem = (m_nDropIndex == -1) ? pDropList->GetItemCount() : m_nDropIndex;
        pDropList->InsertItem(lvi.plvi);
        pDropList->SetItemText(lvi.plvi->iItem, 1, (LPCTSTR)lvi.sCol2);
        pDropList->SetItemText(lvi.plvi->iItem, 2, (LPCTSTR)lvi.sCol3);
        pDropList->SetItemText(lvi.plvi->iItem, 3, (LPCTSTR)lvi.sCol4);

        // Select the new item we just inserted
        pDropList->SetItemState(lvi.plvi->iItem, LVIS_SELECTED, LVIS_SELECTED);
    }
    else //more than 1 item is being dropped
    {
        CList<lvItem*, lvItem*> listItems;
        POSITION listPos;

        // Retrieve the selected items
        POSITION pos = pDragList->GetFirstSelectedItemPosition(); //iterator for the CListCtrl
        while (pos) //so long as we have a valid POSITION, we keep iterating
        {
            plvitem = new LVITEM;
            ZeroMemory(plvitem, sizeof(LVITEM));
            pItem = new lvItem;

            pItem->plvi = plvitem;
            pItem->plvi->iItem = m_nDragIndex;
            pItem->plvi->mask = LVIF_TEXT;
            pItem->plvi->pszText = new char; //since this is a pointer to the string, we need a new pointer to a new string on the heap
            pItem->plvi->cchTextMax = 255;

            m_nDragIndex = pDragList->GetNextSelectedItem(pos);

            // Get the item
            pItem->plvi->iItem = m_nDragIndex; //set the index in the drag list to the selected item
            pDragList->GetItem(pItem->plvi); //retrieve the information
            pItem->sCol2 = pDragList->GetItemText(pItem->plvi->iItem, 1);
            pItem->sCol3 = pDragList->GetItemText(pItem->plvi->iItem, 2);
            pItem->sCol4 = pDragList->GetItemText(pItem->plvi->iItem, 3);

            // Save the pointer to the new item in our CList
            listItems.AddTail(pItem);
        }

        if (pDragList == pDropList) //we are reordering the list (moving)
        {
            // Delete the selected items
            pos = pDragList->GetFirstSelectedItemPosition();
            while (pos)
            {
                pos = pDragList->GetFirstSelectedItemPosition();
                m_nDragIndex = pDragList->GetNextSelectedItem(pos);

                pDragList->DeleteItem(m_nDragIndex); //since we are MOVING, delete the item
                if (m_nDragIndex < m_nDropIndex) m_nDropIndex--; //must decrement the drop index to account
                // for the deleted items
            }
        }

        // Iterate through the items stored in memory and add them back into the CListCtrl at the drop index
        listPos = listItems.GetHeadPosition();
        while (listPos)
        {
            pItem = listItems.GetNext(listPos);

            m_nDropIndex = (m_nDropIndex == -1) ? pDropList->GetItemCount() : m_nDropIndex;
            pItem->plvi->iItem = m_nDropIndex;
            pDropList->InsertItem(pItem->plvi); //add the item
            pDropList->SetItemText(pItem->plvi->iItem, 1, pItem->sCol2);
            pDropList->SetItemText(pItem->plvi->iItem, 2, pItem->sCol3);
            pDropList->SetItemText(pItem->plvi->iItem, 3, pItem->sCol3);

            pDropList->SetItemState(pItem->plvi->iItem, LVIS_SELECTED, LVIS_SELECTED); //highlight/select the item we just added

            m_nDropIndex++; //increment the index we are dropping at to keep the dropped items in the same order they were in in the Drag List
        }

    }
}
