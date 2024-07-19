#pragma once
#include "MsgHook.h"
#include<Afxmt.h>
// CListCtrlEx
typedef BOOL (*PFNEDITORCALLBACK)(CWnd** pWnd, int nRow, int nColumn, CString& strSubItemText, DWORD_PTR dwItemData, void* pThis, BOOL bUpdate);
class CListCtrlEx : public CListCtrl
{
	DECLARE_DYNAMIC(CListCtrlEx)

public:
	CListCtrlEx();
	virtual ~CListCtrlEx();
	// Retrieves the data (lParam) associated with a particular item.
	DWORD_PTR GetItemData(int nItem) const;
	// Retrieves the data (lParam) associated with a particular item.
	DWORD_PTR GetItemDataInternal(int nItem) const;
	// Sets the data (lParam) associated with a particular item.
	BOOL SetItemData(int nItem, DWORD_PTR dwData);	
	// Removes a single item from the control.
	BOOL DeleteItem(int nItem);
	// Removes all items from the control.
	BOOL DeleteAllItems();
	// Finds an item in the control matching the specified criteria.  
	int FindItem(LVFINDINFO* pFindInfo, int nStart = -1) const;
	// Call to sort items using a custom comparison function.
	BOOL SortItems(PFNLVCOMPARE pfnCompare, DWORD_PTR dwData);
	// Adds an item to the control.
	int InsertItem(const LVITEM* pItem);
	int InsertItem(int nItem, LPCTSTR lpszItem);
	int InsertItem(int nItem, LPCTSTR lpszItem, int nImage);

	BOOL EnsureSubItemVisible(int nItem, int nSubItem, CRect *pRect = NULL);
	typedef enum Sort
	{
		None = 0,
		Ascending = 1,
		Descending = 2,
		Auto = 4,
		SortBits = 7
	}Sort;
	typedef enum Comparer
	{
		NotSet,
		Int,
		Double,
		String,
		StringNumber,
		StringNoCase,
		StringNumberNoCase,
		Date,
		MacAddress
	}Comparer;
protected:
	static int CALLBACK CompareProc(LPARAM lParam1, LPARAM lParam2, LPARAM lParamSort);
	static int64_t Compare(LPARAM lParam1, LPARAM lParam2, LPARAM lParamSort);
	static int64_t CompareInt(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareDouble(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareString(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareNumberString(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareNumberStringNoCase(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareStringNoCase(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareDate(LPCSTR pLeftText, LPCSTR pRightText);
	static int64_t CompareMacAddr(LPCSTR pLeftText, LPCSTR pRightText);
	CCriticalSection m_oLock;
protected:
	DECLARE_MESSAGE_MAP()
protected:
	typedef struct EditorInfo
	{
		PFNEDITORCALLBACK m_pfnInitEditor;
		PFNEDITORCALLBACK m_pfnEndEditor;
		CWnd *m_pWnd;
		BOOL m_bReadOnly;
		EditorInfo();
		EditorInfo(PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd *pWnd = NULL);
		inline BOOL IsSet(){return (m_pfnInitEditor || m_pWnd);}
	}EditorInfo;
	
	typedef struct CellInfo
	{	
		EditorInfo m_eiEditor;
		COLORREF m_clrBack;
		COLORREF m_clrText;	
		DWORD_PTR	m_dwUserData;
		int m_nColumn;
		CellInfo(int nColumn);
		CellInfo(int nColumn, COLORREF clrBack, COLORREF clrText, DWORD_PTR dwUserData = NULL);
		CellInfo(int nColumn, EditorInfo eiEditor, COLORREF clrBack, COLORREF clrText, DWORD_PTR dwUserData = NULL);
		CellInfo(int nColumn, EditorInfo eiEditor, DWORD_PTR dwUserData = NULL);
	}CellInfo;
	
	typedef struct ColumnInfo
	{
		EditorInfo m_eiEditor;
		int m_nColumn;
		COLORREF m_clrBack;
		COLORREF m_clrText;	
		Sort m_eSort;
		Comparer m_eCompare;
		PFNLVCOMPARE m_fnCompare;
		ColumnInfo(int nColumn);
		ColumnInfo(int nColumn, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK pfnEndEditor, CWnd *pWnd = NULL);
	}ColumnInfo;
	
	typedef struct ItemData
	{
		EditorInfo m_eiEditor;
		CArray<CellInfo*> m_aCellInfo;
		COLORREF m_clrBack;
		COLORREF m_clrText;		
		DWORD_PTR	m_dwUserData;
		ItemData(DWORD_PTR dwUserData = NULL);
		ItemData(COLORREF clrBack, COLORREF clrText, DWORD_PTR dwUserData = NULL);
		inline BOOL IsSet()
		{
			return (m_dwUserData || m_clrBack != -1 || m_clrText != -1 || !m_aCellInfo.IsEmpty());
		}		
		virtual ~ItemData();
	}ItemData;

	CPtrArray m_aItemData;
	CPtrArray m_aColumnInfo;
	
	BOOL DeleteItemData(int nItem);
	BOOL DeleteAllItemsData( );
	BOOL DeleteAllColumnInfo( );
	BOOL DeleteColumnInfo(int nIndex );
	EditorInfo *m_pEditor;
	EditorInfo m_eiDefEditor;
	int m_nEditingRow;
	int m_nEditingColumn;
	int m_nRow;
	int m_nColumn;
	COLORREF m_clrDefBack;
	COLORREF m_clrDefText;
	CMsgHook m_msgHook;
	BOOL m_bHandleDelete;
	int m_nSortColumn;
	PFNLVCOMPARE m_fnCompare;
	DWORD_PTR m_dwSortData;
public:
	///////////////////////////////////////////////////////////////////////////
	//Editor stuff
	///////////////////////////////////////////////////////////////////////////
	void SetColumnEditor(int nColumn, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK m_pfnEndEditor = NULL,  CWnd* pWnd = NULL);
	void SetColumnEditor(int nColumn, CWnd* pWnd);
	void SetCellEditor(int nRow, int nColumn, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK m_pfnEndEditor = NULL,  CWnd* pWnd = NULL);
	void SetCellEditor(int nRow, int nColumn, CWnd* pWnd);
	void SetRowEditor(int nRow, PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK m_pfnEndEditor = NULL,  CWnd* pWnd = NULL);
	void SetRowEditor(int nRow, CWnd* pWnd);
	void SetDefaultEditor(PFNEDITORCALLBACK pfnInitEditor, PFNEDITORCALLBACK m_pfnEndEditor = NULL,  CWnd* pWnd = NULL);
	void SetDefaultEditor(CWnd* pWnd);
	void SetColumnReadOnly(int nColumn, bool bReadOnly = true);
	void SetCellReadOnly(int nRow, int nColumn, bool bReadOnly = true);
	void SetRowReadOnly(int nRow, bool bReadOnly = true);
	BOOL IsColumnReadOnly(int nColumn);
	BOOL IsRowReadOnly(int nRow);
	BOOL IsCellReadOnly(int nRow, int nColumn);

	BOOL DisplayEditor(int nItem, int nSubItem);
	void HideEditor(BOOL bUpdate = TRUE);

	int GetColumnCount(void);

	///////////////////////////////////////////////////////////////////////////
	//Display stuff
	///////////////////////////////////////////////////////////////////////////
	void SetRowColors(int nItem, COLORREF clrBk, COLORREF clrText);
	void SetColumnColors(int nColumn, COLORREF clrBack, COLORREF clrText);
	void SetCellColors(int nRow, int nColumn, COLORREF clrBack, COLORREF clrText);

	///////////////////////////////////////////////////////////////////////////
	//Item stuff
	///////////////////////////////////////////////////////////////////////////
	BOOL AddItem(int ItemIndex, int SubItemIndex, LPCTSTR ItemText, int ImageIndex=-1);
	void DeleteSelectedItems(void);
	void HandleDeleteKey(BOOL bHandle = TRUE);
	void SelectItem(int nItem, BOOL bSelect);
	BOOL DeleteAllColumns(void);
	BOOL Reset(void);
	
	///////////////////////////////////////////////////////////////////////////
	//Sorting stuff
	///////////////////////////////////////////////////////////////////////////
	void SetColumnSorting(int nColumn, Sort eSort, Comparer eSortType = String);
	void SetColumnSorting(int nColumn, Sort eSort, PFNLVCOMPARE fnCallBack);
	BOOL SortOnColumn(int nColumn, BOOL bChangeOrder = FALSE);


protected:
	afx_msg BOOL OnNMDblclk(NMHDR *pNMHDR, LRESULT *pResult);
	virtual LRESULT WindowProc(UINT message, WPARAM wParam, LPARAM lParam);
	virtual void PreSubclassWindow();
	virtual BOOL PreCreateWindow(CREATESTRUCT& cs);
	virtual BOOL PreTranslateMessage(MSG* pMsg);
	afx_msg BOOL OnNMCustomdraw(NMHDR *pNMHDR, LRESULT *pResult);
	afx_msg void OnHdnItemclick(NMHDR *pNMHDR, LRESULT *pResult);

	int GetItemIndexFromData(DWORD_PTR dwData);

	CListCtrlEx::ColumnInfo* GetColumnInfo(int nColumn);
	CellInfo* GetCellInfo(int nItem, int nSubItem);
	BOOL SetCellData(int nItem, int nSubItem, DWORD_PTR dwData);
	DWORD_PTR GetCellData(int nRow, int nColumn);
	virtual BOOL OnAddNew(void){return FALSE;}
	BOOL m_bInvokeAddNew;
public:
	HACCEL m_hAccel;

};
