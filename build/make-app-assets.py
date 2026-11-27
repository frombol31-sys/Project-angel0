# Builds the offline game page used by the APK and EXE: three.js is loaded from the local file.
import re, shutil, sys, os
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
s = open(os.path.join(src, 'index.html')).read()
s = s.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n', '')
s = s.replace("""<script>if (!window.THREE) document.write('<script src="three.min.js"><\\/script>');</script>""", '<script src="three.min.js"></script>')
assert 'cdnjs' not in s and '<script src="three.min.js"></script>' in s
s = re.sub(r'<link rel="manifest"[^>]*>\n', '', s)
open(os.path.join(out, 'index.html'), 'w').write(s)
for f in ['three.min.js', 'icon-192.png', 'icon-512.png']:
    shutil.copy(os.path.join(src, f), out)
