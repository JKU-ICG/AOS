// ListCtrlEx.cpp : implementation file
//

#include "pch.h"
#include "ListCtrlEx.h"


CListCtrlEx::EditorInfo::EditorInfo()
:m_pfnInitEditor(NULL)
,m_pfnEndEditor(NULL)
,m_pWnd(NULL)
,m_bReadOnly(false)
{
}
CListCtrlEx::EditorInfo::EditorInfo(PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd *pWnd)
:m_pfnInitEditor(pfnInitEditor)
,m_pfnEndEditor(pfnEndEditor)
,m_pWnd(pWnd)
,m_bReadOnly(false)
{
}

CListCtrlEx::CellInfo::CellInfo(int nColumn)
:m_clrBack(-1)
,m_clrText(-1)
,m_dwUserData(NULL)
,m_nColumn(nColumn)
{
	
}
CListCtrlEx::CellInfo::CellInfo(int nColumn, COLORREF clrBack, COLORREF clrText, DWORD_PTR dwUserData)
:m_clrBack(clrBack)
,m_clrText(clrText)
,m_dwUserData(dwUserData)
,m_nColumn(nColumn)
{
}
CListCtrlEx::CellInfo::CellInfo(int nColumn, EditorInfo eiEditor, COLORREF clrBack, COLORREF clrText, DWORD_PTR dwUserData)
:m_clrBack(clrBack)
,m_clrText(clrText)
,m_dwUserData(dwUserData)
,m_eiEditor(eiEditor)
,m_nColumn(nColumn)
{
}
CListCtrlEx::CellInfo::CellInfo(int nColumn, EditorInfo eiEditor, DWORD_PTR dwUserData)
:m_clrBack(-1)
,m_clrText(-1)
,m_dwUserData(dwUserData)
,m_eiEditor(eiEditor)
,m_nColumn(nColumn)
{
}

CListCtrlEx::ColumnInfo::ColumnInfo(int nColumn)
:m_eiEditor()
,m_clrBack(-1)
,m_clrText(-1)
,m_nColumn(nColumn)
,m_eSort(None)
,m_eCompare(NotSet)
,m_fnCompare(NULL)
{
}
CListCtrlEx::ColumnInfo::ColumnInfo(int nColumn, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd *pWnd)
:m_eiEditor(pfnInitEditor, pfnEndEditor, pWnd)
,m_nColumn(nColumn)
,m_clrBack(-1)
,m_clrText(-1)
,m_eSort(None)
,m_eCompare(NotSet)
,m_fnCompare(NULL)
{
}
CListCtrlEx::ItemData::ItemData(DWORD_PTR dwUserData)
:m_clrBack(0xFFFFFFFF)
,m_clrText(0xFFFFFFFF)
,m_dwUserData(dwUserData)
{
}
CListCtrlEx::ItemData::ItemData(COLORREF clrBack, COLORREF clrText, DWORD_PTR dwUserData)
:m_clrBack(clrBack)
,m_clrText(clrText)
,m_dwUserData(dwUserData)
{
}
CListCtrlEx::ItemData::~ItemData()
{
	while(m_aCellInfo.GetCount()>0)
	{
		CellInfo *pInfo = (CellInfo*)m_aCellInfo.GetAt(0);
		m_aCellInfo.RemoveAt(0);
		delete pInfo;
	}
}
// CListCtrlEx

IMPLEMENT_DYNAMIC(CListCtrlEx, CListCtrl)

CListCtrlEx::CListCtrlEx()
:m_pEditor(NULL)
,m_nEditingRow(-1)
,m_nEditingColumn(-1)
,m_msgHook()
,m_nRow(-1)
,m_nColumn(-1)
,m_bHandleDelete(FALSE)
,m_nSortColumn(-1)
,m_fnCompare(NULL)
,m_hAccel(NULL)
,m_dwSortData(NULL)
, m_bInvokeAddNew(FALSE)
{
#ifndef _WIN32_WCE
	EnableActiveAccessibility();
#endif
	
}
#define ID_EDITOR_CTRL		5000
CListCtrlEx::~CListCtrlEx()
{
	DeleteAllItemsData();
	DeleteAllColumnInfo();
}


BEGIN_MESSAGE_MAP(CListCtrlEx, CListCtrl)
	ON_NOTIFY_REFLECT_EX(NM_DBLCLK, &CListCtrlEx::OnNMDblclk)
	ON_NOTIFY_REFLECT_EX(NM_CUSTOMDRAW, &CListCtrlEx::OnNMCustomdraw)
	ON_NOTIFY_REFLECT(LVN_COLUMNCLICK, &CListCtrlEx::OnHdnItemclick)
END_MESSAGE_MAP()



// CListCtrlEx message handlers


// Retrieves the data (lParam) associated with a particular item.
DWORD_PTR CListCtrlEx::GetItemData(int nItem) const
{

	ItemData* pData = (ItemData*)GetItemDataInternal(nItem);
	if(!pData) return NULL;
	return pData->m_dwUserData;
}
// Retrieves the data (lParam) associated with a particular item.
DWORD_PTR CListCtrlEx::GetItemDataInternal(int nItem) const
{
	return CListCtrl::GetItemData(nItem);
}
int CListCtrlEx::InsertItem(int nItem, LPCTSTR lpszItem)
{
	int ret = CListCtrl::InsertItem(nItem, lpszItem);
	SetItemData(ret, 0);
	return ret;
}
int CListCtrlEx::InsertItem(int nItem, LPCTSTR lpszItem, int nImage)
{
	int ret = CListCtrl::InsertItem(nItem, lpszItem, nImage);
	SetItemData(ret, 0);
	return ret;
}
int CListCtrlEx::InsertItem(const LVITEM* pItem)
{
	int ret = 0;
	LVITEM pI = *pItem;
	if(pItem && (pItem->mask & LVIF_PARAM))
	{
		pI.mask &= (~LVIF_PARAM);
	}
	ret = CListCtrl::InsertItem(&pI);
	SetItemData(ret, pItem->lParam);
	return ret;
}
// Sets the data (lParam) associated with a particular item.
BOOL CListCtrlEx::SetItemData(int nItem, DWORD_PTR dwData)
{
	ItemData* pData = (ItemData*)GetItemDataInternal(nItem);
	if(!pData)
	{
		pData = new ItemData(dwData);
		m_aItemData.Add(pData);
	}
	else
		pData->m_dwUserData = dwData;
	return CListCtrl::SetItemData(nItem, (DWORD_PTR)pData);
}

// Removes a single item from the control.
BOOL CListCtrlEx::DeleteItem(int nItem)
{
	DeleteItemData(nItem);
	return CListCtrl::DeleteItem(nItem);
}
// Removes all items from the control.
BOOL CListCtrlEx::DeleteAllItems()
{
	int nCount = this->GetItemCount();
	DeleteAllItemsData();
	return CListCtrl::DeleteAllItems();
}
BOOL CListCtrlEx::DeleteAllItemsData( )
{
	while(m_aItemData.GetCount()>0)
	{
		ItemData* pData = (ItemData*)m_aItemData.GetAt(0);
		if(pData) delete pData;
		m_aItemData.RemoveAt(0);
	}

	return TRUE;
}
BOOL CListCtrlEx::DeleteItemData(int nItem)
{
	if(nItem < 0 || nItem > GetItemCount()) return FALSE;
	ItemData* pData = (ItemData*)CListCtrl::GetItemData(nItem);
	
	INT_PTR nCount = m_aItemData.GetCount();
	for(INT_PTR i = 0; i < nCount && pData; i++)
	{
		if(m_aItemData.GetAt(i) == pData)
		{
			m_aItemData.RemoveAt(i);
			break;
		}
	}

	if(pData) delete pData;

	return TRUE;
}	
BOOL CListCtrlEx::DeleteAllColumnInfo( )
{
	while(m_aColumnInfo.GetCount()>0)
	{
		ColumnInfo* pData = (ColumnInfo*)m_aColumnInfo.GetAt(0);
		if(pData) delete pData;
		m_aColumnInfo.RemoveAt(0);
	}

	return TRUE;
}
BOOL CListCtrlEx::DeleteColumnInfo(int nColumn)
{
	if(nColumn < 0 || nColumn > GetColumnCount()) return FALSE;
	ColumnInfo* pData = (ColumnInfo*)GetColumnInfo(nColumn);
	
	INT_PTR nCount = m_aColumnInfo.GetCount();
	for(INT_PTR i = 0; i < nCount && pData; i++)
	{
		if(m_aColumnInfo.GetAt(i) == pData)
		{
			m_aColumnInfo.RemoveAt(i);
			break;
		}
	}

	if(pData) delete pData;

	return TRUE;
}

void CListCtrlEx::SetColumnEditor(int nColumn, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd* pWnd)
{
	ColumnInfo* pColInfo = GetColumnInfo(nColumn);
	if(!pColInfo)
	{ 
		pColInfo = new ColumnInfo(nColumn);  
		m_aColumnInfo.Add(pColInfo);
	}
	pColInfo->m_eiEditor.m_pfnInitEditor = pfnInitEditor;
	pColInfo->m_eiEditor.m_pfnEndEditor = pfnEndEditor;
	pColInfo->m_eiEditor.m_pWnd = pWnd;
	
}

void CListCtrlEx::SetColumnEditor(int nColumn, CWnd* pWnd)
{
	SetColumnEditor(nColumn, NULL, NULL, pWnd);
}
void CListCtrlEx::SetRowEditor(int nRow, CWnd* pWnd)
{
	SetRowEditor(nRow, NULL, NULL, pWnd);
}
void CListCtrlEx::SetRowEditor(int nRow, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd* pWnd)
{
	ItemData* pData = (ItemData*)GetItemDataInternal(nRow);
	if(!pData)
	{ 
		SetItemData(nRow, 0);
		pData = (ItemData*)GetItemDataInternal(nRow);
	}
	pData->m_eiEditor.m_pfnInitEditor = pfnInitEditor;
	pData->m_eiEditor.m_pfnEndEditor = pfnEndEditor;
	pData->m_eiEditor.m_pWnd = pWnd;
	
}

CListCtrlEx::ColumnInfo* CListCtrlEx::GetColumnInfo(int nColumn)
{
	INT_PTR nCount = m_aColumnInfo.GetCount();
	for(INT_PTR i = 0; i < nCount; i++)
	{
		ColumnInfo* pColInfo = (ColumnInfo*)m_aColumnInfo.GetAt(i);
		if(pColInfo->m_nColumn == nColumn) return pColInfo;
	}
	return NULL;
}
int CListCtrlEx::FindItem(LVFINDINFO* pFindInfo, int nStart ) const
{
	if(pFindInfo->flags & LVIF_PARAM)
	{
		int nCount = GetItemCount();
		for(int i = nStart+1; i < nCount; i++)
		{
			if(pFindInfo->lParam == GetItemData(i)) return i;
		}
		return -1;
	}
	else
	{
		return CListCtrl::FindItem(pFindInfo, nStart);
	}
}
int CListCtrlEx::GetItemIndexFromData(DWORD_PTR dwData)
{
	LVFINDINFO find;
	find.flags = LVFI_PARAM;
	find.lParam = dwData;
	return CListCtrl::FindItem(&find);
}
int CALLBACK CListCtrlEx::CompareProc(LPARAM lParam1, LPARAM lParam2, LPARAM lParamSort)
{
	CListCtrlEx *This = reinterpret_cast<CListCtrlEx*>(lParamSort);
	ColumnInfo *pColInfo;
	int nSort = 0;
	int64_t nCompare = 0;

	if(!This) return 0;
	if(!(This->m_nSortColumn < 0 || This->m_nSortColumn >= This->GetColumnCount()) )
	{
		pColInfo = This->GetColumnInfo(This->m_nSortColumn);
		if(pColInfo && (pColInfo->m_eSort & SortBits)) 
		{
			nSort = pColInfo->m_eSort & Ascending ? 1: -1 ;
			if(!This->m_fnCompare && pColInfo->m_fnCompare) This->m_fnCompare = pColInfo->m_fnCompare;
		}
	}
	if(This->m_fnCompare && This->m_fnCompare != &CListCtrlEx::CompareProc) 
	{
		ItemData *pD1 = reinterpret_cast<ItemData*>(lParam1);
		ItemData *pD2 = reinterpret_cast<ItemData*>(lParam2);
		if(pD1) lParam1 = pD1->m_dwUserData;
		if(pD2) lParam2 = pD2->m_dwUserData;
		nCompare = This->m_fnCompare(lParam1, lParam2, This->m_dwSortData?This->m_dwSortData:This->m_nSortColumn);
		if(!This->m_dwSortData && nSort) 
		{
			return nCompare * nSort;
		}
	}
	if(!nSort) return 0;
	
	int nLeft = This->GetItemIndexFromData(lParam1); 
	int nRight = This->GetItemIndexFromData(lParam2);

	if(nLeft < 0) nLeft = lParam1;
	if(nRight < 0) nRight = lParam2;
	int nCount = This->GetItemCount();
	if(nLeft < 0 || nRight < 0 || nLeft >= nCount || nRight >= nCount) return 0;
	nCompare = Compare(nLeft, nRight, lParamSort);
	if (nCompare > 0)
		nCompare = 1;
	else
		nCompare = -1;
	return ((int)nCompare * nSort);
}
void CListCtrlEx::OnHdnItemclick(NMHDR *pNMHDR, LRESULT *pResult)
{
	NM_LISTVIEW*  phdr = reinterpret_cast<NM_LISTVIEW*>(pNMHDR);
	SortOnColumn(phdr->iSubItem, TRUE);
	*pResult = 0;
	//return FALSE;
}
BOOL CListCtrlEx::SortItems(PFNLVCOMPARE pfnCompare, DWORD_PTR dwData)
{
	int nCount = GetItemCount();
	DWORD_PTR dwEditingItemData = 0;
	if(m_nEditingRow >= 0 && m_nEditingRow < nCount)
	 dwEditingItemData = GetItemDataInternal(m_nEditingRow);
	CString dbg;
	dbg.Format("\nBefore : %d", m_nEditingRow);
	OutputDebugString(dbg);
	m_fnCompare = pfnCompare;
	m_dwSortData = dwData;
	BOOL ret = CListCtrl::SortItems(CompareProc, (DWORD_PTR)this);
	m_fnCompare = NULL;
	m_dwSortData = NULL;
	if(dwEditingItemData) 
		m_nEditingRow = GetItemIndexFromData(dwEditingItemData);
	
	dbg.Format("\nAfter : %d", m_nEditingRow);
	OutputDebugString(dbg);
	return ret;
}

BOOL CListCtrlEx::SortOnColumn(int nColumn, BOOL bChangeOrder)
{
	ColumnInfo *pColInfo;
	if((pColInfo = GetColumnInfo(nColumn)) && (pColInfo->m_eSort & SortBits ))
	{
		if(pColInfo->m_eSort & Auto)
		{
			pColInfo->m_eSort =(Sort)((pColInfo->m_eSort & (Ascending | Descending)) ? pColInfo->m_eSort : pColInfo->m_eSort | Descending);
			if(bChangeOrder) pColInfo->m_eSort = (Sort)(pColInfo->m_eSort ^ (Ascending | Descending));
		}		
		CHeaderCtrl *pHdr = this->GetHeaderCtrl();
		HDITEM hd;
		hd.mask = HDI_FORMAT;
		if(pHdr)
		{
			pHdr->GetItem(m_nSortColumn, &hd);
			hd.fmt = hd.fmt & ~(HDF_SORTDOWN|HDF_SORTUP);			
			pHdr->SetItem(m_nSortColumn, &hd);
		}
		m_nSortColumn = nColumn;
		CListCtrl::SortItems(CompareProc, (DWORD_PTR)this);
		if(pHdr)
		{
			pHdr->GetItem(nColumn, &hd);
			hd.fmt = hd.fmt & ~(HDF_SORTDOWN|HDF_SORTUP);
			hd.fmt |= pColInfo->m_eSort & Ascending ? HDF_SORTUP : HDF_SORTDOWN;
			pHdr->SetItem(nColumn, &hd);
		}		
		return TRUE;
	}
	return FALSE;
}

BOOL CListCtrlEx::OnNMDblclk(NMHDR *pNMHDR, LRESULT *pResult)
{
	NM_LISTVIEW *pNMListView = (NM_LISTVIEW *)pNMHDR;
	if(!pNMListView) return FALSE;
	int nItem = pNMListView->iItem, nSubItem = pNMListView->iSubItem;		

	*pResult = DisplayEditor(nItem, nSubItem);

	return *pResult;
}

BOOL CListCtrlEx::EnsureSubItemVisible(int nItem, int nSubItem, CRect *pRect)
{
	BOOL ret = EnsureVisible(nItem, FALSE);
	CRect rect;
	GetSubItemRect(nItem, nSubItem, LVIR_LABEL, rect);
	CRect rtList;
	GetClientRect(&rtList);
	if(rect.right > rtList.Width()) Scroll(CSize( rect.Width() > rtList.Width()?rect.left : rect.right - rtList.Width(), 0));
	if(rect.left < 0) Scroll(CSize(rect.left));
	if(pRect)
	{
		GetSubItemRect(nItem, nSubItem, LVIR_LABEL, rect);
		rect.right = min(rect.right, rtList.Width()-4);
		*pRect = rect;
	}
	return ret;
}
BOOL CListCtrlEx::DisplayEditor(int nItem, int nSubItem)
{
	int nCount = GetItemCount();
	DWORD_PTR dwEditingItemData = 0;
	if(nItem >= 0 && nItem < nCount)
	 dwEditingItemData = GetItemDataInternal(nItem);
	HideEditor();
	if(dwEditingItemData) 
		nItem = GetItemIndexFromData(dwEditingItemData);
	if(nItem < 0 || nItem > nCount || nSubItem < 0 || nSubItem > this->GetColumnCount() 
		|| IsColumnReadOnly(nSubItem) || IsRowReadOnly(nItem) || IsCellReadOnly(nItem, nSubItem)) return FALSE;
	CRect rectSubItem;
	//GetSubItemRect(nItem, nSubItem, LVIR_LABEL, rectSubItem);
	EnsureSubItemVisible(nItem, nSubItem, &rectSubItem);

	CellInfo *pCellInfo = GetCellInfo(nItem, nSubItem);
	ColumnInfo *pColInfo = GetColumnInfo(nSubItem);
	ItemData *pRowInfo = (ItemData *)GetItemDataInternal(nItem);

	m_pEditor = &m_eiDefEditor;
	BOOL bReadOnly = FALSE;
	if(pColInfo && !(bReadOnly|= pColInfo->m_eiEditor.m_bReadOnly) && pColInfo->m_eiEditor.IsSet())
	{				
		m_pEditor = &pColInfo->m_eiEditor;
	}
	if(pRowInfo && !(bReadOnly|= pRowInfo->m_eiEditor.m_bReadOnly) && pRowInfo->m_eiEditor.IsSet())
	{				
		m_pEditor = &pRowInfo->m_eiEditor;
	}
	if(pCellInfo && !(bReadOnly|= pCellInfo->m_eiEditor.m_bReadOnly) && pCellInfo->m_eiEditor.IsSet())
	{
		m_pEditor = &pCellInfo->m_eiEditor;
	}
	if(bReadOnly || !m_pEditor || !m_pEditor->IsSet() || m_pEditor->m_bReadOnly){m_pEditor = NULL; return  FALSE;}
	
	m_nEditingRow = nItem;
	m_nEditingColumn = nSubItem;
	m_nRow = nItem;
	m_nColumn = nSubItem;
	CString text =  GetItemText(nItem, nSubItem);
	if(m_pEditor->m_pfnInitEditor) 
		m_pEditor->m_pfnInitEditor(&m_pEditor->m_pWnd, nItem, nSubItem, text, GetItemData(nItem), this, TRUE);

	if(!m_pEditor->m_pWnd) return  FALSE;
	SelectItem(-1, FALSE);
	if(!m_pEditor->m_pfnInitEditor) m_pEditor->m_pWnd->SetWindowText(text);

	m_pEditor->m_pWnd->SetParent(this);
	m_pEditor->m_pWnd->SetOwner(this);

	ASSERT(m_pEditor->m_pWnd->GetParent() == this);	
	m_pEditor->m_pWnd->SetWindowPos(NULL, rectSubItem.left, rectSubItem.top, rectSubItem.Width(), rectSubItem.Height(), SWP_SHOWWINDOW);	
	m_pEditor->m_pWnd->ShowWindow(SW_SHOW);
	m_pEditor->m_pWnd->SetFocus();

	m_msgHook.Attach(m_pEditor->m_pWnd->m_hWnd, this->m_hWnd);

	return TRUE;
}

CListCtrlEx::CellInfo* CListCtrlEx::GetCellInfo(int nItem, int nSubItem)
{
	ItemData* pData = (ItemData*)GetItemDataInternal(nItem);
	if(pData == NULL) return NULL;
	INT_PTR nCount = pData->m_aCellInfo.GetCount();
	for(INT_PTR i = 0; i < nCount; i++)
	{
		CellInfo *pInfo = (CellInfo*)pData->m_aCellInfo.GetAt(i);
		if(pInfo && pInfo->m_nColumn == nSubItem) return pInfo;
	}
	return NULL;
}

void CListCtrlEx::HideEditor(BOOL bUpdate)
{
	CSingleLock lock(&m_oLock, TRUE);
	if(lock.IsLocked() && m_msgHook.Detach())
	{	
		if(m_pEditor && m_pEditor->m_pWnd)
		{
			m_pEditor->m_pWnd->ShowWindow(SW_HIDE);
			CString text;
			DWORD_PTR dwData = 0;
			if(GetItemCount() > m_nEditingRow)
			{
				text =  GetItemText(m_nEditingRow, m_nEditingColumn);
				dwData = GetItemData(m_nEditingRow);
			}
			else
			{
				bUpdate = FALSE;
			}
			if(m_pEditor->m_pfnEndEditor)
			{
				bUpdate = m_pEditor->m_pfnEndEditor(&m_pEditor->m_pWnd, m_nEditingRow, m_nEditingColumn, text, dwData, this, bUpdate);
			}
			else
			{
				m_pEditor->m_pWnd->GetWindowText(text);
			}
			if(bUpdate)
			{
				SetItemText(m_nEditingRow, m_nEditingColumn, text);
			}
			if(GetItemCount() > m_nEditingRow) Update(m_nEditingRow);
			if(bUpdate == -1) SortOnColumn(m_nEditingColumn);
			m_pEditor = NULL;
		}
	}
	lock.Unlock();
}

int CListCtrlEx::GetColumnCount(void)
{
	CHeaderCtrl *pHdr = GetHeaderCtrl();
	if(pHdr) return pHdr->GetItemCount();
	int i = 0;
	LVCOLUMN col;
	col.mask = LVCF_WIDTH;
	while(GetColumn(i++, &col));
	return i;
}

BOOL CListCtrlEx::PreTranslateMessage(MSG* pMsg)
{
	if((m_hAccel && GetParent() && GetFocus() == this && ::TranslateAccelerator(GetParent()->m_hWnd, m_hAccel, pMsg))) return TRUE;
	
	if(pMsg->message == WM_KEYDOWN )
	{
		if( pMsg->wParam == VK_TAB && (GetKeyState(VK_CONTROL)>>8 != -1))
		{
			int nCount = GetItemCount();
			int nColCount = GetColumnCount();
			if(m_pEditor && m_pEditor->m_pWnd && m_pEditor->m_pWnd->m_hWnd == pMsg->hwnd)
			{
				PostMessage(pMsg->message, pMsg->wParam, pMsg->lParam);
				return TRUE;
			}
			bool bShiftPressed = (GetKeyState(VK_SHIFT)>>8 == -1);
			if(!bShiftPressed && nCount == 0 && OnAddNew())
			{
				nCount = GetItemCount();
				m_nColumn = 0;
			}
			if(nCount > 0 && nColCount > 0)
			{
				BOOL bContinue;
				do
				{
					bContinue = FALSE;
					if(m_nRow < 0 || m_nColumn < 0)
					{ 
						m_nRow = bShiftPressed ? nCount - 1: 0; 
						m_nColumn = bShiftPressed ? nColCount - 1: 0;
					}
					else if(m_nRow >= nCount || m_nColumn >= nColCount)
					{
						m_nRow = bShiftPressed ? nCount - 1: 0 ; 
						m_nColumn = bShiftPressed ? nColCount - 1: 0;
					}
					else
					{
						m_nColumn += (bShiftPressed ? -1 : 1);
						if(m_nColumn <0 || m_nColumn >= nColCount)
						{
							m_nRow += (bShiftPressed ? -1 : 1);
							m_nColumn = (bShiftPressed ? nColCount-1 : 0);
						}
					}
					
					if(m_bInvokeAddNew && ((m_nRow == nCount -1 && m_nColumn >= nColCount)||m_nRow >= nCount))
					{
						HideEditor();
						if(OnAddNew())
						{
							nCount = GetItemCount();
							m_nColumn = 0;
						}
						else return TRUE;
					}
					if(m_nRow >= 0 && m_nRow < nCount && m_nColumn >= 0 && m_nColumn < nColCount )
					{					
						if(DisplayEditor(m_nRow, m_nColumn))
							return TRUE;
						bContinue = TRUE;
					}
				}while(bContinue);
			}
		}
		else if( pMsg->wParam == VK_DELETE  && m_bHandleDelete)
		{
			DeleteSelectedItems();
			return TRUE;
		}
	}
	return CListCtrl::PreTranslateMessage(pMsg);
	
}

BOOL CListCtrlEx::OnNMCustomdraw(NMHDR *pNMHDR, LRESULT *pResult)
{
	LPNMLVCUSTOMDRAW lplvcd = reinterpret_cast<LPNMLVCUSTOMDRAW>(pNMHDR);

	int iRow = lplvcd->nmcd.dwItemSpec;
	int iCol = lplvcd->iSubItem;
	*pResult = 0;
	switch(lplvcd->nmcd.dwDrawStage)
	{
		case CDDS_PREPAINT:
		*pResult = CDRF_NOTIFYSUBITEMDRAW;          // ask for subitem notifications.
		break;

		case CDDS_ITEMPREPAINT:
			*pResult = CDRF_NOTIFYSUBITEMDRAW;
			break;
		case CDDS_ITEMPREPAINT|CDDS_SUBITEM|CDDS_ITEM:
			{
				COLORREF clrBack = 0xFFFFFFFF;
				COLORREF clrText = 0xFFFFFFFF;

				if (iRow % 2 != 0)
					clrBack = RGB(255, 255, 255);
				else
					clrBack = RGB(218, 218, 218);

				// Store the colors back in the NMLVCUSTOMDRAW struct.
				
				*pResult = CDRF_DODEFAULT;
				CellInfo *pCell = GetCellInfo(iRow, iCol);
				if(pCell)
				{
					clrBack = pCell->m_clrBack;
					clrText = pCell->m_clrText;
				}
				if(clrBack == 0xFFFFFFFF && clrText == 0xFFFFFFFF)
				{
					ItemData* pData = (ItemData*)GetItemDataInternal(iRow);
					if(pData)
					{
						clrBack = pData->m_clrBack;
						clrText = pData->m_clrText;
					}
				}
				if(clrBack == 0xFFFFFFFF && clrText == 0xFFFFFFFF)
				{
					ColumnInfo *pInfo = GetColumnInfo(iCol);
					if(pInfo)
					{						
						clrBack = pInfo->m_clrBack;
						clrText = pInfo->m_clrText;
					}
				}
				if(clrBack != 0xFFFFFFFF)
				{
					lplvcd->clrTextBk = clrBack;					
					*pResult  = CDRF_NEWFONT;
				}
				else
				{
					if(clrBack != m_clrDefBack)
					{
						lplvcd->clrTextBk = m_clrDefBack;				
						*pResult  = CDRF_NEWFONT;
					}
				}
				if(clrText != 0xFFFFFFFF)
				{					
					lplvcd->clrText = clrText;					
					*pResult  = CDRF_NEWFONT;
				}				
				else
				{
					if(clrText != m_clrDefText)
					{
						lplvcd->clrText = m_clrDefText;		
						*pResult  = CDRF_NEWFONT;
					}
				}
			}
		break;

		default:
		*pResult = CDRF_DODEFAULT;
	}
	if(*pResult == 0 || *pResult == CDRF_DODEFAULT)
		return FALSE;
	else
		return TRUE;
}

void CListCtrlEx::SetRowColors(int nItem, COLORREF clrBk, COLORREF clrText)
{
	
	ItemData* pData = (ItemData*)GetItemDataInternal(nItem);
	if(!pData) SetItemData(nItem, 0);
	pData = (ItemData*)GetItemDataInternal(nItem);
	if(!pData) return;

	pData->m_clrText = clrText;
	pData->m_clrBack = clrBk;
	Update(nItem);
}
BOOL CListCtrlEx::AddItem(int ItemIndex, int SubItemIndex, LPCTSTR ItemText, int ImageIndex)
{
	LV_ITEM lvItem;
	lvItem.mask = LVIF_TEXT;
	lvItem.iItem = ItemIndex;
	lvItem.iSubItem = SubItemIndex;
	lvItem.pszText = (LPTSTR) ItemText;
	if(ImageIndex != -1){
		lvItem.mask |= LVIF_IMAGE;
		lvItem.iImage |= LVIF_IMAGE;
	}
	if(SubItemIndex == 0)
		return InsertItem(&lvItem);
	return SetItem(&lvItem);
}
LRESULT CListCtrlEx::WindowProc(UINT message, WPARAM wParam, LPARAM lParam)
{
	if(message == UM_HIDEEDITOR)
	{
		HideEditor((BOOL)wParam);
	}
	return CListCtrl::WindowProc(message, wParam, lParam);
}

void CListCtrlEx::SetColumnColors(int nColumn, COLORREF clrBack, COLORREF clrText)
{
	if(nColumn < 0 || nColumn >= GetColumnCount()) return;

	ColumnInfo* pColInfo = GetColumnInfo(nColumn);
	if(!pColInfo)
	{ 
		pColInfo = new ColumnInfo(nColumn);  
		m_aColumnInfo.Add(pColInfo);
	}

	pColInfo->m_clrBack = clrBack;
	pColInfo->m_clrText = clrText;
	
}
void CListCtrlEx::SetCellColors(int nRow, int nColumn, COLORREF clrBack, COLORREF clrText)
{
	if(nRow < 0 || nRow >= GetItemCount() || nColumn < 0 || nColumn >= GetColumnCount()) return;
	CellInfo* pCellInfo = GetCellInfo(nRow, nColumn);
	if(!pCellInfo)
	{ 
		SetCellData(nRow, nColumn, 0);
	}
	pCellInfo = GetCellInfo(nRow, nColumn);
	ASSERT(pCellInfo);
	pCellInfo->m_clrBack = clrBack;
	pCellInfo->m_clrText = clrText;
	
}
void CListCtrlEx::PreSubclassWindow()
{
	m_clrDefBack = GetTextBkColor();
	m_clrDefText = GetTextColor();
	CListCtrl::PreSubclassWindow();
	SetExtendedStyle(LVS_EX_FULLROWSELECT);
	ModifyStyle(0, LVS_REPORT );
}

BOOL CListCtrlEx::SetCellData(int nItem, int nSubItem, DWORD_PTR dwData)
{
	if(nItem < 0 || nItem >= GetItemCount() || nSubItem < 0 || nSubItem >= GetColumnCount()) return FALSE;
	CellInfo* pCellInfo = GetCellInfo(nItem, nSubItem);
	if(!pCellInfo)
	{ 
		pCellInfo = new CellInfo(nSubItem);
		ItemData *pData = (ItemData*)GetItemDataInternal(nItem);
		if(!pData)
		{
			SetItemData(nItem, 0);
			pData = (ItemData*)GetItemDataInternal(nItem);
		}
		pData->m_aCellInfo.Add(pCellInfo);
	}
	pCellInfo->m_dwUserData = dwData;

	return TRUE;
}

DWORD_PTR CListCtrlEx::GetCellData(int nItem, int nSubItem)
{
	CellInfo* pCellInfo = GetCellInfo(nItem, nSubItem);
	if(pCellInfo) return pCellInfo->m_dwUserData;
	else return 0;
}

void CListCtrlEx::SetCellEditor(int nRow, int nColumn, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd* pWnd)
{
	if(nRow < 0 || nRow >= GetItemCount() || nColumn < 0 || nColumn >= GetColumnCount()) return;
	CellInfo* pCellInfo = GetCellInfo(nRow, nColumn);
	if(!pCellInfo)
	{ 
		SetCellData(nRow, nColumn, 0);
		pCellInfo = (CellInfo*)GetCellInfo(nRow, nColumn);
		ASSERT(pCellInfo);
	}
	
	pCellInfo->m_eiEditor.m_pfnInitEditor = pfnInitEditor;
	pCellInfo->m_eiEditor.m_pfnEndEditor = pfnEndEditor;
	pCellInfo->m_eiEditor.m_pWnd = pWnd;
	
}

void CListCtrlEx::SetCellEditor(int nRow, int nColumn, CWnd* pWnd)
{
	SetCellEditor(nRow, nColumn, NULL, NULL, pWnd);
}


void CListCtrlEx::SetDefaultEditor(PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd* pWnd)
{
	m_eiDefEditor.m_pfnInitEditor = pfnInitEditor;
	m_eiDefEditor.m_pfnEndEditor = pfnEndEditor;
	m_eiDefEditor.m_pWnd = pWnd;	
}

void CListCtrlEx::SetDefaultEditor(CWnd* pWnd)
{
	SetDefaultEditor(NULL, NULL, pWnd);
}

void CListCtrlEx::SetColumnReadOnly(int nColumn, bool bReadOnly)
{
	if(nColumn < 0 || nColumn >= GetColumnCount()) return;
	ColumnInfo *pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	if(!pInfo) SetColumnEditor(nColumn, (CWnd*)NULL);
	pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	ASSERT(pInfo);
	pInfo->m_eiEditor.m_bReadOnly = bReadOnly;
}

void CListCtrlEx::SetColumnSorting(int nColumn, Sort eSort, Comparer eComparer)
{
	if(nColumn < 0 || nColumn >= GetColumnCount() || !(eSort & SortBits)) return;
	ColumnInfo *pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	if(!pInfo) SetColumnEditor(nColumn, (CWnd*)NULL);
	pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	ASSERT(pInfo);
	pInfo->m_eSort = eSort;
	pInfo->m_eCompare = eComparer;
	pInfo->m_fnCompare = NULL;
}
void CListCtrlEx::SetColumnSorting(int nColumn, Sort eSort, PFNLVCOMPARE fnCallBack)
{
	if(nColumn < 0 || nColumn >= GetColumnCount() || !(eSort & SortBits)) return;
	ColumnInfo *pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	if(!pInfo) SetColumnEditor(nColumn, (CWnd*)NULL);
	pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	ASSERT(pInfo);
	pInfo->m_eSort = eSort;
	pInfo->m_eCompare = NotSet;
	pInfo->m_fnCompare = fnCallBack;
}
void CListCtrlEx::SetCellReadOnly(int nRow, int nColumn, bool bReadOnly )
{
	if(nRow < 0 || nRow >= GetItemCount() || nColumn < 0 || nColumn >= GetColumnCount()) return;

	CellInfo *pInfo = (CellInfo*)GetCellInfo(nRow, nColumn);
	if(!pInfo) SetCellEditor(nRow, nColumn, (CWnd*)NULL);
	pInfo = (CellInfo*)GetCellInfo(nRow, nColumn);
	ASSERT(pInfo);
	pInfo->m_eiEditor.m_bReadOnly = bReadOnly;
}
void CListCtrlEx::SetRowReadOnly(int nRow, bool bReadOnly)
{
	if(nRow < 0 || nRow >= GetItemCount() ) return;

	ItemData *pInfo = (ItemData*)GetItemDataInternal(nRow);
	if(!pInfo) SetItemData(nRow, 0);
	pInfo = (ItemData*)GetItemDataInternal(nRow);
	ASSERT(pInfo);
	pInfo->m_eiEditor.m_bReadOnly = bReadOnly;
}

BOOL CListCtrlEx::IsColumnReadOnly(int nColumn)
{
	if(nColumn < 0 || nColumn >= GetColumnCount()) return FALSE;
	ColumnInfo *pInfo = (ColumnInfo*)GetColumnInfo(nColumn);
	if( pInfo )
	{
		 return pInfo->m_eiEditor.m_bReadOnly;
	}
	return FALSE;
}

BOOL CListCtrlEx::IsRowReadOnly(int nRow)
{
	if(nRow < 0 || nRow >= GetItemCount() ) return FALSE;
	ItemData *pInfo = (ItemData*)GetItemDataInternal(nRow);
	if( pInfo )
	{
		 return pInfo->m_eiEditor.m_bReadOnly;
	}
	return FALSE;
}

BOOL CListCtrlEx::IsCellReadOnly(int nRow, int nColumn)
{
	if(nRow < 0 || nRow >= GetItemCount() || nColumn < 0 || nColumn >= GetColumnCount()) return FALSE;

	CellInfo *pInfo = (CellInfo*)GetCellInfo(nRow, nColumn);
	if( pInfo )
	{
		 return pInfo->m_eiEditor.m_bReadOnly;
	}
	else
		return (IsRowReadOnly(nRow) || IsColumnReadOnly(nColumn));
}

void CListCtrlEx::DeleteSelectedItems(void)
{
	int nItem = -1;
	while((nItem = GetNextItem(-1, LVNI_SELECTED)) >= 0)
	{
		DeleteItem(nItem);
	}	
}
void CListCtrlEx::HandleDeleteKey(BOOL bHandle)
{
	m_bHandleDelete = bHandle;
}
void CListCtrlEx::SelectItem(int nItem, BOOL bSelect)
{
	if(nItem < 0)
	{
		int nIndex = -1;
		while((nIndex = this->GetNextItem(nIndex, bSelect ? LVNI_ALL : LVNI_SELECTED)) >= 0)
		{
			this->SetItemState(nIndex, (bSelect ? LVIS_SELECTED: 0 ), LVIS_SELECTED);
		}
	}
	else
	{
		this->SetItemState(nItem, (bSelect ? LVIS_SELECTED: 0 ), LVIS_SELECTED);
	}
}

BOOL CListCtrlEx::DeleteAllColumns(void)
{
	while(DeleteColumn(0));
	return (GetColumnCount() == 0);
}

BOOL CListCtrlEx::Reset(void)
{
	return (DeleteAllItems() &&
	DeleteAllColumns());
}
int64_t CListCtrlEx::Compare(LPARAM lParam1, LPARAM lParam2, LPARAM lParamSort)
{
	CListCtrlEx *This = (CListCtrlEx *)lParamSort;
	if(!This || This->m_nSortColumn < 0 || This->m_nSortColumn >= This->GetColumnCount()) return 0;
	int nSubItem = This->m_nSortColumn;
	ColumnInfo *pInfo = This->GetColumnInfo(nSubItem);
	if(!pInfo) return 0;

	CString strLeft = This->GetItemText(lParam1, nSubItem);
	CString strRight = This->GetItemText(lParam2, nSubItem);
	
	switch(pInfo->m_eCompare)
	{
	case Int:
		return CompareInt(strLeft, strRight);
	case Double:
		return CompareDouble(strLeft, strRight);
	case StringNoCase:
		return CompareStringNoCase(strLeft, strRight);
	case StringNumber:
		return CompareNumberString(strLeft, strRight);
	case StringNumberNoCase:
		return CompareNumberStringNoCase(strLeft, strRight);
	case String:
		return CompareString(strLeft, strRight);
	case Date:
		return CompareDate(strLeft, strRight);
	case MacAddress:
		return CompareMacAddr(strLeft, strRight);
	case NotSet:
		return 0;
	default:
		return CompareString(strLeft, strRight);
	}
	return CompareString(strLeft, strRight);
}
int64_t CListCtrlEx::CompareInt(LPCSTR pLeftText, LPCSTR pRightText)
{
	return (int)(atol(pLeftText) - atol(pRightText));
}
int64_t CListCtrlEx::CompareDouble(LPCSTR pLeftText, LPCSTR pRightText)
{
	return (int)(atof(pLeftText) - atof(pRightText));
}
int64_t CListCtrlEx::CompareString(LPCSTR pLeftText, LPCSTR pRightText)
{
	return CString(pLeftText).Compare(pRightText);
}
int64_t CListCtrlEx::CompareNumberString(LPCSTR pLeftText, LPCSTR pRightText)
{
	LONGLONG l1 = atol(pLeftText);
	LONGLONG l2 = atol(pRightText);
	if(l1 && l2 && (l1 - l2))
	{
		CString str1, str2;
		str1.Format("%ld", l1);
		str2.Format("%ld", l2);
		CString left(pLeftText);
		CString right(pRightText);
		if(str1.GetLength() == left.GetLength() && str2.GetLength() == right.GetLength()) return (int) (l1 - l2);		
	}
	return CString(pLeftText).Compare(pRightText);
}
int64_t CListCtrlEx::CompareNumberStringNoCase(LPCSTR pLeftText, LPCSTR pRightText)
{
	LONGLONG l1 = atol(pLeftText);
	LONGLONG l2 = atol(pRightText);
	if(l1 && l2 && (l1 - l2))
	{
		CString str1, str2;
		str1.Format("%ld", l1);
		str2.Format("%ld", l2);
		CString left(pLeftText);
		CString right(pRightText);
		if(str1.GetLength() == left.GetLength() && str2.GetLength() == right.GetLength()) return (int) (l1 - l2);		
	}
	return CString(pLeftText).CompareNoCase(pRightText);
}
int64_t CListCtrlEx::CompareStringNoCase(LPCSTR pLeftText, LPCSTR pRightText)
{
	return CString(pLeftText).CompareNoCase(pRightText);
}
int64_t CListCtrlEx::CompareDate(LPCSTR pLeftText, LPCSTR pRightText)
{
	COleDateTime dL, dR;
	dL.ParseDateTime(pLeftText);
	dR.ParseDateTime(pRightText);
	return (dL == dR ? 0 :(dL < dR ? -1 : 1));
}

int64_t CListCtrlEx::CompareMacAddr(LPCSTR pLeftText, LPCSTR pRightText)
{
	uint64_t outAddr1 = 0, outAddr2 = 0;
	CString toInt1, toInt2;
	CString temp1 = "0x", temp2 = "0x";

	toInt1 = pLeftText;
	toInt2 = pRightText;
	toInt1.Replace("-", "");
	toInt2.Replace("-", "");

	temp1.Append(toInt1);
	temp2.Append(toInt2);

	outAddr1 = strtoll(temp1.GetBuffer(), 0, 16);
	outAddr2 = strtoll(temp2.GetBuffer(), 0, 16);
	
	return (int64_t)outAddr1 - (int64_t)outAddr2;
}

BOOL CListCtrlEx::PreCreateWindow(CREATESTRUCT& cs)
{
	cs.dwExStyle |= LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES;

	return CListCtrl::PreCreateWindow(cs);
}
