package com.gorezone.game;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.view.DisplayCutout;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.window.OnBackInvokedCallback;
import android.window.OnBackInvokedDispatcher;

public class MainActivity extends Activity {
    private WebView web;
    private FrameLayout root;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        root = new FrameLayout(this);
        root.setBackgroundColor(0xFF0B0A0B);
        setContentView(root);
        if (Build.VERSION.SDK_INT >= 28) {
            // Android 15+ draws edge-to-edge: keep the game clear of the camera cutout
            root.setOnApplyWindowInsetsListener(new View.OnApplyWindowInsetsListener() {
                @android.annotation.TargetApi(28) @Override public WindowInsets onApplyWindowInsets(View v, WindowInsets in) {
                    DisplayCutout c = in.getDisplayCutout();
                    v.setPadding(c == null ? 0 : c.getSafeInsetLeft(), c == null ? 0 : c.getSafeInsetTop(),
                        c == null ? 0 : c.getSafeInsetRight(), c == null ? 0 : c.getSafeInsetBottom());
                    return in;
                }
            });
        }
        createWebView();
        hideSystemUi();
        if (Build.VERSION.SDK_INT >= 33) {
            // Android 13+ (and required on Android 16): predictive back instead of onBackPressed
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT,
                new OnBackInvokedCallback() { @Override public void onBackInvoked() { handleBack(); } });
        }
    }

    // no lambdas: the class also builds with the plain dx toolchain (build/build-apk36.sh)
    private void createWebView() {
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            // if the renderer crashes or is killed for memory, rebuild the page instead of killing the app
            @android.annotation.TargetApi(26) @Override public boolean onRenderProcessGone(WebView v, RenderProcessGoneDetail d) {
                if (v.getParent() instanceof ViewGroup) ((ViewGroup) v.getParent()).removeView(v);
                v.destroy();
                if (v == web) { web = null; createWebView(); }
                return true;
            }
        });
        root.addView(web, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        web.loadUrl("file:///android_asset/index.html");
    }

    // Back steps back through the game's screens (window.gzBack); only the main menu closes the app
    private void handleBack() {
        if (web == null) { finish(); return; }
        web.evaluateJavascript("(function(){try{return window.gzBack?gzBack():'exit'}catch(e){return 'exit'}})()",
            new ValueCallback<String>() {
                @Override public void onReceiveValue(String v) { if ("\"exit\"".equals(v)) finish(); }
            });
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        if (Build.VERSION.SDK_INT < 33) handleBack();
        else super.onBackPressed();
    }

    @SuppressWarnings("deprecation")
    private void hideSystemUi() {
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                c.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
        } else {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean focus) {
        super.onWindowFocusChanged(focus);
        if (focus) hideSystemUi();
    }

    @Override
    protected void onPause() { super.onPause(); if (web != null) web.onPause(); }

    @Override
    protected void onResume() { super.onResume(); if (web != null) web.onResume(); hideSystemUi(); }

    @Override
    protected void onDestroy() { if (web != null) { root.removeView(web); web.destroy(); web = null; } super.onDestroy(); }
}
