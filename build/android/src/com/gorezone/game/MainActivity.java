package com.gorezone.game;

import android.app.Activity;
import android.os.Bundle;
import android.view.WindowManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient());
        setContentView(web);
        hideSystemUi();
        web.loadUrl("file:///android_asset/index.html");
    }

    private void hideSystemUi() {
        // immersive sticky: hide status bar and navigation bar
        getWindow().getDecorView().setSystemUiVisibility(0x1000 | 0x200 | 0x400 | 0x100 | 0x4 | 0x2);
    }

    @Override
    public void onWindowFocusChanged(boolean focus) {
        super.onWindowFocusChanged(focus);
        if (focus) hideSystemUi();
    }

    @Override
    protected void onPause() { super.onPause(); web.onPause(); }

    @Override
    protected void onResume() { super.onResume(); web.onResume(); hideSystemUi(); }

    @Override
    public void onBackPressed() {
        // Back pauses the game; in menus it closes the app
        web.evaluateJavascript("(game.state==='menu'||game.state==='pause')?'exit':(pauseGame(),'ok')", new ValueCallback<String>() {
            @Override
            public void onReceiveValue(String v) { if ("\"exit\"".equals(v)) finish(); }
        });
    }
}
