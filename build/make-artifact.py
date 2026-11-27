#!/usr/bin/env python3
"""Turns game/index.html into the body-only page used for the claude.ai artifact.
Usage: build/make-artifact.py game/index.html out.html"""
import re, sys
src = open(sys.argv[1], encoding='utf-8').read()
head = src[src.index('<title>'):src.index('</head>')]
head = re.sub(r'<link rel="(manifest|apple-touch-icon|icon)"[^>]*>\n?', '', head)
# the artifact is a single page: load the same fonts from Google Fonts instead of the bundled files
head = head.replace('<link rel="stylesheet" href="fonts/fonts.css">', '<link href="https://fonts.googleapis.com/css2?family=Rubik+Wet+Paint&family=Oswald:wght@400;500;600;700&family=Russo+One&display=swap" rel="stylesheet">')
assert 'fonts/fonts.css' not in head
body = src[src.index('<body>') + len('<body>'):src.index('</body>')]
body = re.sub(r"if \('serviceWorker' in navigator[^\n]*\n", '', body)
body = body.replace("<script>if (!window.THREE) document.write('<script src=\"three.min.js\"><\\/script>');</script>\n", '')
open(sys.argv[2], 'w', encoding='utf-8').write('<meta name="claude:viewport-fit-sides" content="cover">\n\n' + head + body)
