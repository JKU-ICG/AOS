// Copyright (C) Microsoft Corporation. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#pragma once

#include "pch.h"
#include "Dialog2Dlg.h"
#include <dcomp.h>
#include <unordered_set>
#ifdef USE_WEBVIEW2_WIN10
#include <winrt/Windows.UI.Composition.Desktop.h>
#endif

// This component handles commands from the View menu, as well as the ZoomFactorChanged
// event, and any functionality related to sizing and visibility of the WebView.
// It also manages interaction with the compositor if running in windowless mode.

class DCompTargetImpl;

class ViewComponent : public ComponentBase
{
    friend class DCompTargetImpl;

public:
    ViewComponent(
        CDialog2Dlg* appWindow,
        IDCompositionDevice* dcompDevice,
#ifdef USE_WEBVIEW2_WIN10
        winrtComp::Compositor wincompCompositor,
#endif
        bool isDCompTargetMode
    );

    bool HandleWindowMessage(
        HWND hWnd,
        UINT message,
        WPARAM wParam,
        LPARAM lParam,
        LRESULT* result) override;

    void SetBounds(RECT bounds);

    ~ViewComponent() override;

private:
    enum class TransformType
    {
        kIdentity = 0,
        kScale2X,
        kRotate30Deg,
        kRotate60DegDiagonally
    };
    void ResizeWebView();
    void ToggleVisibility();
    void SetSizeRatio(float ratio);
    void SetZoomFactor(float zoom);
    void SetScale(float scale);
    void SetTransform(TransformType transformType);
    void ShowWebViewBounds();
    void ShowWebViewZoom();

    //Browser* m_appWindow = nullptr;
    CDialog2Dlg* m_appWindow = nullptr;
    Microsoft::WRL::ComPtr<ICoreWebView2Controller> m_controller;
    Microsoft::WRL::ComPtr<ICoreWebView2> m_webView;
    
    bool m_isDcompTargetMode;
    bool m_isVisible = true;
    float m_webViewRatio = 1.0f;
    float m_webViewZoomFactor = 1.0f;
    RECT m_webViewBounds = {};
    float m_webViewScale = 1.0f;
    bool m_useCursorId = false;
    EventRegistrationToken m_zoomFactorChangedToken = {};

    bool OnMouseMessage(UINT message, WPARAM wParam, LPARAM lParam);
    bool OnPointerMessage(UINT message, WPARAM wParam, LPARAM lParam);
    void TrackMouseEvents(DWORD mouseTrackingFlags);
    bool m_isTrackingMouse = false;
    bool m_isCapturingMouse = false;
    std::unordered_set<UINT> m_pointerIdsStartingInWebView;

    void BuildDCompTreeUsingVisual();
    void DestroyDCompVisualTree();

    Microsoft::WRL::ComPtr<IDCompositionDevice> m_dcompDevice;
    Microsoft::WRL::ComPtr<IDCompositionTarget> m_dcompHwndTarget;
    Microsoft::WRL::ComPtr<IDCompositionVisual> m_dcompRootVisual;
    Microsoft::WRL::ComPtr<IDCompositionVisual> m_dcompWebViewVisual;

#ifdef USE_WEBVIEW2_WIN10
    void BuildWinCompVisualTree();
    void DestroyWinCompVisualTree();

    winrt::Windows::UI::Composition::Compositor m_wincompCompositor{ nullptr };
    winrt::Windows::UI::Composition::Desktop::DesktopWindowTarget m_wincompHwndTarget{ nullptr };
    winrt::Windows::UI::Composition::ContainerVisual m_wincompRootVisual{ nullptr };
    winrt::Windows::UI::Composition::ContainerVisual m_wincompWebViewVisual{ nullptr };
#endif


    EventRegistrationToken m_cursorChangedToken = {};
};
