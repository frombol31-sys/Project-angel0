//go:build windows

package main

import (
	"os"
	"path/filepath"
	"syscall"
	"unsafe"

	webview "github.com/jchv/go-webview2"
)

var (
	user32            = syscall.NewLazyDLL("user32.dll")
	pGetWindowLongPtr = user32.NewProc("GetWindowLongPtrW")
	pSetWindowLongPtr = user32.NewProc("SetWindowLongPtrW")
	pGetWindowRect    = user32.NewProc("GetWindowRect")
	pSetWindowPos     = user32.NewProc("SetWindowPos")
	pMonitorFromWin   = user32.NewProc("MonitorFromWindow")
	pGetMonitorInfo   = user32.NewProc("GetMonitorInfoW")
	pShowWindow       = user32.NewProc("ShowWindow")
)

const (
	gwlStyle            = ^uintptr(15) // GWL_STYLE (-16)
	wsOverlappedWindow  = 0x00CF0000
	swpNoZOrder         = 0x0004
	swpNoOwnerZOrder    = 0x0200
	swpFrameChanged     = 0x0020
	monitorNearest      = 2
	swMaximize          = 3
)

type rect struct{ Left, Top, Right, Bottom int32 }
type monitorInfo struct {
	CbSize    uint32
	RcMonitor rect
	RcWork    rect
	DwFlags   uint32
}

// game window: borderless fullscreen toggle (F11 in the game)
type gameWindow struct {
	hwnd       uintptr
	fullscreen bool
	savedStyle uintptr
	savedRect  rect
}

func (g *gameWindow) toggleFullscreen() {
	if !g.fullscreen {
		g.savedStyle, _, _ = pGetWindowLongPtr.Call(g.hwnd, gwlStyle)
		pGetWindowRect.Call(g.hwnd, uintptr(unsafe.Pointer(&g.savedRect)))
		mon, _, _ := pMonitorFromWin.Call(g.hwnd, monitorNearest)
		mi := monitorInfo{CbSize: uint32(unsafe.Sizeof(monitorInfo{}))}
		pGetMonitorInfo.Call(mon, uintptr(unsafe.Pointer(&mi)))
		pSetWindowLongPtr.Call(g.hwnd, gwlStyle, g.savedStyle&^wsOverlappedWindow)
		r := mi.RcMonitor
		pSetWindowPos.Call(g.hwnd, 0, uintptr(r.Left), uintptr(r.Top), uintptr(r.Right-r.Left), uintptr(r.Bottom-r.Top),
			swpNoZOrder|swpNoOwnerZOrder|swpFrameChanged)
		g.fullscreen = true
	} else {
		pSetWindowLongPtr.Call(g.hwnd, gwlStyle, g.savedStyle)
		r := g.savedRect
		pSetWindowPos.Call(g.hwnd, 0, uintptr(r.Left), uintptr(r.Top), uintptr(r.Right-r.Left), uintptr(r.Bottom-r.Top),
			swpNoZOrder|swpNoOwnerZOrder|swpFrameChanged)
		g.fullscreen = false
	}
}

func runNative(url string) (ok bool) {
	defer func() {
		if recover() != nil {
			ok = false
		}
	}()
	dataDir := filepath.Join(os.Getenv("LOCALAPPDATA"), "GoreZone")
	w := webview.NewWithOptions(webview.WebViewOptions{
		AutoFocus: true,
		DataPath:  dataDir,
		WindowOptions: webview.WindowOptions{
			Title:  "GORE ZONE",
			Width:  1280,
			Height: 720,
			IconId: 2, // RT_GROUP_ICON 2 (1 is the manifest), see build-exe.sh
			Center: true,
		},
	})
	if w == nil {
		return false
	}
	defer w.Destroy()
	g := &gameWindow{hwnd: uintptr(w.Window())}
	w.Bind("gzToggleFullscreen", func() { g.toggleFullscreen() })
	w.Bind("gzQuit", func() { w.Terminate() })
	pShowWindow.Call(g.hwnd, swMaximize)
	g.toggleFullscreen() // games start fullscreen; F11 switches to a window
	w.Navigate(url)
	w.Run()
	return true
}
