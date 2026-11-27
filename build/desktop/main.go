// GORE ZONE desktop launcher.
// Serves the embedded game on 127.0.0.1 and shows it in a native game window
// (Windows: WebView2, see native_windows.go). If the native window cannot be
// created, the game opens in Edge/Chrome app mode or the default browser instead.
package main

import (
	"embed"
	"io/fs"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

//go:embed web
var webFS embed.FS

func startServer() string {
	sub, _ := fs.Sub(webFS, "web")
	// a fixed port keeps the same origin, so settings and records survive between launches
	ln, err := net.Listen("tcp", "127.0.0.1:47613")
	if err != nil {
		if ln, err = net.Listen("tcp", "127.0.0.1:0"); err != nil {
			return ""
		}
	}
	go http.Serve(ln, http.FileServer(http.FS(sub)))
	return "http://" + ln.Addr().String() + "/"
}

func findBrowser() string {
	var cands []string
	if runtime.GOOS == "windows" {
		for _, env := range []string{"ProgramFiles(x86)", "ProgramFiles", "LocalAppData"} {
			base := os.Getenv(env)
			if base == "" {
				continue
			}
			cands = append(cands,
				filepath.Join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
				filepath.Join(base, "Google", "Chrome", "Application", "chrome.exe"))
		}
	} else {
		cands = []string{"/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/microsoft-edge"}
	}
	for _, c := range cands {
		if st, err := os.Stat(c); err == nil && !st.IsDir() {
			return c
		}
	}
	return ""
}

func browserFallback(url string) {
	if b := findBrowser(); b != "" {
		profile := filepath.Join(os.TempDir(), "GoreZoneProfile")
		if d, err := os.UserConfigDir(); err == nil {
			profile = filepath.Join(d, "GoreZone")
		}
		cmd := exec.Command(b, "--app="+url, "--user-data-dir="+profile, "--start-fullscreen",
			"--no-first-run", "--no-default-browser-check")
		if err := cmd.Start(); err == nil {
			cmd.Wait()
			return
		}
	}
	if runtime.GOOS == "windows" {
		exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	} else {
		exec.Command("xdg-open", url).Start()
	}
	select {}
}

func main() {
	url := startServer()
	if url == "" {
		return
	}
	if os.Getenv("GOREZONE_SERVE_ONLY") != "" {
		select {}
	}
	if runNative(url) {
		return
	}
	browserFallback(url)
}
