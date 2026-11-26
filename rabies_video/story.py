"""Сюжетное видео 9:16 про бешенство: «До свадьбы заживёт?»
Озвучка — RHVoice (apt: rhvoice rhvoice-russian), графика — pycairo, сборка — ffmpeg.
Запуск:  python3 story.py            -> rabies_story_9x16.mp4
         python3 story.py preview 5 12   -> PNG-кадры для проверки
"""
import math, os, subprocess, sys, wave, hashlib
from multiprocessing import Pool
import numpy as np
import cairo
from render import *  # примитивы и персонажи из первого видео

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "rabies_story_9x16.mp4")
CACHE = os.path.join(HERE, ".tts_cache")
SR = 44100
NO_VOICE = os.environ.get("NO_VOICE") == "1"  # 1 = без озвучки (музыка + субтитры)

VOICES = {  # ключ: (голос RHVoice, высота %, темп % (100 = норма), подпись, цвет подписи)
    "N": ("aleksandr-hq", 100, 112, None, NAVY),
    "B": ("elena", 92, 100, "Бабушка", PURPLE),
    "H": ("artemiy", 125, 112, "Ты", BLUE),
    "F": ("yuriy", 120, 115, "Друг", hexc("2a9d8f")),
    "D": ("irina", 100, 108, "Врач", RED),
}

# ---------- сценарий ----------
# сцена: (функция, фон, настроение музыки, [(ключ_метки, голос, текст, пауза_перед), ...])
def S(fn, bg, mood, lines, tail=0.7): return dict(fn=fn, bg=bg, mood=mood, lines=lines, tail=tail)

# ---------- дополнительные персонажи и декорации ----------
def kid(ctx, x, y, s=1.0, shirt=BLUE, cap=CORAL, **kw):
    person(ctx, x, y, s, shirt=shirt, pants=hexc("3d5a80"), **kw)
    flip = kw.get("flip", False); bob = kw.get("bob", 0)
    ctx.save(); ctx.translate(x, y + bob); ctx.scale(-s if flip else s, s)
    ctx.arc(0, -318, 55, math.pi, 2*math.pi); col(ctx, cap); ctx.fill()
    col(ctx, cap); rrect(ctx, 10, -325, 80, 16, 8); ctx.fill()
    ctx.restore()

def grandma(ctx, x, y, s=1.0, arm_l=15, arm_r=15, face="happy", bob=0.0, flip=False):
    ctx.save(); ctx.translate(x, y + bob); ctx.scale(-s if flip else s, s)
    dress, scarf = hexc("8e6bbf"), hexc("e63946")
    line(ctx, -16, -80, -18, 0, 20, hexc("6d4c41")); line(ctx, 16, -80, 18, 0, 20, hexc("6d4c41"))
    for side, ang in ((-1, arm_l), (1, arm_r)):
        a = math.radians(ang); sx, sy = side*34, -222
        ex, ey = sx + side*math.sin(a)*95, sy + math.cos(a)*95
        line(ctx, sx, sy, ex, ey, 24, dress); circle(ctx, ex, ey, 14, SKIN)
    ctx.move_to(-38, -240); ctx.line_to(38, -240); ctx.line_to(78, -60); ctx.line_to(-78, -60); ctx.close_path()
    col(ctx, dress); ctx.fill()
    col(ctx, WHITE); rrect(ctx, -34, -190, 68, 120, 14); ctx.fill()
    for i in range(3): circle(ctx, -18 + i*18, -150, 5, CORAL)
    hy = -292
    circle(ctx, 0, hy, 48, SKIN)
    ctx.arc(0, hy - 4, 56, math.pi*0.95, math.pi*2.05); col(ctx, scarf); ctx.fill()
    ctx.move_to(-10, hy + 40); ctx.line_to(10, hy + 40); ctx.line_to(28, hy + 72); ctx.line_to(-6, hy + 62); ctx.close_path()
    col(ctx, scarf); ctx.fill()
    for xx in (-20, 20): circle(ctx, xx + 10, hy - 30, 6, WHITE)
    for xx in (-18, 18):
        ctx.set_line_width(4); ctx.arc(xx, hy - 2, 15, 0, 2*math.pi); col(ctx, INK); ctx.stroke()
        circle(ctx, xx, hy - 2, 5, INK)
    line(ctx, -3, hy - 2, 3, hy - 2, 4, INK)
    if face == "happy":
        ctx.set_line_width(5); ctx.arc(0, hy + 18, 13, 0.15*math.pi, 0.85*math.pi); col(ctx, INK); ctx.stroke()
    else:
        line(ctx, -10, hy + 26, 10, hy + 26, 5, INK)
    circle(ctx, -32, hy + 16, 8, CORAL, 0.5); circle(ctx, 32, hy + 16, 8, CORAL, 0.5)
    ctx.restore()

def doctor(ctx, x, y, s=1.0, **kw):
    person(ctx, x, y, s, shirt=WHITE, pants=hexc("4a6fa5"), hair=hexc("333333"), **kw)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    col(ctx, RED); rrect(ctx, 8, -220, 10, 30, 2); ctx.fill(); rrect(ctx, -2, -210, 30, 10, 2); ctx.fill()
    ctx.set_line_width(5); ctx.arc(0, -232, 26, 0.1*math.pi, 0.9*math.pi); col(ctx, GREY); ctx.stroke()
    ctx.restore()

def tree(ctx, x, y, s=1.0, c=GREEN, trunk=BROWN):
    col(ctx, trunk); rrect(ctx, x - 14*s, y - 120*s, 28*s, 120*s, 8*s); ctx.fill()
    for dx, dy, r in ((0, -200, 80), (-50, -150, 60), (50, -150, 60)):
        circle(ctx, x + dx*s, y + dy*s, r*s, c)

def bush(ctx, x, y, s, c):
    for dx, dy, r in ((-50, -30, 45), (0, -50, 60), (55, -30, 45)): circle(ctx, x + dx*s, y + dy*s, r*s, c)

def house(ctx, x, y, s=1.0):
    col(ctx, hexc("c68b59")); ctx.rectangle(x - 200*s, y - 260*s, 400*s, 260*s); ctx.fill()
    for i in range(6): line(ctx, x - 200*s, y - 260*s + i*44*s, x + 200*s, y - 260*s + i*44*s, 3, hexc("a26c3c"))
    ctx.move_to(x - 240*s, y - 250*s); ctx.line_to(x, y - 420*s); ctx.line_to(x + 240*s, y - 250*s); ctx.close_path()
    col(ctx, hexc("d62828")); ctx.fill()
    col(ctx, WHITE); rrect(ctx, x - 150*s, y - 200*s, 110*s, 100*s, 8); ctx.fill()
    col(ctx, YELLOW); rrect(ctx, x - 140*s, y - 190*s, 90*s, 80*s, 6); ctx.fill()
    line(ctx, x - 95*s, y - 190*s, x - 95*s, y - 110*s, 6, WHITE); line(ctx, x - 140*s, y - 150*s, x - 50*s, y - 150*s, 6, WHITE)
    col(ctx, hexc("6d4c41")); rrect(ctx, x + 40*s, y - 190*s, 100*s, 190*s, 8); ctx.fill()
    circle(ctx, x + 120*s, y - 95*s, 8*s, YELLOW)

def car(ctx, x, y, s=1.0, wheel=0.0, c=hexc("ffbe0b")):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    col(ctx, c); rrect(ctx, -170, -110, 340, 80, 30); ctx.fill()
    ctx.move_to(-100, -110); ctx.line_to(-60, -175); ctx.line_to(70, -175); ctx.line_to(110, -110); ctx.close_path(); ctx.fill()
    col(ctx, SKY); ctx.move_to(-80, -115); ctx.line_to(-52, -162); ctx.line_to(0, -162); ctx.line_to(0, -115); ctx.close_path(); ctx.fill()
    ctx.move_to(12, -115); ctx.line_to(12, -162); ctx.line_to(62, -162); ctx.line_to(90, -115); ctx.close_path(); ctx.fill()
    for wx in (-100, 100):
        circle(ctx, wx, -30, 38, INK); circle(ctx, wx, -30, 16, GREY)
        line(ctx, wx, -30, wx + math.cos(wheel)*16, -30 + math.sin(wheel)*16, 5, INK)
    circle(ctx, 165, -85, 10, YELLOW)
    ctx.restore()

def moon_sky(ctx, t):
    circle(ctx, 820, 330, 90, hexc("fef3c7")); circle(ctx, 785, 305, 90, hexc("1b1f3b"))
    for i in range(40):
        sx = (i * 241) % W; sy = 160 + (i * 137) % 900
        a = 0.4 + 0.6*abs(math.sin(t*2 + i))
        circle(ctx, sx, sy, 2 + i % 3, WHITE, a)

def leaf(ctx, x, y, s=1.0, rot=0.3):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.save(); ctx.scale(1, 0.6); ctx.arc(0, 0, 40, 0, 2*math.pi); ctx.restore(); col(ctx, hexc("52b788")); ctx.fill()
    for i in (-20, 0, 20): line(ctx, i, -18, i, 18, 3, hexc("2d6a4f"))
    ctx.restore()

def subtitle(ctx, voice, txt, k):
    _, _, _, label, lc = VOICES[voice]
    size = 50
    lines = wrap(ctx, txt, size, 860)
    h = len(lines) * size * 1.28 + 60
    y = 1880 - h
    a = clamp(k)
    with Pop(ctx, W/2, y + h/2, a, alpha=a):
        col(ctx, (0, 0, 0), 0.25); rrect(ctx, 60, y + 10, W - 120, h, 36); ctx.fill()
        col(ctx, WHITE); rrect(ctx, 60, y, W - 120, h, 36); ctx.fill()
        if label:
            ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(36)
            lw = ctx.text_extents(label).x_advance + 50
            col(ctx, lc); rrect(ctx, 100, y - 34, lw, 60, 30); ctx.fill()
            text(ctx, label, 100 + lw/2, y + 9, 36, WHITE)
        for i, ln in enumerate(lines):
            text(ctx, ln, W/2, y + 30 + size + i*size*1.28 - 6, size, INK if voice == "N" else lc)

# ---------- сцены (M = метки реплик: M[key] = (start, end)) ----------
def at(M, key, frac=0.0):
    s, e = M[key]; return s + (e - s) * frac

def sc_intro(ctx, t, d, M):
    for i in range(10):
        px = (i * 197 + 80) % W; py = ((i * 331) % H + t * (30 + i*5)) % (H + 200) - 100
        virus(ctx, px, py, 18 + (i % 3)*8, hexc("2b3a5c"), rot=t*0.5 + i, face=False)
    with Pop(ctx, W/2, 560, prog(t, 0.2, 0.6)):
        leaf(ctx, W/2, 560, 3.2, rot=-0.3 + math.sin(t*2)*0.08)
    with Pop(ctx, W/2, 900, prog(t, 0.6, 0.5)):
        text(ctx, "«ДО СВАДЬБЫ", W/2, 880, 104, YELLOW)
        text(ctx, "ЗАЖИВЁТ»?", W/2, 1000, 104, YELLOW)
    k = ease_out(prog(t, 1.2, 0.5))
    text(ctx, "история про бешенство", W/2, 1120 + (1-k)*30, 52, WHITE, bold=False, a=k)

def sc_village(ctx, t, d, M):
    circle(ctx, 180, 300, 80, YELLOW)
    for cx, cy in ((700, 330), (900, 260)):
        for dx, r in ((-50, 45), (0, 60), (50, 45)): circle(ctx, cx + dx, cy, r, WHITE)
    ground(ctx, 1300, hexc("95d5b2"))
    tree(ctx, 140, 1300, 1.3, hexc("52b788")); tree(ctx, 960, 1300, 1.1, hexc("40916c"))
    house(ctx, 560, 1300, 1.25)
    for i in range(12):
        col(ctx, hexc("e9c46a")); rrect(ctx, i*95 - 10, 1210, 30, 110, 6); ctx.fill()
    col(ctx, hexc("e9c46a")); ctx.rectangle(0, 1240, W, 16); ctx.fill()
    col(ctx, hexc("b08968")); ctx.rectangle(0, 1330, W, 120); ctx.fill()
    arrive = ease_out(prog(t, 0.0, 2.2))
    cx = lerp(-300, 330, arrive)
    car(ctx, cx, 1440, 1.0, wheel=cx/38)
    ks = prog(t, 2.0, 0.5)
    if ks > 0:
        with Pop(ctx, 470, 1440, ks):
            kid(ctx, 470, 1440, 0.85, arm_r=150 + math.sin(t*8)*15)
    gk = prog(t, at(M, "b1") - 0.4, 0.5)
    if gk > 0:
        with Pop(ctx, 800, 1440, gk):
            grandma(ctx, 800, 1440, 1.0, arm_l=150 + math.sin(t*7)*20, arm_r=150 - math.sin(t*7)*20,
                    bob=-abs(math.sin(t*5))*10 if t < at(M, "b1", 1) else 0)
            for i in range(3):
                kk = prog(t, at(M, "b1") + i*0.25, 0.4)
                with Pop(ctx, 700 + i*90, 980 - i*40, kk):
                    ctx.save(); ctx.translate(700 + i*90, 980 - i*40); ctx.scale(0.35, 0.35)
                    ctx.move_to(0, 60); ctx.curve_to(-120, -20, -60, -110, 0, -50); ctx.curve_to(60, -110, 120, -20, 0, 60)
                    col(ctx, CORAL); ctx.fill(); ctx.restore()

def sc_friend(ctx, t, d, M):
    circle(ctx, 880, 320, 90, hexc("ffb703"))
    ground(ctx, 1150, hexc("74c69d"))
    for i in range(18):
        circle(ctx, (i*137) % W, 1180 + (i*71) % 250, 8, [YELLOW, WHITE, CORAL][i % 3])
    tree(ctx, 120, 1150, 1.2, hexc("40916c"))
    leave = at(M, "f1", 0.9)
    ball_x = 540 + math.sin(t*2.2)*240
    ball_y = 1380 - abs(math.sin(t*4.4))*180
    if t < leave:
        kid(ctx, 300, 1420, 1.0, arm_l=30 + math.sin(t*4.4)*30, arm_r=30 + math.cos(t*4.4)*30,
            bob=-abs(math.sin(t*4.4))*25)
        person(ctx, 780, 1420, 1.0, shirt=hexc("2a9d8f"), hair=hexc("222222"), face="happy",
               arm_l=150 if t > at(M, "f1") else 30, arm_r=150 if t > at(M, "f1") else 30,
               bob=-abs(math.cos(t*4.4))*25)
        circle(ctx, ball_x, ball_y, 40, WHITE); circle(ctx, ball_x, ball_y, 40, CORAL, 0.0)
        ctx.set_line_width(5); ctx.arc(ball_x, ball_y, 40, 0, 2*math.pi); col(ctx, INK); ctx.stroke()
        circle(ctx, ball_x, ball_y, 13, INK)
    else:
        lt = t - leave
        kid(ctx, 300, 1420, 1.0, arm_r=150 if lt < 1.2 else 20, arm_l=20, face="sad" if lt > 1.5 else "happy")
        fx = 780 + lt*260
        person(ctx, fx, 1420, 1.0 - min(lt*0.05, 0.3), shirt=hexc("2a9d8f"), hair=hexc("222222"),
               leg=lt*10, arm_l=30, arm_r=150 if lt < 1 else 30)
    # небо темнеет к вечеру
    dark = prog(t, at(M, "f1"), 3.0)
    col(ctx, hexc("3c1642"), 0.45*dark); ctx.paint()

def sc_night(ctx, t, d, M):
    moon_sky(ctx, t)
    ground(ctx, 1250, hexc("1b4332"))
    col(ctx, hexc("2d3142")); ctx.rectangle(0, 1330, W, 110); ctx.fill()
    for i in range(6):
        tree(ctx, i*210 - 40, 1260, 1.1 + (i % 2)*0.3, hexc("081c15"), hexc("081c15"))
    bush(ctx, 900, 1340, 1.6, hexc("2d6a4f"))
    t_fox, t_bite = at(M, "n4"), at(M, "n5")
    walk = ease_out(prog(t, 0.0, max(1.0, t_fox - 0.3)))
    kx = lerp(-120, 360, walk)
    hit = t > t_bite
    shake = math.sin(t*60)*12*clamp(1 - (t - t_bite)/0.6) if hit else 0
    kid(ctx, kx + shake, 1440, 1.05, leg=t*9 if t < t_fox - 0.3 else 0,
        face="scared" if t > t_fox + 0.6 else "happy",
        arm_l=150 if hit else 25, arm_r=140 if hit else 25)
    # фонарик
    if not hit:
        line(ctx, kx + 75, 1220, kx + 105, 1240, 18, GREY)
        ctx.move_to(kx + 110, 1240); ctx.line_to(kx + 520, 1150); ctx.line_to(kx + 520, 1420); ctx.close_path()
        col(ctx, YELLOW, 0.12); ctx.fill()
    # лиса
    if t > t_fox - 0.5:
        lt = t - (t_fox - 0.5)
        if not hit:
            fx = lerp(960, 640, ease_in_out(clamp((t - t_fox) / max(0.5, t_bite - t_fox))))
            lunge = clamp((t - (t_bite - 0.25)) / 0.25) * 80
            dog(ctx, fx - lunge, 1440, 0.95, c=hexc("e76f51"), fox=True, flip=True, leg=t*6 if t > t_fox else 0,
                mouth=0.6 if t > t_bite - 0.5 else 0.2, angry=True)
            for ex in (fx - 125 - lunge,):
                circle(ctx, ex, 1270, 10, YELLOW, 0.8)
        else:
            fx = 560 + (t - t_bite)**2 * 700
            dog(ctx, fx, 1440, 0.95, c=hexc("e76f51"), fox=True, leg=t*14)
        if t < t_fox:  # глаза в кустах
            for ex in (870, 920): circle(ctx, ex, 1290, 9, YELLOW, clamp(lt*2))
    if hit:
        k = prog(t, t_bite, 0.35)
        with Pop(ctx, 470, 1280, k, alpha=clamp(1 - (t - t_bite - 1.2)/0.5)):
            ctx.save(); ctx.translate(470, 1280)
            ctx.move_to(0, -110)
            for i in range(1, 16):
                r = 110 if i % 2 == 0 else 55; a = i*math.pi/8 - math.pi/2
                ctx.line_to(math.cos(a)*r, math.sin(a)*r)
            ctx.close_path(); col(ctx, YELLOW); ctx.fill(); ctx.restore()
            text(ctx, "КУСЬ!", 470, 1300, 56, RED)
        fl = clamp(1 - (t - t_bite)/0.25)
        col(ctx, WHITE, 0.6*fl); ctx.paint()

def interior(ctx):
    col(ctx, hexc("f6bd60")); ctx.rectangle(0, 0, W, 1300); ctx.fill()
    for i in range(12): line(ctx, i*100, 0, i*100, 1300, 6, hexc("f7c873"))
    col(ctx, hexc("bc6c25")); ctx.rectangle(0, 1300, W, H); ctx.fill()
    col(ctx, WHITE); rrect(ctx, 640, 380, 300, 320, 12); ctx.fill()
    col(ctx, hexc("1b1f3b")); rrect(ctx, 660, 400, 260, 280, 6); ctx.fill()
    circle(ctx, 850, 470, 30, hexc("fef3c7"))
    line(ctx, 790, 400, 790, 680, 10, WHITE); line(ctx, 660, 540, 920, 540, 10, WHITE)
    line(ctx, 300, 0, 300, 300, 4, INK); ctx.move_to(220, 380); ctx.line_to(380, 380); ctx.line_to(330, 300); ctx.line_to(270, 300)
    ctx.close_path(); col(ctx, CORAL); ctx.fill(); circle(ctx, 300, 390, 22, YELLOW)
    col(ctx, hexc("7f5539")); rrect(ctx, 380, 1060, 330, 30, 8); ctx.fill()
    line(ctx, 410, 1090, 410, 1300, 18, hexc("7f5539")); line(ctx, 680, 1090, 680, 1300, 18, hexc("7f5539"))
    col(ctx, WHITE); rrect(ctx, 520, 990, 70, 70, 10); ctx.fill()

def sc_home(ctx, t, d, M):
    interior(ctx)
    t_leaf = at(M, "b2", 0.35); healed = at(M, "n6", 0.5)
    kid(ctx, 300, 1500, 1.1, face="sad" if t < at(M, "b2", 0.6) else "happy",
        arm_l=20, arm_r=60 if t < at(M, "h2", 1) else 20)
    if t < at(M, "b2"): circle(ctx, 330, 1430, 12, RED)
    if t_leaf < t < healed + 0.5:
        with Pop(ctx, 330, 1430, prog(t, t_leaf, 0.4), alpha=clamp((healed + 0.5 - t)/0.5)):
            leaf(ctx, 330, 1430, 0.9, rot=0.4)
    grandma(ctx, 780, 1500, 1.25, face="happy", arm_l=20 + (math.sin(t*6)*25 + 50 if at(M, "b2") < t < at(M, "b2", 1) else 0),
            arm_r=20 + (130 if at(M, "b2") < t < at(M, "b2", 1) else 0))
    if t > healed:
        k = prog(t, healed, 0.5)
        with Pop(ctx, 300, 820, k):
            check(ctx, 300, 820, 1.6)

def sc_later(ctx, t, d, M):
    # календарь
    t1, t2, t3 = at(M, "n7"), at(M, "n8"), at(M, "n9")
    if t < t2 + 0.3:
        a = clamp((t2 + 0.3 - t)/0.4)
        ctx.push_group()
        col(ctx, (0, 0, 0), 0.15); rrect(ctx, 240, 512, 600, 640, 40); ctx.fill()
        col(ctx, WHITE); rrect(ctx, 240, 500, 600, 640, 40); ctx.fill()
        col(ctx, RED); rrect(ctx, 240, 500, 600, 150, 40); ctx.fill(); ctx.rectangle(240, 600, 600, 50); ctx.fill()
        months = ["ИЮНЬ", "ИЮЛЬ", "АВГУСТ"]
        flip = clamp((t - t1)/1.2)
        mi = min(2, int(flip * 2.99))
        text(ctx, months[mi], 540, 605, 70, WHITE)
        day = int(lerp(14, 14, flip)) if mi < 2 else 14
        text(ctx, str((int(t * 9) % 30) + 1 if flip < 1 else 14), 540, 960, 260, INK)
        for x in (330, 750): circle(ctx, x, 500, 22, NAVY)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    if t > t2:
        k = prog(t, t2, 0.5)
        sick = t > t3
        sh = math.sin(t*35)*5 if sick else 0
        with Pop(ctx, 540, 1500, k):
            kid(ctx, 540 + sh, 1500, 1.25, shirt=hexc("8d99ae"), face="sick" if sick else "sad",
                arm_l=10 + sh, arm_r=10 - sh)
        if sick:
            pa = 0.5 + 0.5*math.sin(t*7)
            col(ctx, RED, 0.12 + 0.12*pa); ctx.paint()
            icons = ["fever", "water", "light"]
            for i, ic in enumerate(icons):
                kk = prog(t, at(M, "n9", [0.0, 0.18, 0.7][i]), 0.4)
                x, y = [(220, 620), (540, 480), (860, 620)][i]
                with Pop(ctx, x, y, kk):
                    circle(ctx, x, y, 110, WHITE)
                    if ic == "fever":
                        col(ctx, CORAL); rrect(ctx, x - 16, y - 70, 32, 100, 16); ctx.fill(); circle(ctx, x, y + 40, 32, RED)
                        text(ctx, "39°", x, y + 100 - 120, 34, INK) if False else None
                    elif ic == "water":
                        ctx.move_to(x - 50, y - 60); ctx.line_to(x + 50, y - 60); ctx.line_to(x + 38, y + 70); ctx.line_to(x - 38, y + 70)
                        ctx.close_path(); col(ctx, SKY); ctx.fill()
                        col(ctx, BLUE); ctx.rectangle(x - 44, y - 10, 88, 78); ctx.fill()
                        line(ctx, x - 70, y + 70, x + 70, y - 70, 14, RED)
                    else:
                        circle(ctx, x, y, 40, YELLOW)
                        for j in range(8):
                            aa = j*math.pi/4 + t
                            line(ctx, x + math.cos(aa)*55, y + math.sin(aa)*55, x + math.cos(aa)*80, y + math.sin(aa)*80, 10, YELLOW)
                        text(ctx, "!", x + 70, y - 50, 60, RED)

def sc_verdict(ctx, t, d, M):
    with Pop(ctx, W/2, 640, prog(t, 0.0, 0.6)):
        virus(ctx, W/2, 640 + math.sin(t*3)*12, 190, GREEN, rot=t*0.4)
    with Pop(ctx, W/2, 1050, prog(t, 0.4, 0.5)):
        text(ctx, "БЕШЕНСТВО", W/2, 1080, 120, CORAL)
    with Pop(ctx, W/2, 1280, prog(t, at(M, "n10", 0.3), 0.5)):
        col(ctx, RED); rrect(ctx, 90, 1180, W - 180, 230, 40); ctx.fill()
        n = int(lerp(0, 100, ease_out(prog(t, at(M, "n10", 0.35), 1.2))))
        text(ctx, f"≈{n}%", W/2, 1300, 110, WHITE)
        text(ctx, "смертельно после симптомов", W/2, 1375, 40, WHITE)

def sc_rewind(ctx, t, d, M):
    t2 = at(M, "n12")
    if t < t2 - 0.2:
        for i in range(30):
            y = (i*97 + t*2600) % H
            col(ctx, WHITE, 0.06 + (i % 3)*0.04); ctx.rectangle(0, y, W, 6 + (i % 4)*6); ctx.fill()
        k = prog(t, 0.0, 0.4)
        with Pop(ctx, W/2, 700, k):
            for dx in (-90, 50):
                ctx.move_to(W/2 + dx + 120, 600); ctx.line_to(W/2 + dx, 700); ctx.line_to(W/2 + dx + 120, 800); ctx.close_path()
                col(ctx, WHITE); ctx.fill()
        if int(t*3) % 2 == 0: text(ctx, "◀◀ ПЕРЕМОТКА", W/2, 1000, 60, WHITE)
        circle(ctx, W/2, 1300, 150, WHITE)
        for ang, ln, w in ((-t*12, 100, 12), (-t*1.5, 70, 16)):
            line(ctx, W/2, 1300, W/2 + math.sin(ang)*ln, 1300 - math.cos(ang)*ln, w, INK)
    else:
        k = prog(t, t2 - 0.2, 0.5)
        with Pop(ctx, W/2, 700, k):
            leaf(ctx, W/2, 640, 3.0, rot=-0.3); cross(ctx, W/2 + 170, 520, 1.8)
        with Pop(ctx, W/2, 1100, prog(t, t2, 0.5)):
            text(ctx, "Укус — это", W/2, 1060, 90, WHITE)
            text(ctx, "НЕ ЕРУНДА", W/2, 1170, 110, YELLOW)

def sc_steps(ctx, t, d, M):
    title(ctx, "Как надо было:", t, y=220, c=INK, size=80)
    keys = ["s1", "s2", "s4"]
    colors = [TEAL, CORAL, PURPLE]
    labels = ["Промой рану водой с мылом — 15 минут", "В тот же день — к врачу", "Пройди весь курс прививок"]
    for i in range(3):
        st = at(M, keys[i]) - 0.2
        k = prog(t, st, 0.5)
        if k <= 0: continue
        y = 290 + i*430
        lt = t - st
        with Pop(ctx, W/2, y + 190, k):
            col(ctx, (0, 0, 0), 0.12); rrect(ctx, 60, y + 12, W - 120, 395, 40); ctx.fill()
            col(ctx, WHITE); rrect(ctx, 60, y, W - 120, 395, 40); ctx.fill()
            badge(ctx, 140, y + 75, 46, colors[i], str(i + 1), 52)
            ls = wrap(ctx, labels[i], 40, 780)
            for j, ln in enumerate(ls):
                text(ctx, ln, 210, y + 90 + j*46 - (len(ls) - 1)*20, 40, INK, align="left")
            if i == 0:
                col(ctx, GREY); rrect(ctx, 210, y + 140, 160, 28, 12); ctx.fill(); rrect(ctx, 340, y + 140, 30, 60, 10); ctx.fill()
                for j in range(6):
                    q = (lt*2 + j/6) % 1; circle(ctx, 355, y + 210 + q*110, 9, BLUE, 1 - q)
                for j, sx in enumerate((-1, 1)):
                    circle(ctx, 355 + sx*28 + math.sin(lt*14 + j*3)*12, y + 320, 30, SKIN)
                cx, cy = 860, y + 255
                circle(ctx, cx, cy, 80, hexc("e8f7f5"))
                ctx.move_to(cx, cy); ctx.arc(cx, cy, 80, -math.pi/2, -math.pi/2 + 2*math.pi*clamp(lt/3)); ctx.close_path()
                col(ctx, TEAL); ctx.fill()
                text(ctx, "15", cx, cy + 14, 44, INK); text(ctx, "мин", cx, cy + 56, 26, INK, bold=False)
            elif i == 1:
                px = lerp(200, 430, ease_in_out(clamp(lt/1.8)))
                kid(ctx, px, y + 385, 0.68, leg=lt*14 if lt < 1.8 else 0, arm_l=30, arm_r=30)
                talk = at(M, "s3") < t < at(M, "s3", 1)
                doctor(ctx, 760, y + 385, 0.68, face="happy", arm_l=20, arm_r=60 + (math.sin(t*8)*20 if talk else 0))
                if talk: syringe(ctx, 900, y + 190, 0.55, rot=-0.5)
            else:
                syringe(ctx, 320, y + 260, 0.9, rot=-0.5 + math.sin(lt*3)*0.05)
                days = ["0", "3", "7", "14", "28"]
                for j, dd in enumerate(days):
                    kk = prog(lt, 0.2 + j*0.2, 0.3)
                    bx = 560 + (j % 3)*140; by = y + 195 + (j // 3)*115
                    with Pop(ctx, bx, by, kk):
                        col(ctx, hexc("efeaff")); rrect(ctx, bx - 55, by - 48, 110, 96, 18); ctx.fill()
                        text(ctx, dd, bx, by + 17, 46, PURPLE)
                text(ctx, "день*", 840, y + 330, 32, GREY, bold=False)

def sc_carriers(ctx, t, d, M):
    title(ctx, "Кто переносит?", t, y=220)
    items = [
        ("Лисы", lambda x, y: dog(ctx, x + 20, y, 0.7, c=hexc("ef6c00"), fox=True, tail=t*6), 0.18),
        ("Собаки", lambda x, y: dog(ctx, x + 20, y, 0.7, c=hexc("c08552"), tail=t*12), 0.27),
        ("Кошки", lambda x, y: cat(ctx, x, y, 0.95), 0.36),
        ("Летучие мыши", lambda x, y: bat(ctx, x, y - 110 + math.sin(t*4)*12, 0.8, flap=t*14), 0.45),
    ]
    pos = [(290, 640), (790, 640), (290, 1020), (790, 1020)]
    for (name, fn, fr), (x, y) in zip(items, pos):
        k = prog(t, at(M, "c1", fr) - 0.3, 0.45)
        if k <= 0: continue
        with Pop(ctx, x, y - 110, k):
            col(ctx, (0, 0, 0), 0.15); rrect(ctx, x - 220, y - 280 + 12, 440, 350, 40); ctx.fill()
            col(ctx, WHITE); rrect(ctx, x - 220, y - 280, 440, 350, 40); ctx.fill()
            ctx.save(); ctx.rectangle(x - 220, y - 280, 440, 280); ctx.clip(); fn(x, y - 30); ctx.restore()
            text(ctx, name, x, y + 40, 42, INK)
    k = prog(t, at(M, "c1", 0.62), 0.5)
    with Pop(ctx, W/2, 1300, k):
        col(ctx, RED); rrect(ctx, 70, 1180, W - 140, 220, 40); ctx.fill()
        text(ctx, "Дикий зверь не боится", W/2, 1270, 50, WHITE)
        text(ctx, "людей? Держись подальше!", W/2, 1340, 50, WHITE)

def sc_end(ctx, t, d, M):
    for i in range(3):
        rr = (t*300 + i*260) % 800
        ctx.set_line_width(8); ctx.arc(W/2, 600, rr, 0, 2*math.pi); col(ctx, WHITE, 0.25*(1 - rr/800)); ctx.stroke()
    with Pop(ctx, W/2, 600, prog(t, 0.1, 0.6)):
        sc = 1 + math.sin(t*6)*0.04
        ctx.save(); ctx.translate(W/2, 600); ctx.scale(sc*2.4, sc*2.4)
        ctx.move_to(0, 60); ctx.curve_to(-120, -20, -60, -110, 0, -50); ctx.curve_to(60, -110, 120, -20, 0, 60)
        col(ctx, WHITE); ctx.fill(); ctx.restore()
        syringe(ctx, W/2, 590, 0.85, rot=-0.6)
    grandma(ctx, 700, 1450, 1.05, arm_l=150 + math.sin(t*7)*20, arm_r=40, face="happy")
    kid(ctx, 400, 1450, 0.95, arm_l=150 - math.sin(t*7)*20, arm_r=150 + math.sin(t*7)*20,
        bob=-abs(math.sin(t*5))*18)
    k = prog(t, at(M, "e2") - 0.2, 0.5)
    with Pop(ctx, W/2, 940, k):
        text(ctx, "Вакцина", W/2, 920, 100, WHITE)
        text(ctx, "спасает жизнь", W/2, 1030, 84, YELLOW)

SCENES = [
    S(sc_intro, NAVY, "calm", [("i1", "N", "Эта история могла случиться с кем угодно.", 1.6)], tail=0.6),
    S(sc_village, SKY, "happy", [
        ("n1", "N", "Летом тебя привезли к бабушке в деревню.", 0.5),
        ("b1", "B", "Ой, внучек приехал! Проходи, проходи!", 0.3)]),
    S(sc_friend, hexc("caf0f8"), "happy", [
        ("n2", "N", "Днём ты гулял с другом. Вы играли до самого вечера.", 0.4),
        ("f1", "F", "Ладно, мне пора. Пока!", 0.3),
        ("n3", "N", "Друг ушёл домой, а ты остался один.", 0.6)]),
    S(sc_night, hexc("1b1f3b"), "dark", [
        ("n4a", "N", "Ты идёшь домой. Уже совсем темно.", 1.2),
        ("n4", "N", "Из кустов выходит лиса. Она не убегает от человека. Это очень плохой знак.", 0.6),
        ("n5", "N", "Лиса бросается и кусает тебя за ногу!", 0.3),
        ("h1", "H", "Ай!", 0.2)]),
    S(sc_home, hexc("f6bd60"), "calm", [
        ("h2", "H", "Бабуль, меня лиса укусила!", 0.5),
        ("b2", "B", "Ой, ерунда! Подорожник приложим — до свадьбы заживёт!", 0.3),
        ("n6", "N", "Ранка быстро затянулась, и ты про неё забыл.", 0.4)]),
    S(sc_later, hexc("2b2d42"), "dark", [
        ("n7", "N", "Прошёл месяц.", 0.6),
        ("n8", "N", "А потом ты сам замечаешь, что с тобой что-то не так.", 0.6),
        ("n9", "N", "Жар. Слабость. Страшно пить воду — горло сводит судорогой. Свет и шум раздражают.", 0.3)]),
    S(sc_verdict, hexc("111111"), "dark", [
        ("n10", "N", "Это бешенство. Когда появились симптомы, спасти человека почти невозможно.", 0.8)], tail=1.0),
    S(sc_rewind, hexc("3a0ca3"), "rewind", [
        ("n11", "N", "Стоп. Давай перемотаем назад.", 0.3),
        ("n12", "N", "Укус дикого животного — это не ерунда. Вот что нужно было сделать.", 0.6)]),
    S(sc_steps, hexc("e0fbfc"), "happy", [
        ("s1", "N", "Сразу промыть рану водой с мылом. Пятнадцать минут.", 0.5),
        ("s2", "N", "В тот же день поехать к врачу, в травмпункт.", 0.5),
        ("s3", "D", "Сделаем прививки от бешенства. Главное — успеть до симптомов.", 0.3),
        ("s4", "N", "И пройти весь курс прививок до конца.", 0.5)], tail=1.0),
    S(sc_carriers, hexc("ff9f1c"), "happy", [
        ("c1", "N", "Бешенство переносят лисы, собаки, кошки, летучие мыши. "
                    "Если дикое животное не боится людей — держись подальше.", 0.6)], tail=1.0),
    S(sc_end, hexc("ef476f"), "happy", [
        ("e1", "B", "Вот умница! Береги себя.", 0.5),
        ("e2", "N", "Укусило животное — сразу к врачу. Вакцина спасает жизнь.", 0.4)], tail=2.0),
]

# ---------- TTS и таймлайн ----------
def tts(voice, txt):
    os.makedirs(CACHE, exist_ok=True)
    name, pitch, rate = VOICES[voice][:3]
    h = hashlib.md5(f"{name}|{pitch}|{rate}|{txt}".encode()).hexdigest()[:16]
    raw, wav = os.path.join(CACHE, h + "_raw.wav"), os.path.join(CACHE, h + ".wav")
    if not os.path.exists(wav):
        subprocess.run(["RHVoice-test", "-p", name, "-t", str(pitch), "-r", str(rate), "-o", raw],
                       input=txt.encode(), check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", str(SR), "-ac", "1",
                        "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                               "silenceremove=start_periods=1:start_threshold=-50dB,areverse,loudnorm=I=-16",
                        wav], check=True)
        os.remove(raw)
    with wave.open(wav) as wf:
        return np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768

def load_audio(path):
    """mp3/wav -> моно 44.1 кГц, без тишины по краям, громкость выровнена."""
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                          "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                                 "silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).astype(np.float32) / 32768

def build():
    t, plan = 0.0, []
    for sc in SCENES:
        start = t; lt = 0.0; marks = {}; clips = []
        for key, v, txt, pre in sc["lines"]:
            lt += pre; a = tts(v, txt); dur = len(a) / SR
            marks[key] = (lt, lt + dur); clips.append((start + lt, a, v, txt, key)); lt += dur
        extra = []
        if sc.get("audio"):  # своя запись на всю сцену: растягиваем метки и субтитры под её длину
            rec = load_audio(sc["audio"]); first = sc["lines"][0][3]; pad = 0.4
            r = (len(rec) / SR) / (lt - first)
            fix = lambda x: pad + (x - first) * r
            marks = {k: (fix(a), fix(b)) for k, (a, b) in marks.items()}
            clips = [(start + fix(st - start), np.zeros(int(len(a) * r)), v, txt, key) for st, a, v, txt, key in clips]
            extra = [(start + pad, rec)]; lt = pad + len(rec) / SR
        dur = lt + sc["tail"]
        plan.append(dict(sc, start=start, dur=dur, marks=marks, clips=clips, extra=extra)); t += dur
    return plan, t

PLAN, TOTAL = None, None
def init():
    global PLAN, TOTAL
    if PLAN is None: PLAN, TOTAL = build()

FADE = 0.35
def frame(fi):
    init(); t = fi / FPS
    idx = max(i for i, p in enumerate(PLAN) if p["start"] <= t + 1e-9)
    p = PLAN[idx]; lt = t - p["start"]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    prev = PLAN[idx - 1]["bg"] if idx else p["bg"]
    col(ctx, lerpc(prev, p["bg"], ease_out(clamp(lt / FADE)))); ctx.paint()
    alpha = clamp(lt / FADE) * (clamp((p["dur"] - lt) / FADE) if idx < len(PLAN) - 1 else 1)
    ctx.push_group(); p["fn"](ctx, lt, p["dur"], p["marks"]); ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)
    for st, a, v, txt, key in p["clips"]:
        en = st + len(a) / SR
        if st - 0.1 <= t <= en + 0.25:
            subtitle(ctx, v, txt, min(clamp((t - st + 0.1) / 0.2), clamp((en + 0.25 - t) / 0.2)))
    col(ctx, WHITE, 0.35); rrect(ctx, 60, 60, W - 120, 12, 6); ctx.fill()
    col(ctx, WHITE, 0.95); rrect(ctx, 60, 60, (W - 120) * t / TOTAL, 12, 6); ctx.fill()
    surf.flush(); return bytes(surf.get_data())

# ---------- звук ----------
def soundtrack(path):
    init()
    n = int(TOTAL * SR) + SR; tt = np.arange(n) / SR
    mus = np.zeros(n); f = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 96; bar = beat * 4
    happy = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    mood_at = lambda x: next(p["mood"] for p in reversed(PLAN) if p["start"] <= x)
    for b in range(int(TOTAL / bar) + 1):
        t0 = b * bar; mood = mood_at(t0); ch = happy[b % 4]
        i0, i1 = int(t0*SR), min(n, int((t0 + bar)*SR)); seg = tt[i0:i1] - t0
        env = np.minimum(1, seg/0.3) * np.minimum(1, (bar - seg)/0.3)
        if mood == "dark":
            for m in (45, 52, 56 if b % 2 else 55):
                mus[i0:i1] += 0.06 * env * np.sin(2*np.pi*f(m - 12)*seg) * (0.7 + 0.3*np.sin(2*np.pi*0.5*seg))
            for s in range(2):  # сердцебиение
                for off in (0, 0.22):
                    ts = t0 + s*bar/2 + off; j0 = int(ts*SR); j1 = min(n, j0 + int(0.2*SR))
                    if j0 >= n: continue
                    ss = tt[j0:j1] - ts
                    mus[j0:j1] += 0.3 * np.exp(-ss*25) * np.sin(2*np.pi*(45 + 40*np.exp(-ss*30))*ss)
            continue
        if mood == "rewind":
            ss = seg; mus[i0:i1] += 0.05 * env * np.sin(2*np.pi*(300 + 900*((ss*3) % 1))*ss)
            continue
        vol = 1.0 if mood == "happy" else 0.6
        for m in ch: mus[i0:i1] += 0.04*vol*env*np.sin(2*np.pi*f(m)*seg)
        mus[i0:i1] += 0.06*vol*env*np.sin(2*np.pi*f(ch[0] - 12)*seg)
        for s in range(8):
            m = ch[s % 3] + (12 if s >= 4 else 0) + 12
            ts = t0 + s*beat/2; j0 = int(ts*SR); j1 = min(n, j0 + int(0.4*SR))
            if j0 >= n: break
            ss = tt[j0:j1] - ts; mus[j0:j1] += 0.05*vol*np.exp(-ss*9)*np.sin(2*np.pi*f(m)*ss)
        if mood == "happy":
            for s in range(4):
                ts = t0 + s*beat; j0 = int(ts*SR); j1 = min(n, j0 + int(0.25*SR))
                if j0 >= n: break
                ss = tt[j0:j1] - ts; mus[j0:j1] += 0.14*np.exp(-ss*18)*np.sin(2*np.pi*(50 + 80*np.exp(-ss*30))*ss)
    voice = np.zeros(n); sfx = np.zeros(n)
    rng = np.random.default_rng(1)
    for p in PLAN:
        for st, a, v, txt, key in p["clips"]:
            j0 = int(st*SR); voice[j0:j0 + len(a)] += a[:n - j0] * (0.0 if NO_VOICE else 0.9)
        for st, a in p.get("extra", []):
            j0 = int(st*SR); voice[j0:j0 + len(a)] += a[:n - j0] * (0.0 if NO_VOICE else 0.95)
        if p["fn"] is sc_night:  # укус
            ts = p["start"] + p["marks"]["n5"][0] + 0.0
            ts = p["start"] + p["marks"]["n5"][0]
            j0 = int(ts*SR); L = int(0.35*SR); ss = np.arange(L)/SR
            sfx[j0:j0+L] += 0.5*np.exp(-ss*14)*(rng.standard_normal(L)*0.6 + np.sin(2*np.pi*120*ss))
        if p["fn"] is sc_rewind:
            j0 = int(p["start"]*SR); L = int(1.2*SR); ss = np.arange(L)/SR
            sfx[j0:j0+L] += 0.18*np.sin(2*np.pi*(1500*ss - 500*ss**2))*np.exp(-ss*1.5)
        if p["fn"] is sc_verdict:
            j0 = int(p["start"]*SR); L = int(2.5*SR); ss = np.arange(L)/SR
            sfx[j0:j0+L] += 0.35*np.exp(-ss*1.5)*np.sin(2*np.pi*55*ss)
    # «приглушение» музыки под голос
    env = np.convolve(np.abs(voice), np.ones(int(0.15*SR))/int(0.15*SR), mode="same")
    duck = 1 - 0.6*np.clip(env*12, 0, 1)
    fade = np.clip(np.minimum(tt/1.0, (TOTAL - tt)/1.5), 0, 1)
    out = np.tanh((mus*duck*fade*0.9 + sfx + voice) * 1.1) * 0.9
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((out[:int(TOTAL*SR)]*32767).astype(np.int16).tobytes())

def main():
    init()
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        for sec in map(float, sys.argv[2:]):
            surf = cairo.ImageSurface.create_for_data(bytearray(frame(int(sec*FPS))), cairo.FORMAT_ARGB32, W, H)
            surf.write_to_png(os.path.join(HERE, f"preview_{sec:05.1f}.png"))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "timeline":
        for p in PLAN: print(f"{p['start']:6.1f}  {p['fn'].__name__:12s} {p['dur']:5.1f}s", {k: round(v[0], 1) for k, v in p['marks'].items()})
        print("ВСЕГО", round(TOTAL, 1)); return
    wav = os.path.join(HERE, "_story.wav"); soundtrack(wav)
    nf = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    with Pool() as pool:
        for i, fr in enumerate(pool.imap(frame, range(nf), chunksize=8)):
            ff.stdin.write(fr)
            if i % 300 == 0: print(f"кадр {i}/{nf}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print("готово:", OUT, f"({TOTAL:.1f} с)")

if __name__ == "__main__":
    main()
