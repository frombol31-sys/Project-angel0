// GORE ZONE desktop launcher.
// Serves the embedded game files on 127.0.0.1 and opens them in an app window
// (Microsoft Edge or Google Chrome in --app mode); falls back to the default browser.
// Closing the game window stops the launcher.
package main

import (
	"embed"
	"fmt"
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

func openDefault(url string) error {
	if runtime.GOOS == "windows" {
		return exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	}
	return exec.Command("xdg-open", url).Start()
}

func main() {
	sub, _ := fs.Sub(webFS, "web")
	// a fixed port keeps the same origin, so settings and records survive between launches
	ln, err := net.Listen("tcp", "127.0.0.1:47613")
	if err != nil {
		if ln, err = net.Listen("tcp", "127.0.0.1:0"); err != nil {
			fmt.Println("Не удалось запустить игру:", err)
			return
		}
	}
	go http.Serve(ln, http.FileServer(http.FS(sub)))
	url := "http://" + ln.Addr().String() + "/"
	fmt.Println("GORE ZONE запущена:", url)
	fmt.Println("Закрой окно игры, чтобы выйти.")

	if os.Getenv("GOREZONE_SERVE_ONLY") != "" {
		select {}
	}
	if b := findBrowser(); b != "" {
		profile := filepath.Join(os.TempDir(), "GoreZoneProfile")
		if d, err := os.UserConfigDir(); err == nil {
			profile = filepath.Join(d, "GoreZone")
		}
		cmd := exec.Command(b, "--app="+url, "--user-data-dir="+profile, "--window-size=1280,720",
			"--no-first-run", "--no-default-browser-check")
		if err := cmd.Start(); err == nil {
			cmd.Wait()
			return
		}
	}
	openDefault(url)
	fmt.Println("Игра открыта в браузере. Не закрывай это окно, пока играешь.")
	select {}
}
