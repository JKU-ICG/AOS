// Copyright (C) Microsoft Corporation. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#pragma once
#include "pch.h"
#include "ViewComponent.h"
#include "Dialog2Dlg.h"
#include <sstream>
#include <windowsx.h>
#include <WinUser.h>
#ifdef USE_WEBVIEW2_WIN10
#include <windows.ui.composition.interop.h>
#endif

//#include "CheckFailure.h"

using namespace Microsoft::WRL;
ViewComponent::ViewComponent(
    CDialog2Dlg* appWindow,
    IDCompositionDevice* dcompDevice,
#ifdef USE_WEBVIEW2_WIN10
    winrtComp::Compositor wincompCompositor,
#endif
    bool isDcompTargetMode)
    : m_appWindow(appWindow), m_controller(appWindow->GetWebViewController()),
    m_webView(appWindow->GetWebView()), m_dcompDevice(dcompDevice),
#ifdef USE_WEBVIEW2_WIN10
    m_wincompCompositor(wincompCompositor),
#endif
    m_isDcompTargetMode(isDcompTargetMode)
{

    m_controller->add_ZoomFactorChanged(
        Callback<ICoreWebView2ZoomFactorChangedEventHandler>(
            [this](ICoreWebView2Controller* sender, IUnknown* args) -> HRESULT {
                double zoomFactor;
                sender->get_ZoomFactor(&zoomFactor);
                //std::wstring message = L"WebView2APISample (Zoom: " +
                //    std::to_wstring(int(zoomFactor * 100)) + L"%)";
                ////SetWindowText(m_appWindow->GetMainWindow(), message.c_str());
                return S_OK;
            })
        .Get(),
                &m_zoomFactorChangedToken);

    ResizeWebView();
}
bool ViewComponent::HandleWindowMessage(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam, LRESULT* result)
{
    //! [ToggleIsVisibleOnMinimize]
    if (message == WM_SYSCOMMAND)
    {
        if (wParam == SC_MINIMIZE)
        {
            // Hide the webview when the app window is minimized.
            m_controller->put_IsVisible(FALSE);
        }
        else if (wParam == SC_RESTORE)
        {
            // When the app window is restored, show the webview
            // (unless the user has toggle visibility off).
            if (m_isVisible)
            {
                m_controller->put_IsVisible(TRUE);
            }
        }
    }
    //! [ToggleIsVisibleOnMinimize]
    if ((message >= WM_MOUSEFIRST && message <= WM_MOUSELAST) || message == WM_MOUSELEAVE)
    {
        OnMouseMessage(message, wParam, lParam);
    }

    //! [NotifyParentWindowPositionChanged]
    if (message == WM_MOVE || message == WM_MOVING)
    {
        m_controller->NotifyParentWindowPositionChanged();
        return true;
    }
    //! [NotifyParentWindowPositionChanged]
    return false;
}
//! [ToggleIsVisible]
void ViewComponent::ToggleVisibility()
{
    BOOL visible;
    m_controller->get_IsVisible(&visible);
    m_isVisible = !visible;
    m_controller->put_IsVisible(m_isVisible);
}
//! [ToggleIsVisible]

void ViewComponent::SetSizeRatio(float ratio)
{
    m_webViewRatio = ratio;
    ResizeWebView();
}

void ViewComponent::SetZoomFactor(float zoom)
{
    m_webViewZoomFactor = zoom;
    m_controller->put_ZoomFactor(zoom);
}

void ViewComponent::SetBounds(RECT bounds)
{
    m_webViewBounds = bounds;
    ResizeWebView();
}

//! [SetBoundsAndZoomFactor]
void ViewComponent::SetScale(float scale)
{
    RECT bounds;
    m_controller->get_Bounds(&bounds);
    double scaleChange = scale / m_webViewScale;

    bounds.bottom = LONG(
        (bounds.bottom - bounds.top) * scaleChange + bounds.top);
    bounds.right = LONG(
        (bounds.right - bounds.left) * scaleChange + bounds.left);

    m_webViewScale = scale;
    m_controller->SetBoundsAndZoomFactor(bounds, scale);
}
//! [SetBoundsAndZoomFactor]

//! [ResizeWebView]
// Update the bounds of the WebView window to fit available space.
void ViewComponent::ResizeWebView()
{
    SIZE webViewSize = {
            LONG((m_webViewBounds.right - m_webViewBounds.left) * m_webViewRatio * m_webViewScale),
            LONG((m_webViewBounds.bottom - m_webViewBounds.top) * m_webViewRatio * m_webViewScale) };

    RECT desiredBounds = m_webViewBounds;
    desiredBounds.bottom = LONG(
        webViewSize.cy + m_webViewBounds.top);
    desiredBounds.right = LONG(
        webViewSize.cx + m_webViewBounds.left);

    m_controller->put_Bounds(desiredBounds);
}
//! [ResizeWebView]

// Show the current bounds of the WebView.
void ViewComponent::ShowWebViewBounds()
{
    RECT bounds;
    HRESULT result = m_controller->get_Bounds(&bounds);
    if (SUCCEEDED(result))
    {
        std::wstringstream message;
        message << L"Left:\t" << bounds.left << L"\n"
            << L"Top:\t" << bounds.top << L"\n"
            << L"Right:\t" << bounds.right << L"\n"
            << L"Bottom:\t" << bounds.bottom << std::endl;
        //MessageBox(nullptr, message.str().c_str(), L"WebView Bounds", MB_OK);
    }
}

// Show the current zoom factor of the WebView.
void ViewComponent::ShowWebViewZoom()
{
    double zoomFactor;
    HRESULT result = m_controller->get_ZoomFactor(&zoomFactor);
    if (SUCCEEDED(result))
    {
        std::wstringstream message;
        message << L"Zoom Factor:\t" << zoomFactor << std::endl;
        //MessageBox(nullptr, message.str().c_str(), L"WebView Zoom Factor", MB_OK);
    }
}

void ViewComponent::SetTransform(TransformType transformType)
{
}

//! [SendMouseInput]
bool ViewComponent::OnMouseMessage(UINT message, WPARAM wParam, LPARAM lParam)
{
    // Manually relay mouse messages to the WebView
#ifdef USE_WEBVIEW2_WIN10
    if (m_dcompDevice || m_wincompCompositor)
#else
    if (m_dcompDevice)
#endif
    {
        POINT point;
        POINTSTOPOINT(point, lParam);
        if (message == WM_MOUSEWHEEL || message == WM_MOUSEHWHEEL)
        {
            // Mouse wheel messages are delivered in screen coordinates.
            // SendMouseInput expects client coordinates for the WebView, so convert
            // the point from screen to client.
            ::ScreenToClient(m_appWindow->GetMainWindow(), &point);
        }
        // Send the message to the WebView if the mouse location is inside the
        // bounds of the WebView, if the message is telling the WebView the
        // mouse has left the client area, or if we are currently capturing
        // mouse events.
        bool isMouseInWebView = PtInRect(&m_webViewBounds, point);
        if (isMouseInWebView || message == WM_MOUSELEAVE || m_isCapturingMouse)
        {
            DWORD mouseData = 0;

            switch (message)
            {
            case WM_MOUSEWHEEL:
            case WM_MOUSEHWHEEL:
                mouseData = GET_WHEEL_DELTA_WPARAM(wParam);
                break;
            case WM_XBUTTONDBLCLK:
            case WM_XBUTTONDOWN:
            case WM_XBUTTONUP:
                mouseData = GET_XBUTTON_WPARAM(wParam);
                break;
            case WM_MOUSEMOVE:
                if (!m_isTrackingMouse)
                {
                    // WebView needs to know when the mouse leaves the client area
                    // so that it can dismiss hover popups. TrackMouseEvent will
                    // provide a notification when the mouse leaves the client area.
                    TrackMouseEvents(TME_LEAVE);
                    m_isTrackingMouse = true;
                }
                break;
            case WM_MOUSELEAVE:
                m_isTrackingMouse = false;
                break;
            }

            // We need to capture the mouse in case the user drags the
            // mouse outside of the window bounds and we still need to send
            // mouse messages to the WebView process. This is useful for
            // scenarios like dragging the scroll bar or panning a map.
            // This is very similar to the Pointer Message case where a
            // press started inside of the WebView.
            if (message == WM_LBUTTONDOWN || message == WM_MBUTTONDOWN ||
                message == WM_RBUTTONDOWN || message == WM_XBUTTONDOWN)
            {
                if (isMouseInWebView && ::GetCapture() != m_appWindow->GetMainWindow())
                {
                    m_isCapturingMouse = true;
                    ::SetCapture(m_appWindow->GetMainWindow());
                }
            }
            else if (message == WM_LBUTTONUP || message == WM_MBUTTONUP ||
                message == WM_RBUTTONUP || message == WM_XBUTTONUP)
            {
                if (::GetCapture() == m_appWindow->GetMainWindow())
                {
                    m_isCapturingMouse = false;
                    ::ReleaseCapture();
                }
            }

            // Adjust the point from app client coordinates to webview client coordinates.
            // WM_MOUSELEAVE messages don't have a point, so don't adjust the point.
            if (message != WM_MOUSELEAVE)
            {
                point.x -= m_webViewBounds.left;
                point.y -= m_webViewBounds.top;
            }

            /*m_compositionController->SendMouseInput(
                static_cast<COREWEBVIEW2_MOUSE_EVENT_KIND>(message),
                static_cast<COREWEBVIEW2_MOUSE_EVENT_VIRTUAL_KEYS>(GET_KEYSTATE_WPARAM(wParam)),
                mouseData, point);*/
            return true;
        }
        else if (message == WM_MOUSEMOVE && m_isTrackingMouse)
        {
            // When the mouse moves outside of the WebView, but still inside the app
            // turn off mouse tracking and send the WebView a leave event.
            m_isTrackingMouse = false;
            TrackMouseEvents(TME_LEAVE | TME_CANCEL);
            OnMouseMessage(WM_MOUSELEAVE, 0, 0);
        }
    }
    return false;
}
//! [SendMouseInput]

bool ViewComponent::OnPointerMessage(UINT message, WPARAM wParam, LPARAM lParam)
{
    bool handled = false;
#ifdef USE_WEBVIEW2_WIN10
    if (m_dcompDevice || m_wincompCompositor)
#else
    if (m_dcompDevice)
#endif
    {
        POINT point;
        POINTSTOPOINT(point, lParam);
        // UINT pointerId = GET_POINTERID_WPARAM(wParam);

        ::ScreenToClient(m_appWindow->GetMainWindow(), &point);

        // bool pointerStartedInWebView = m_pointerIdsStartingInWebView.find(pointerId) !=  m_pointerIdsStartingInWebView.end();

    }
    return handled;
}

void ViewComponent::TrackMouseEvents(DWORD mouseTrackingFlags)
{
    TRACKMOUSEEVENT tme;
    tme.cbSize = sizeof(tme);
    tme.dwFlags = mouseTrackingFlags;
    tme.hwndTrack = m_appWindow->GetMainWindow();
    tme.dwHoverTime = 0;
    ::TrackMouseEvent(&tme);
}

void ViewComponent::BuildDCompTreeUsingVisual()
{

    if (m_dcompWebViewVisual == nullptr)
    {
        m_dcompDevice->CreateTargetForHwnd(
            m_appWindow->GetMainWindow(), TRUE, &m_dcompHwndTarget);
        m_dcompDevice->CreateVisual(&m_dcompRootVisual);
        m_dcompHwndTarget->SetRoot(m_dcompRootVisual.Get());
        m_dcompDevice->CreateVisual(&m_dcompWebViewVisual);
        m_dcompRootVisual->AddVisual(m_dcompWebViewVisual.Get(), TRUE, nullptr);
    }
}
//! [BuildDCompTree]

void ViewComponent::DestroyDCompVisualTree()
{
    if (m_dcompWebViewVisual)
    {
        m_dcompWebViewVisual->RemoveAllVisuals();
        m_dcompWebViewVisual.Reset();

        m_dcompRootVisual->RemoveAllVisuals();
        m_dcompRootVisual.Reset();

        m_dcompHwndTarget->SetRoot(nullptr);
        m_dcompHwndTarget.Reset();

        m_dcompDevice->Commit();
    }

    /*if (m_dcompTarget)
    {
        m_dcompTarget->RemoveOwnerRef();
        m_dcompTarget = nullptr;
    }*/
}

#ifdef USE_WEBVIEW2_WIN10
void ViewComponent::BuildWinCompVisualTree()
{
    namespace abiComp = ABI::Windows::UI::Composition;

    if (m_wincompWebViewVisual == nullptr)
    {
        auto interop = m_wincompCompositor.as<abiComp::Desktop::ICompositorDesktopInterop>();
        winrt::check_hresult(interop->CreateDesktopWindowTarget(
            m_appWindow->GetMainWindow(), false,
            reinterpret_cast<abiComp::Desktop::IDesktopWindowTarget**>(winrt::put_abi(m_wincompHwndTarget))));

        m_wincompRootVisual = m_wincompCompositor.CreateContainerVisual();
        m_wincompHwndTarget.Root(m_wincompRootVisual);

        m_wincompWebViewVisual = m_wincompCompositor.CreateContainerVisual();
        m_wincompRootVisual.Children().InsertAtTop(m_wincompWebViewVisual);
    }
}

void ViewComponent::DestroyWinCompVisualTree()
{
    if (m_wincompWebViewVisual != nullptr)
    {
        m_wincompWebViewVisual.Children().RemoveAll();
        m_wincompWebViewVisual = nullptr;

        m_wincompRootVisual.Children().RemoveAll();
        m_wincompRootVisual = nullptr;

        m_wincompHwndTarget.Root(nullptr);
        m_wincompHwndTarget = nullptr;
    }
}
#endif

ViewComponent::~ViewComponent()
{
    m_controller->remove_ZoomFactorChanged(m_zoomFactorChangedToken);
}
