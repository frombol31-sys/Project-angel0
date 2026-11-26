"""Плоское вертикальное (9:16) видео про бешенство с человечками.

Рендер: pycairo -> сырые кадры -> ffmpeg. Музыка синтезируется numpy.
Запуск:  python3 render.py   (результат: rabies_9x16.mp4)
"""
import math, os, subprocess, sys, wave
from multiprocessing import Pool
import numpy as np
import cairo

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "rabies_9x16.mp4")
FONT = "DejaVu Sans"

# ---------- палитра ----------
def hexc(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
NAVY, CREAM, TEAL, CORAL = hexc("1f2a44"), hexc("fff4e0"), hexc("2ec4b6"), hexc("ff6b6b")
YELLOW, ORANGE, PURPLE, GREEN = hexc("ffd166"), hexc("f4a261"), hexc("7b61ff"), hexc("06d6a0")
WHITE, INK, SKIN, BROWN = hexc("ffffff"), hexc("1f2a44"), hexc("ffd6b0"), hexc("a0684a")
BLUE, GREY, RED, SKY = hexc("4d96ff"), hexc("8d99ae"), hexc("e63946"), hexc("bde0fe")

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, start, dur): return clamp((t - start) / dur)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 3*x*x - 2*x*x*x
def back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, x): return a + (b - a) * x
def lerpc(c1, c2, x): return tuple(lerp(a, b, x) for a, b in zip(c1, c2))

# ---------- примитивы ----------
def col(ctx, c, a=1.0): ctx.set_source_rgba(c[0], c[1], c[2], a)

def rrect(ctx, x, y, w, h, r):
    r = min(r, w/2, h/2)
    ctx.new_sub_path()
    ctx.arc(x+w-r, y+r, r, -math.pi/2, 0); ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi); ctx.arc(x+r, y+r, r, math.pi, 1.5*math.pi)
    ctx.close_path()

def circle(ctx, x, y, r, c, a=1.0):
    ctx.arc(x, y, r, 0, 2*math.pi); col(ctx, c, a); ctx.fill()

def line(ctx, x1, y1, x2, y2, w, c, a=1.0):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w)
    ctx.move_to(x1, y1); ctx.line_to(x2, y2); col(ctx, c, a); ctx.stroke()

class Pop:
    """Контекст: масштаб+прозрачность вокруг точки (появление «с пружинкой»)."""
    def __init__(self, ctx, x, y, k, alpha=None):
        self.ctx, self.x, self.y, self.k = ctx, x, y, k
        self.alpha = clamp(k * 1.5) if alpha is None else alpha
    def __enter__(self):
        c = self.ctx; c.save(); c.push_group()
        c.translate(self.x, self.y); s = max(back(self.k), 0.0001) if self.k < 1 else 1
        c.scale(s, s); c.translate(-self.x, -self.y); return c
    def __exit__(self, *a):
        c = self.ctx; c.pop_group_to_source(); c.paint_with_alpha(self.alpha); c.restore()

def text(ctx, s, x, y, size, c, bold=True, align="center", a=1.0):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    if align == "center": tx = x - ext.x_advance / 2
    elif align == "right": tx = x - ext.x_advance
    else: tx = x
    ctx.move_to(tx, y); col(ctx, c, a); ctx.show_text(s)
    return ext.x_advance

def wrap(ctx, s, size, maxw, bold=True):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    lines, cur = [], ""
    for wd in s.split():
        test = (cur + " " + wd).strip()
        if ctx.text_extents(test).x_advance <= maxw or not cur: cur = test
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def para(ctx, s, x, y, size, c, maxw=900, bold=True, lh=1.25, a=1.0):
    for i, ln in enumerate(wrap(ctx, s, size, maxw, bold)):
        text(ctx, ln, x, y + i * size * lh, size, c, bold, a=a)

def title(ctx, s, t, y=260, c=WHITE, size=92, start=0.0):
    k = ease_out(prog(t, start, 0.5))
    text(ctx, s, W/2, y + (1-k) * 60, size, c, a=k)

def caption(ctx, s, t, start, y=1560, c=INK, bg=WHITE, size=54):
    k = prog(t, start, 0.5)
    if k <= 0: return
    lines = wrap(ctx, s, size, 860)
    h = len(lines) * size * 1.3 + 70
    with Pop(ctx, W/2, y + h/2, k):
        col(ctx, (0, 0, 0), 0.15); rrect(ctx, 70, y + 12, W - 140, h, 44); ctx.fill()
        col(ctx, bg); rrect(ctx, 70, y, W - 140, h, 44); ctx.fill()
        for i, ln in enumerate(lines):
            text(ctx, ln, W/2, y + 35 + size + i * size * 1.3 - 8, size, c)

# ---------- персонажи ----------
def person(ctx, x, y, s=1.0, shirt=BLUE, pants=NAVY, skin=SKIN, arm_l=20, arm_r=20,
           leg=0.0, face="happy", bob=0.0, hair=BROWN, flip=False):
    """Человечек. (x,y) — точка между ступнями. Углы рук в градусах от вертикали (наружу)."""
    ctx.save(); ctx.translate(x, y + bob); ctx.scale(-s if flip else s, s)
    lw = 26
    # ноги
    for side in (-1, 1):
        sw = math.sin(leg) * 22 * side
        line(ctx, side*18, -120, side*24 + sw, 0, lw, pants)
    # туловище
    col(ctx, shirt); rrect(ctx, -46, -250, 92, 140, 34); ctx.fill()
    # руки
    for side, ang in ((-1, arm_l), (1, arm_r)):
        a = math.radians(ang)
        sx, sy = side*38, -232
        ex, ey = sx + side*math.sin(a)*105, sy + math.cos(a)*105
        line(ctx, sx, sy, ex, ey, lw, shirt)
        circle(ctx, ex, ey, 15, skin)
    # голова
    hx, hy = 0, -305
    circle(ctx, hx, hy, 52, skin)
    ctx.arc(hx, hy - 6, 54, math.pi*1.05, math.pi*1.95); col(ctx, hair); ctx.fill()
    # лицо
    if face == "sick":
        line(ctx, -26, -312, -10, -304, 7, INK); line(ctx, 26, -312, 10, -304, 7, INK)
    elif face == "scared":
        circle(ctx, -18, -308, 9, WHITE); circle(ctx, 18, -308, 9, WHITE)
        circle(ctx, -18, -308, 5, INK); circle(ctx, 18, -308, 5, INK)
    else:
        circle(ctx, -18, -308, 6.5, INK); circle(ctx, 18, -308, 6.5, INK)
    if face == "happy":
        ctx.set_line_width(6); ctx.arc(0, -292, 16, 0.15*math.pi, 0.85*math.pi); col(ctx, INK); ctx.stroke()
        circle(ctx, -32, -290, 8, CORAL, 0.5); circle(ctx, 32, -290, 8, CORAL, 0.5)
    elif face == "sad" or face == "sick":
        ctx.set_line_width(6); ctx.arc(0, -270, 14, 1.2*math.pi, 1.8*math.pi); col(ctx, INK); ctx.stroke()
    elif face == "scared":
        ctx.save(); ctx.translate(0, -280); ctx.scale(1, 1.3); ctx.arc(0, 0, 9, 0, 2*math.pi); ctx.restore()
        col(ctx, INK); ctx.fill()
    elif face == "angry":
        line(ctx, -30, -322, -8, -314, 6, INK); line(ctx, 30, -322, 8, -314, 6, INK)
        line(ctx, -14, -280, 14, -280, 6, INK)
    ctx.restore()

def dog(ctx, x, y, s=1.0, c=ORANGE, flip=False, leg=0.0, mouth=0.0, angry=False,
        tail=0.0, fox=False, foam=False):
    ctx.save(); ctx.translate(x, y); ctx.scale(-s if flip else s, s)
    dark = tuple(v*0.8 for v in c)
    # хвост
    ta = math.sin(tail) * 0.4
    ctx.save(); ctx.translate(-95, -120); ctx.rotate(-0.9 + ta)
    if fox:
        ctx.save(); ctx.scale(1, 0.45); ctx.arc(-55, 0, 55, 0, 2*math.pi); ctx.restore(); col(ctx, c); ctx.fill()
        ctx.save(); ctx.scale(1, 0.45); ctx.arc(-95, 0, 20, 0, 2*math.pi); ctx.restore(); col(ctx, WHITE); ctx.fill()
    else:
        line(ctx, 0, 0, -70, 0, 20, c)
    ctx.restore()
    # ноги
    for i, lx in enumerate((-70, -40, 45, 75)):
        sw = math.sin(leg + i * math.pi) * 14
        line(ctx, lx, -80, lx + sw, 0, 20, dark if i % 2 else c)
    # тело
    col(ctx, c); rrect(ctx, -110, -165, 220, 100, 50); ctx.fill()
    # голова
    hx, hy = 110, -175
    if fox:
        ctx.move_to(hx-35, hy-30); ctx.line_to(hx-20, hy-95); ctx.line_to(hx+5, hy-40); ctx.close_path()
        ctx.move_to(hx+10, hy-40); ctx.line_to(hx+40, hy-95); ctx.line_to(hx+45, hy-30); ctx.close_path()
        col(ctx, dark); ctx.fill()
    circle(ctx, hx, hy, 58, c)
    # морда
    col(ctx, WHITE if fox else tuple(min(1, v*1.15) for v in c))
    rrect(ctx, hx + 10, hy - 10, 85, 50 + mouth*20, 24); ctx.fill()
    circle(ctx, hx + 92, hy + 2, 12, INK)
    if mouth > 0:
        col(ctx, RED); rrect(ctx, hx + 30, hy + 30, 60, 10 + mouth*28, 8); ctx.fill()
        for tx in (40, 58, 76):
            ctx.move_to(hx+tx, hy+30); ctx.line_to(hx+tx+7, hy+30+12*mouth); ctx.line_to(hx+tx+14, hy+30)
            col(ctx, WHITE); ctx.fill()
    if not fox:
        ctx.save(); ctx.translate(hx - 30, hy - 30); ctx.rotate(0.5)
        ctx.scale(0.55, 1); ctx.arc(0, 30, 42, 0, 2*math.pi); ctx.restore(); col(ctx, dark); ctx.fill()
    # глаз
    circle(ctx, hx + 18, hy - 18, 9, INK)
    if angry: line(ctx, hx + 2, hy - 42, hx + 34, hy - 30, 8, INK)
    if foam:
        for fx, fy, r in ((hx+40, hy+48, 10), (hx+58, hy+56, 13), (hx+78, hy+50, 9)):
            circle(ctx, fx, fy + mouth*20, r, WHITE)
    ctx.restore()

def cat(ctx, x, y, s=1.0, c=GREY):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(18)
    ctx.move_to(60, -40); ctx.curve_to(120, -60, 110, -150, 80, -160); col(ctx, c); ctx.stroke()
    ctx.save(); ctx.scale(1, 1.1); ctx.arc(0, -55, 62, 0, 2*math.pi); ctx.restore(); col(ctx, c); ctx.fill()
    for sx in (-1, 1):
        ctx.move_to(sx*20, -165); ctx.line_to(sx*55, -215); ctx.line_to(sx*58, -150); ctx.close_path(); ctx.fill()
    circle(ctx, 0, -150, 52, c)
    circle(ctx, -18, -155, 8, INK); circle(ctx, 18, -155, 8, INK)
    ctx.move_to(-7, -138); ctx.line_to(7, -138); ctx.line_to(0, -130); ctx.close_path(); col(ctx, CORAL); ctx.fill()
    for sy in (-135, -125):
        line(ctx, 20, sy, 62, sy - 4, 3, INK); line(ctx, -20, sy, -62, sy - 4, 3, INK)
    ctx.restore()

def bat(ctx, x, y, s=1.0, flap=0.0, c=PURPLE):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    f = math.sin(flap) * 25
    for sx in (-1, 1):
        ctx.move_to(sx*20, -10)
        ctx.curve_to(sx*80, -70 - f, sx*140, -60 - f, sx*170, -20 - f)
        ctx.curve_to(sx*140, -10, sx*120, 10, sx*110, 30)
        ctx.curve_to(sx*90, 10, sx*70, 15, sx*55, 35)
        ctx.curve_to(sx*45, 15, sx*30, 15, sx*20, 25)
        ctx.close_path(); col(ctx, c); ctx.fill()
    ctx.save(); ctx.scale(1, 1.2); ctx.arc(0, 0, 40, 0, 2*math.pi); ctx.restore(); col(ctx, c); ctx.fill()
    for sx in (-1, 1):
        ctx.move_to(sx*10, -35); ctx.line_to(sx*30, -75); ctx.line_to(sx*35, -25); ctx.close_path(); ctx.fill()
    circle(ctx, -14, -8, 7, YELLOW); circle(ctx, 14, -8, 7, YELLOW)
    for sx in (-8, 8):
        ctx.move_to(sx-4, 16); ctx.line_to(sx, 28); ctx.line_to(sx+4, 16); col(ctx, WHITE); ctx.fill()
    ctx.restore()

def raccoon(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    g, dg = hexc("9aa5b1"), hexc("4a5568")
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(5):
        ctx.set_line_width(30); a = -0.6 + i * 0.0
        line(ctx, 55 + i*12, -40 - i*18, 67 + i*12, -58 - i*18, 30, dg if i % 2 else g)
    ctx.save(); ctx.scale(1, 1.05); ctx.arc(0, -55, 62, 0, 2*math.pi); ctx.restore(); col(ctx, g); ctx.fill()
    for sx in (-1, 1): circle(ctx, sx*40, -195, 22, g)
    circle(ctx, 0, -150, 56, g)
    col(ctx, dg); rrect(ctx, -50, -172, 100, 34, 17); ctx.fill()
    circle(ctx, -20, -155, 8, WHITE); circle(ctx, 20, -155, 8, WHITE)
    circle(ctx, -20, -155, 4, INK); circle(ctx, 20, -155, 4, INK)
    circle(ctx, 0, -125, 9, INK)
    ctx.restore()

def virus(ctx, x, y, r, c=GREEN, rot=0.0, face=True, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    dark = tuple(v*0.75 for v in c)
    for i in range(10):
        ang = i * 2*math.pi/10
        line(ctx, 0, 0, math.cos(ang)*r*1.35, math.sin(ang)*r*1.35, r*0.16, dark, a)
        circle(ctx, math.cos(ang)*r*1.4, math.sin(ang)*r*1.4, r*0.17, dark, a)
    circle(ctx, 0, 0, r, c, a)
    for dx, dy, rr in ((0.35, -0.3, 0.16), (-0.4, 0.3, 0.12), (0.2, 0.45, 0.1)):
        circle(ctx, dx*r, dy*r, rr*r, dark, a*0.6)
    ctx.restore()
    if face and r > 30:
        circle(ctx, x - r*0.3, y - r*0.1, r*0.12, INK, a); circle(ctx, x + r*0.3, y - r*0.1, r*0.12, INK, a)
        line(ctx, x - r*0.48, y - r*0.38, x - r*0.15, y - r*0.25, r*0.08, INK, a)
        line(ctx, x + r*0.48, y - r*0.38, x + r*0.15, y - r*0.25, r*0.08, INK, a)
        ctx.set_line_width(r*0.08); ctx.arc(x, y + r*0.4, r*0.25, 1.15*math.pi, 1.85*math.pi)
        col(ctx, INK, a); ctx.stroke()

def ground(ctx, y, c, a=1.0):
    col(ctx, c, a); ctx.rectangle(0, y, W, H - y); ctx.fill()

def badge(ctx, x, y, r, c, label, size=44, tc=WHITE):
    circle(ctx, x, y, r, c); text(ctx, label, x, y + size*0.36, size, tc)

def syringe(ctx, x, y, s=1.0, rot=-0.6, c=BLUE):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    col(ctx, WHITE); rrect(ctx, -110, -30, 170, 60, 14); ctx.fill()
    col(ctx, c); rrect(ctx, -110, -30, 110, 60, 14); ctx.fill()
    for i in range(4): line(ctx, -90 + i*35, -30, -90 + i*35, -12, 5, INK)
    col(ctx, GREY); ctx.rectangle(60, -10, 30, 20); ctx.fill()
    line(ctx, 90, 0, 160, 0, 6, GREY)
    col(ctx, GREY); ctx.rectangle(-140, -8, 30, 16); ctx.fill()
    col(ctx, NAVY); rrect(ctx, -160, -40, 22, 80, 8); ctx.fill()
    ctx.restore()

def check(ctx, x, y, s, c=GREEN):
    circle(ctx, x, y, 40*s, c)
    ctx.set_line_width(10*s); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x - 18*s, y); ctx.line_to(x - 4*s, y + 15*s); ctx.line_to(x + 20*s, y - 14*s); col(ctx, WHITE); ctx.stroke()

def cross(ctx, x, y, s, c=RED):
    circle(ctx, x, y, 40*s, c)
    line(ctx, x - 16*s, y - 16*s, x + 16*s, y + 16*s, 10*s, WHITE)
    line(ctx, x + 16*s, y - 16*s, x - 16*s, y + 16*s, 10*s, WHITE)

# ---------- сцены ----------
def sc_title(ctx, t, d):
    for i in range(14):  # фоновые вирусы
        px = (i * 197 + 80) % W; py = ((i * 331) % H + t * (30 + i*5)) % (H + 200) - 100
        virus(ctx, px, py, 18 + (i % 3) * 8, hexc("2b3a5c"), rot=t*0.5 + i, face=False)
    k = prog(t, 0.1, 0.8)
    with Pop(ctx, W/2, 760, k):
        virus(ctx, W/2, 760 + math.sin(t*3)*15, 170, GREEN, rot=t*0.4)
    k = prog(t, 0.7, 0.6)
    with Pop(ctx, W/2, 1180, k):
        text(ctx, "БЕШЕНСТВО", W/2, 1210, 130, YELLOW)
    k = ease_out(prog(t, 1.3, 0.6))
    text(ctx, "что важно знать каждому", W/2, 1320 + (1-k)*40, 54, WHITE, bold=False, a=k)
    k = prog(t, 2.0, 0.5)
    with Pop(ctx, W/2, 1500, k):
        col(ctx, CORAL); rrect(ctx, W/2 - 270, 1450, 540, 100, 50); ctx.fill()
        text(ctx, "смотри до конца ↓", W/2, 1515, 44, WHITE)

def sc_what(ctx, t, d):
    title(ctx, "Что это?", t)
    ground(ctx, 1380, hexc("e9dcc3"))
    k = prog(t, 0.2, 0.6)
    with Pop(ctx, 540, 1380, k):
        person(ctx, 540, 1380, 2.0, shirt=TEAL, face="sad" if t > 3 else "happy", arm_l=15, arm_r=15,
               bob=math.sin(t*4)*4)
    # мозг пульсирует красным
    if t > 1.2:
        pa = 0.5 + 0.5*math.sin(t*8)
        circle(ctx, 540, 1380 - 610, 70 + pa*14, RED, 0.25 + 0.2*pa)
    for i in range(6):
        kk = prog(t, 1.0 + i*0.25, 0.5)
        if kk <= 0: continue
        ang = t*1.4 + i * math.pi/3; rr = 210 - kk*60
        with Pop(ctx, 540 + math.cos(ang)*rr, 770 + math.sin(ang)*rr, kk):
            virus(ctx, 540 + math.cos(ang)*rr, 770 + math.sin(ang)*rr, 26, GREEN, rot=t*2, face=False)
    caption(ctx, "Вирус поражает мозг и нервную систему", t, 0.8, y=380, size=56)
    k = prog(t, 3.2, 0.5)
    with Pop(ctx, W/2, 1610, k):
        col(ctx, RED); rrect(ctx, 70, 1460, W-140, 300, 44); ctx.fill()
        n = int(lerp(0, 100, ease_out(prog(t, 3.3, 1.2))))
        text(ctx, f"≈{n}%", W/2, 1590, 120, WHITE)
        text(ctx, "смертельно, если уже появились", W/2, 1670, 40, WHITE)
        text(ctx, "симптомы", W/2, 1720, 40, WHITE)

def sc_bite(ctx, t, d):
    title(ctx, "Как заражаются?", t, c=INK)
    ground(ctx, 1250, hexc("b7e4c7"))
    # сцена: человек идёт слева, собака бежит справа
    bite_t = 2.6
    walk = ease_in_out(prog(t, 0.0, bite_t))
    px = lerp(-150, 430, walk)
    dx = lerp(1250, 640, ease_in_out(prog(t, 0.6, bite_t - 0.6)))
    after = t > bite_t
    shake = math.sin(t*60) * 10 * clamp(1 - (t - bite_t)/0.6) if after else 0
    person(ctx, px + shake, 1250, 1.45, shirt=BLUE, leg=t*9 if not after else 0,
           face="scared" if after else "happy", arm_l=25 if not after else 150, arm_r=25 if not after else 140)
    dog(ctx, dx, 1250, 1.1, c=hexc("8d6e63"), flip=True, leg=t*12 if not after else t*3,
        mouth=0.5 + 0.5*math.sin(t*10), angry=True, foam=True)
    if after:
        k = prog(t, bite_t, 0.4)
        with Pop(ctx, 470, 980, k):
            # вспышка-звезда
            ctx.save(); ctx.translate(470, 960); ctx.rotate(0.2)
            ctx.move_to(0, -120)
            for i in range(1, 16):
                r = 120 if i % 2 == 0 else 60; a = i * math.pi/8 - math.pi/2
                ctx.line_to(math.cos(a)*r, math.sin(a)*r + 120 - 120)
            ctx.close_path(); col(ctx, YELLOW); ctx.fill(); ctx.restore()
            text(ctx, "КУСЬ!", 470, 985, 64, RED)
        # капли слюны
        for i in range(5):
            kk = prog(t, bite_t + 0.2 + i*0.15, 1.2)
            if 0 < kk < 1:
                circle(ctx, 560 + i*25, 1080 + kk*160, 12, SKY, 1 - kk)
    caption(ctx, "Через слюну больного животного: укус, царапина, слюна на ране или слизистой",
            t, bite_t + 0.8, y=1390, size=50)

def sc_carriers(ctx, t, d):
    title(ctx, "Кто переносит?", t)
    items = [
        ("Собаки", lambda x, y, k: dog(ctx, x + 20, y, 0.75, c=hexc("c08552"), tail=t*12)),
        ("Лисы", lambda x, y, k: dog(ctx, x + 20, y, 0.75, c=hexc("ef6c00"), fox=True, tail=t*6)),
        ("Кошки", lambda x, y, k: cat(ctx, x, y, 1.0)),
        ("Летучие мыши", lambda x, y, k: bat(ctx, x, y - 110 + math.sin(t*4)*12, 0.85, flap=t*14)),
        ("Еноты, волки", lambda x, y, k: raccoon(ctx, x, y, 1.0)),
    ]
    pos = [(290, 760), (790, 760), (290, 1180), (790, 1180), (540, 1580)]
    for i, ((name, fn), (x, y)) in enumerate(zip(items, pos)):
        k = prog(t, 0.4 + i*0.45, 0.5)
        if k <= 0: continue
        with Pop(ctx, x, y - 120, k):
            col(ctx, (0, 0, 0), 0.15); rrect(ctx, x - 220, y - 300 + 12, 440, 380, 40); ctx.fill()
            col(ctx, WHITE); rrect(ctx, x - 220, y - 300, 440, 380, 40); ctx.fill()
            ctx.save(); ctx.rectangle(x - 220, y - 300, 440, 300); ctx.clip()
            fn(x, y - 20, k); ctx.restore()
            text(ctx, name, x, y + 50, 44, INK)

def sc_path(ctx, t, d):
    title(ctx, "Путь вируса", t, c=INK)
    cx, gy, s = 540, 1450, 2.3
    person(ctx, cx, gy, s, shirt=hexc("cdd5e0"), pants=hexc("aab4c3"), skin=hexc("e6ebf2"),
           hair=hexc("cdd5e0"), arm_l=20, arm_r=55, face="happy" if t < 3.5 else "sick")
    # координаты: кисть правой руки -> плечо -> шея -> мозг
    a = math.radians(55)
    hand = (cx + s*(38 + math.sin(a)*105), gy + s*(-232 + math.cos(a)*105))
    shoulder = (cx + s*38, gy + s*-232)
    neck = (cx, gy + s*-255)
    brain = (cx, gy + s*-318)
    pts = [hand, shoulder, neck, brain]
    # нерв
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(10); ctx.set_dash([4, 18])
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    col(ctx, PURPLE, 0.7); ctx.stroke(); ctx.set_dash([])
    # укус на кисти
    k = prog(t, 0.3, 0.4)
    with Pop(ctx, *hand, k): circle(ctx, *hand, 26, RED)
    # частица движется
    seg = [math.dist(pts[i], pts[i+1]) for i in range(3)]; tot = sum(seg)
    pp = ease_in_out(prog(t, 1.0, 2.8)) * tot
    for back_i in range(6):
        q = max(0, pp - back_i*28); acc = 0
        for i in range(3):
            if q <= acc + seg[i] or i == 2:
                u = clamp((q - acc) / seg[i]); x = lerp(pts[i][0], pts[i+1][0], u); y = lerp(pts[i][1], pts[i+1][1], u); break
            acc += seg[i]
        if t > 1.0: virus(ctx, x, y, 22 - back_i*2.5, GREEN, rot=t*3, face=False, a=1 - back_i*0.14)
    if t > 3.8:
        pa = 0.5 + 0.5*math.sin(t*9)
        circle(ctx, *brain, 120 + pa*15, RED, 0.25)
        virus(ctx, *brain, 55, GREEN, rot=t)
    # таймлайн инкубации
    k = prog(t, 1.2, 0.5)
    with Pop(ctx, W/2, 420, k):
        col(ctx, WHITE); rrect(ctx, 70, 340, W-140, 170, 40); ctx.fill()
        text(ctx, "Инкубация: обычно 1–3 месяца", W/2, 410, 48, INK)
        text(ctx, "(бывает от недели до года)", W/2, 470, 36, GREY, bold=False)
    caption(ctx, "Вирус медленно ползёт по нервам к мозгу — симптомов пока нет!", t, 2.2, y=1530, size=50)

def sc_symptoms(ctx, t, d):
    title(ctx, "Симптомы", t)
    person(ctx, 540, 1080, 1.4, shirt=CORAL, face="sick", arm_l=12 + math.sin(t*25)*4,
           arm_r=12 - math.sin(t*25)*4, bob=math.sin(t*30)*3 if t > 1.5 else 0)
    cards = [
        ("Жар, слабость", "🌡", YELLOW),
        ("Боязнь воды", "💧", BLUE),
        ("Возбуждение, агрессия", "!", CORAL),
        ("Судороги, паралич", "⚡", PURPLE),
    ]
    pos = [(290, 1230), (790, 1230), (290, 1530), (790, 1530)]
    for i, ((name, ic, c), (x, y)) in enumerate(zip(cards, pos)):
        k = prog(t, 0.5 + i*0.55, 0.5)
        if k <= 0: continue
        with Pop(ctx, x, y + 120, k):
            col(ctx, c); rrect(ctx, x - 230, y, 460, 260, 40); ctx.fill()
            # иконки рисуем вручную (без эмодзи)
            ix, iy = x, y + 85
            if i == 0:
                col(ctx, WHITE); rrect(ctx, ix - 14, iy - 55, 28, 85, 14); ctx.fill(); circle(ctx, ix, iy + 35, 26, WHITE)
                col(ctx, RED); rrect(ctx, ix - 6, iy - 20, 12, 55, 6); ctx.fill(); circle(ctx, ix, iy + 35, 17, RED)
            elif i == 1:
                ctx.move_to(ix, iy - 60); ctx.curve_to(ix + 50, iy, ix + 45, iy + 45, ix, iy + 45)
                ctx.curve_to(ix - 45, iy + 45, ix - 50, iy, ix, iy - 60); col(ctx, WHITE); ctx.fill()
                line(ctx, ix - 60, iy + 50, ix + 60, iy - 60, 12, RED)
            elif i == 2:
                circle(ctx, ix, iy, 55, WHITE); text(ctx, "!", ix, iy + 32, 90, CORAL)
            else:
                ctx.move_to(ix + 15, iy - 65); ctx.line_to(ix - 30, iy + 5); ctx.line_to(ix, iy + 5)
                ctx.line_to(ix - 15, iy + 65); ctx.line_to(ix + 30, iy - 10); ctx.line_to(ix, iy - 10)
                ctx.close_path(); col(ctx, YELLOW); ctx.fill()
            for j, ln in enumerate(wrap(ctx, name, 38, 400)):
                text(ctx, ln, x, y + 200 + j*44 - (len(wrap(ctx, name, 38, 400)) - 1)*22, 38, WHITE if i != 0 else INK)
    k = prog(t, 3.0, 0.5)
    with Pop(ctx, W/2, 440, k):
        col(ctx, WHITE); rrect(ctx, 70, 360, W-140, 150, 40); ctx.fill()
        text(ctx, "Когда они появились —", W/2, 425, 46, INK)
        text(ctx, "лечить уже поздно", W/2, 485, 46, RED)

def sc_action(ctx, t, d):
    title(ctx, "Укусило животное?", t, c=INK, size=84)
    steps = [
        ("1", "Промой рану водой с мылом 15 минут", TEAL),
        ("2", "Сразу к врачу — в тот же день!", CORAL),
        ("3", "Пройди курс прививок полностью", PURPLE),
    ]
    for i, (n, s, c) in enumerate(steps):
        k = prog(t, 0.5 + i*2.4, 0.5)
        if k <= 0: continue
        y = 400 + i * 470
        with Pop(ctx, W/2, y + 200, k):
            col(ctx, (0, 0, 0), 0.12); rrect(ctx, 60, y + 12, W - 120, 420, 44); ctx.fill()
            col(ctx, WHITE); rrect(ctx, 60, y, W - 120, 420, 44); ctx.fill()
            badge(ctx, 140, y + 80, 50, c, n, 56)
            lt = t - (0.5 + i*2.4)
            if i == 0:   # мытьё рук под краном
                col(ctx, GREY); rrect(ctx, 210, y + 130, 160, 30, 12); ctx.fill(); rrect(ctx, 340, y + 130, 30, 70, 10); ctx.fill()
                for j in range(6):
                    q = ((lt * 2 + j / 6) % 1)
                    circle(ctx, 355, y + 210 + q * 120, 9, BLUE, 1 - q)
                for j, sx in enumerate((-1, 1)):
                    circle(ctx, 355 + sx*28 + math.sin(lt*14 + j*3)*12, y + 320, 30, SKIN)
                for j in range(5):
                    circle(ctx, 300 + j*28 + math.sin(lt*5 + j)*10, y + 290 - ((lt*40 + j*25) % 70), 10 + j % 3*3, WHITE)
                    ctx.set_line_width(3); ctx.arc(300 + j*28 + math.sin(lt*5 + j)*10, y + 290 - ((lt*40 + j*25) % 70), 10 + j % 3*3, 0, 2*math.pi); col(ctx, SKY); ctx.stroke()
                # таймер
                cx, cy = 870, y + 260
                circle(ctx, cx, cy, 80, hexc("e8f7f5"))
                ctx.move_to(cx, cy); ctx.arc(cx, cy, 80, -math.pi/2, -math.pi/2 + 2*math.pi*clamp(lt/2.2))
                ctx.close_path(); col(ctx, TEAL); ctx.fill()
                text(ctx, "15", cx, cy + 14, 44, INK); text(ctx, "мин", cx, cy + 58, 26, INK, bold=False)
            elif i == 1:  # человечек бежит к больнице
                hx = 820
                col(ctx, hexc("f1f5f9")); rrect(ctx, hx - 110, y + 150, 220, 240, 16); ctx.fill()
                col(ctx, RED); rrect(ctx, hx - 15, y + 175, 30, 80, 6); ctx.fill(); rrect(ctx, hx - 40, y + 200, 80, 30, 6); ctx.fill()
                col(ctx, SKY); rrect(ctx, hx - 35, y + 290, 70, 100, 8); ctx.fill()
                px = lerp(280, 600, ease_in_out(clamp(lt / 2.0)))
                person(ctx, px, y + 395, 0.7, shirt=BLUE, leg=lt*14 if lt < 2 else 0, arm_l=35, arm_r=35)
                for j in range(3):
                    line(ctx, px - 70 - j*20, y + 220 + j*40, px - 120 - j*20, y + 220 + j*40, 8, GREY, 0.5)
            else:  # шприц + календарь
                syringe(ctx, 330, y + 280, 1.0, rot=-0.5 + math.sin(lt*3)*0.05)
                days = ["0", "3", "7", "14", "28"]
                for j, dd in enumerate(days):
                    kk = prog(lt, 0.3 + j*0.25, 0.3)
                    bx = 560 + (j % 3) * 140; by = y + 200 + (j // 3) * 120
                    with Pop(ctx, bx, by, kk):
                        col(ctx, hexc("efeaff")); rrect(ctx, bx - 55, by - 50, 110, 100, 18); ctx.fill()
                        text(ctx, dd, bx, by + 18, 48, PURPLE)
                text(ctx, "день", 840, y + 345, 34, GREY, bold=False)
            for j, ln in enumerate(wrap(ctx, s, 44, 760)):
                text(ctx, ln, 210, y + 75 + j*52, 44, INK, align="left")
    k = ease_out(prog(t, 7.8, 0.4))
    text(ctx, "*точную схему назначит врач", W/2, 1850, 32, GREY, bold=False, a=k)

def sc_prevent(ctx, t, d):
    title(ctx, "Профилактика", t)
    ground(ctx, 1150, hexc("b7e4c7"))
    person(ctx, 360, 1150, 1.4, shirt=TEAL, arm_r=60 + math.sin(t*3)*10, face="happy")
    dog(ctx, 700, 1150, 0.95, c=hexc("c08552"), tail=t*14, leg=0)
    k = prog(t, 0.8, 0.5)
    with Pop(ctx, 820, 780, k):
        syringe(ctx, 820, 780, 0.9, rot=0.6 + math.sin(t*4)*0.08)
        check(ctx, 930, 690, 1.0)
    items = [("Прививай домашних животных каждый год", True),
             ("Не трогай диких и бездомных животных", False),
             ("Странно ведёт себя зверь? Отойди и сообщи взрослым", False)]
    for i, (s, ok) in enumerate(items):
        kk = prog(t, 1.5 + i*0.9, 0.5)
        if kk <= 0: continue
        y = 1240 + i*190
        with Pop(ctx, W/2, y + 80, kk):
            col(ctx, WHITE); rrect(ctx, 70, y, W-140, 165, 40); ctx.fill()
            (check if ok else cross)(ctx, 160, y + 82, 1.1)
            ls = wrap(ctx, s, 42, 740)
            for j, ln in enumerate(ls):
                text(ctx, ln, 230, y + 95 + j*50 - (len(ls)-1)*25, 42, INK, align="left")

def sc_end(ctx, t, d):
    for i in range(3):
        rr = ((t*300 + i*260) % 800)
        ctx.set_line_width(8); ctx.arc(W/2, 780, rr, 0, 2*math.pi); col(ctx, WHITE, 0.25*(1 - rr/800)); ctx.stroke()
    k = prog(t, 0.1, 0.6)
    with Pop(ctx, W/2, 780, k):
        sc = 1 + math.sin(t*6)*0.04
        ctx.save(); ctx.translate(W/2, 780); ctx.scale(sc*2.6, sc*2.6)
        ctx.move_to(0, 60); ctx.curve_to(-120, -20, -60, -110, 0, -50)
        ctx.curve_to(60, -110, 120, -20, 0, 60); col(ctx, WHITE); ctx.fill(); ctx.restore()
        syringe(ctx, W/2, 760, 0.9, rot=-0.6)
    k = prog(t, 0.6, 0.5)
    with Pop(ctx, W/2, 1150, k):
        text(ctx, "Вакцина", W/2, 1150, 110, WHITE)
        text(ctx, "спасает жизнь", W/2, 1270, 90, YELLOW)
    k = ease_out(prog(t, 1.3, 0.5))
    para(ctx, "Не жди симптомов — после укуса действуй сразу!", W/2, 1440 + (1-k)*30, 50, WHITE, 900, a=k)
    for i, (x, c) in enumerate(((220, BLUE), (430, YELLOW), (650, GREEN), (860, PURPLE))):
        kk = prog(t, 1.8 + i*0.15, 0.4)
        with Pop(ctx, x, 1860, kk):
            person(ctx, x, 1900, 0.75, shirt=c, arm_l=150 + math.sin(t*8 + i)*15, arm_r=150 - math.sin(t*8 + i)*15,
                   bob=-abs(math.sin(t*6 + i))*20)

SCENES = [  # (функция, длительность, цвет фона)
    (sc_title, 4.5, NAVY),
    (sc_what, 6.5, hexc("3d5a80")),
    (sc_bite, 7.5, SKY),
    (sc_carriers, 6.0, hexc("ff9f1c")),
    (sc_path, 7.0, CREAM),
    (sc_symptoms, 6.5, hexc("2b2d42")),
    (sc_action, 9.0, hexc("e0fbfc")),
    (sc_prevent, 6.5, hexc("3a86ff")),
    (sc_end, 5.0, hexc("ef476f")),
]
STARTS = np.cumsum([0] + [s[1] for s in SCENES])
TOTAL = float(STARTS[-1])
NFRAMES = int(TOTAL * FPS)
FADE = 0.35

def render(fi):
    t = fi / FPS
    idx = int(np.searchsorted(STARTS, t, side="right") - 1); idx = min(idx, len(SCENES) - 1)
    fn, dur, bg = SCENES[idx]; lt = t - STARTS[idx]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    prev_bg = SCENES[idx - 1][2] if idx > 0 else bg
    col(ctx, lerpc(prev_bg, bg, ease_out(clamp(lt / FADE)))); ctx.paint()
    alpha = clamp(lt / FADE) * (clamp((dur - lt) / FADE) if idx < len(SCENES) - 1 else 1)
    ctx.push_group(); fn(ctx, lt, dur); ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)
    # прогресс-бар сверху
    col(ctx, WHITE, 0.35); rrect(ctx, 60, 60, W - 120, 12, 6); ctx.fill()
    col(ctx, WHITE, 0.95); rrect(ctx, 60, 60, (W - 120) * t / TOTAL, 12, 6); ctx.fill()
    surf.flush()
    return bytes(surf.get_data())

# ---------- музыка ----------
def music(path):
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr
    out = np.zeros(n)
    bpm = 100; beat = 60 / bpm
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    bar = beat * 4
    for b in range(int(TOTAL / bar) + 1):
        ch = chords[b % 4]; t0 = b * bar
        i0, i1 = int(t0 * sr), min(n, int((t0 + bar) * sr))
        seg = tt[i0:i1] - t0
        env = np.minimum(1, seg / 0.3) * np.minimum(1, (bar - seg) / 0.3)
        for m in ch:
            out[i0:i1] += 0.05 * env * np.sin(2 * np.pi * f(m) * seg)
        out[i0:i1] += 0.08 * env * np.sin(2 * np.pi * f(ch[0] - 12) * seg)
        for s in range(8):  # арпеджио
            m = ch[s % 3] + (12 if s >= 4 else 0) + 12
            ts = t0 + s * beat / 2; j0 = int(ts * sr); j1 = min(n, j0 + int(0.4 * sr))
            if j0 >= n: break
            ss = tt[j0:j1] - ts
            out[j0:j1] += 0.07 * np.exp(-ss * 9) * np.sin(2 * np.pi * f(m) * ss)
        for s in range(4):  # мягкая бочка
            ts = t0 + s * beat; j0 = int(ts * sr); j1 = min(n, j0 + int(0.25 * sr))
            if j0 >= n: break
            ss = tt[j0:j1] - ts
            out[j0:j1] += 0.18 * np.exp(-ss * 18) * np.sin(2 * np.pi * (50 + 80 * np.exp(-ss * 30)) * ss)
    # «поп» на смене сцен
    for st in STARTS[1:-1]:
        j0 = int(st * sr); j1 = min(n, j0 + int(0.2 * sr)); ss = tt[j0:j1] - st
        out[j0:j1] += 0.15 * np.exp(-ss * 25) * np.sin(2 * np.pi * (900 - 2000 * ss) * ss)
    fade = np.minimum(1, np.minimum(tt / 1.0, (TOTAL - tt) / 1.5))
    out = np.tanh(out * fade * 1.4) * 0.8
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "preview":  # PNG-кадры для проверки
        for sec in map(float, sys.argv[2:]):
            surf = cairo.ImageSurface.create_for_data(bytearray(render(int(sec * FPS))), cairo.FORMAT_ARGB32, W, H)
            surf.write_to_png(os.path.join(HERE, f"preview_{sec:05.1f}.png"))
        return
    wav = os.path.join(HERE, "_music.wav"); music(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    with Pool() as pool:
        for i, fr in enumerate(pool.imap(render, range(NFRAMES), chunksize=8)):
            ff.stdin.write(fr)
            if i % 150 == 0: print(f"кадр {i}/{NFRAMES}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print("готово:", OUT, f"({TOTAL:.1f} с)")

if __name__ == "__main__":
    main()
