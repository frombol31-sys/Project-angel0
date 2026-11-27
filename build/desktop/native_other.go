//go:build !windows

package main

// runNative has no native window outside Windows; the browser fallback is used.
func runNative(url string) bool { return false }
