"""Видео 9:16: «Существуют ли Real Potosí, Barcelona SC, L. Ñesi и C. Orlando?»
Использует движок story.py (озвучка RHVoice + субтитры). Запуск: python3 football.py [preview 3 10 | timeline]
"""
import math, os
import story
from story import *  # примитивы, персонажи, subtitle, at, S

BSC_Y, BSC_D = hexc("ffd60a"), hexc("1d1d1d")
RP_P, RP_W = hexc("7b2cbf"), hexc("ffffff")

def shield(ctx, x, y, s, c1, c2, label):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-80, -90); ctx.line_to(80, -90); ctx.line_to(80, 10)
    ctx.curve_to(80, 60, 30, 90, 0, 110); ctx.curve_to(-30, 90, -80, 60, -80, 10); ctx.close_path()
    col(ctx, c1); ctx.fill_preserve(); ctx.set_line_width(10); col(ctx, c2); ctx.stroke()
    ctx.rectangle(-80, -20, 160, 36); col(ctx, c2); ctx.fill()
    text(ctx, label, 0, 10, 34, c1)
    ctx.restore()

def ball(ctx, x, y, r, rot=0.0):
    circle(ctx, x, y, r, WHITE)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.move_to(0, -r*0.38)
    for i in range(1, 5):
        a = -math.pi/2 + i*2*math.pi/5; ctx.line_to(math.cos(a)*r*0.38, math.sin(a)*r*0.38)
    ctx.close_path(); col(ctx, INK); ctx.fill()
    for i in range(5):
        a = -math.pi/2 + i*2*math.pi/5
        line(ctx, math.cos(a)*r*0.38, math.sin(a)*r*0.38, math.cos(a)*r, math.sin(a)*r, r*0.08, INK)
    ctx.restore()
    ctx.set_line_width(r*0.08); ctx.arc(x, y, r, 0, 2*math.pi); col(ctx, INK); ctx.stroke()

def player(ctx, x, y, s, shirt, num, **kw):
    person(ctx, x, y, s, shirt=shirt, pants=WHITE if shirt != WHITE else INK, **kw)
    ctx.save(); ctx.translate(x, y + kw.get("bob", 0)); ctx.scale(s, s)
    text(ctx, str(num), 0, -160, 50, INK if shirt in (BSC_Y, WHITE) else WHITE)
    ctx.restore()

def flag(ctx, x, y, w, h, colors):
    if colors == "EC":
        parts = [(BSC_Y, 0.5), (hexc("034ea2"), 0.25), (hexc("ed1c24"), 0.25)]
    else:
        parts = [(hexc("d52b1e"), 1/3), (hexc("f9e300"), 1/3), (hexc("007934"), 1/3)]
    yy = y
    for c, f in parts:
        col(ctx, c); ctx.rectangle(x, yy, w, h*f); ctx.fill(); yy += h*f
    line(ctx, x, y, x, y + h + 120, 10, GREY)

def match_card(ctx, x, y, w, t, goals=True, glitch=0.0):
    col(ctx, WHITE); rrect(ctx, x, y, w, 520, 30); ctx.fill()
    text(ctx, "Финал", x + w/2, y + 60, 34, GREY, bold=False)
    shield(ctx, x + 95, y + 190, 0.6, BSC_Y, BSC_D, "BSC")
    shield(ctx, x + w - 95, y + 190, 0.6, RP_P, RP_W, "RP")
    text(ctx, "3 – 3", x + w/2, y + 225, 86, INK)
    text(ctx, "Barcelona SC", x + 130, y + 330, 30, INK)
    text(ctx, "Real Potosí", x + w - 130, y + 330, 30, INK)
    if goals:
        for i in range(3):
            text(ctx, f"L. Ñesi {12 + i*25}'", x + 130, y + 395 + i*40, 30, INK, bold=False)
            text(ctx, f"C. Orlando {20 + i*23}'", x + w - 130, y + 395 + i*40, 30, INK, bold=False)
    if glitch > 0:
        for i in range(8):
            gy = y + ((i*67 + t*900) % 520)
            col(ctx, [CORAL, TEAL, YELLOW][i % 3], 0.5*glitch); ctx.rectangle(x + (i*37 % 60) - 30, gy, w, 10 + i % 3*8); ctx.fill()

def phone(ctx, cx, cy, t, k_card, glitch=0.0):
    w, h = 640, 1180; x, y = cx - w/2, cy - h/2
    col(ctx, (0, 0, 0), 0.25); rrect(ctx, x + 14, y + 20, w, h, 70); ctx.fill()
    col(ctx, hexc("111111")); rrect(ctx, x, y, w, h, 70); ctx.fill()
    col(ctx, hexc("2b2d42")); rrect(ctx, x + 24, y + 24, w - 48, h - 48, 50); ctx.fill()
    col(ctx, hexc("111111")); rrect(ctx, cx - 70, y + 40, 140, 34, 17); ctx.fill()
    with Pop(ctx, cx, y + 520, k_card):
        match_card(ctx, x + 50, y + 260, w - 100, t, glitch=glitch)
    for i, (ic, n) in enumerate((("♥", "2,4M"), ("…", "18K"), ("➦", "95K"))):
        circle(ctx, x + w - 80, y + 860 + i*100, 34, WHITE, 0.15)
        text(ctx, ic, x + w - 80, y + 873 + i*100, 36, CORAL if i == 0 else WHITE)
        text(ctx, n, x + w - 80, y + 920 + i*100, 22, WHITE, bold=False)
    text(ctx, "#futbol #meme", x + 60, y + 1100, 30, WHITE, align="left")

def stamp(ctx, x, y, label, c, k, rot=-0.18):
    if k <= 0: return
    s = 1 + (1 - ease_out(k)) * 1.5
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(70)
    w = ctx.text_extents(label).x_advance + 80
    ctx.set_line_width(12); rrect(ctx, -w/2, -65, w, 130, 24); col(ctx, c, clamp(k*2)); ctx.stroke()
    text(ctx, label, 0, 25, 70, c, a=clamp(k*2))
    ctx.restore()

# ---------- сцены ----------
def sc_hook(ctx, t, d, M):
    phone(ctx, W/2, 860, t, prog(t, 0.2, 0.6), glitch=0)
    k = prog(t, at(M, "q2"), 0.5)
    with Pop(ctx, W/2, 220, k):
        col(ctx, YELLOW); rrect(ctx, 200, 140, W - 400, 140, 70); ctx.fill()
        text(ctx, "Это правда?", W/2, 235, 70, INK)

def sc_bsc(ctx, t, d, M):
    title(ctx, "Barcelona SC", t, y=230, c=INK, size=96)
    with Pop(ctx, 270, 560, prog(t, 0.2, 0.5)):
        shield(ctx, 270, 560, 1.5, BSC_Y, BSC_D, "BSC")
    with Pop(ctx, 760, 560, prog(t, at(M, "b1", 0.3), 0.5)):
        flag(ctx, 640, 420, 240, 160, "EC")
        text(ctx, "Гуаякиль,", 760, 760, 44, INK); text(ctx, "Эквадор", 760, 815, 44, INK)
    facts = [("1925", "год основания", "b1", 0.65), ("Монументаль", "домашний стадион", "b2", 0.15),
             ("1990 · 1998", "финалы Кубка Либертадорес", "b2", 0.55)]
    for i, (big, small, key, fr) in enumerate(facts):
        k = prog(t, at(M, key, fr), 0.5)
        y = 920 + i*200
        with Pop(ctx, W/2, y + 80, k):
            col(ctx, WHITE); rrect(ctx, 90, y, W - 180, 170, 36); ctx.fill()
            col(ctx, BSC_Y); rrect(ctx, 90, y, 26, 170, 13); ctx.fill()
            text(ctx, big, 150, y + 85, 60, INK, align="left"); text(ctx, small, 150, y + 135, 36, GREY, bold=False, align="left")
    stamp(ctx, 760, 420, "СУЩЕСТВУЕТ", hexc("2a9d8f"), prog(t, at(M, "b3"), 0.4))

def sc_rp(ctx, t, d, M):
    title(ctx, "Real Potosí", t, y=230, c=WHITE, size=96)
    # гора со стадионом
    with Pop(ctx, W/2, 900, prog(t, 0.2, 0.6)):
        ctx.move_to(60, 1180); ctx.line_to(420, 560); ctx.line_to(620, 820); ctx.line_to(760, 640); ctx.line_to(1040, 1180)
        ctx.close_path(); col(ctx, hexc("6d597a")); ctx.fill()
        ctx.move_to(420, 560); ctx.line_to(490, 680); ctx.line_to(450, 660); ctx.line_to(400, 700); ctx.line_to(360, 660); ctx.close_path()
        col(ctx, WHITE); ctx.fill()
        col(ctx, hexc("40916c")); rrect(ctx, 300, 1040, 480, 140, 20); ctx.fill()
        ctx.set_line_width(5); rrect(ctx, 320, 1055, 440, 110, 10); col(ctx, WHITE); ctx.stroke()
        line(ctx, 540, 1055, 540, 1165, 5, WHITE)
        for i in range(3):
            pp = player
            pp(ctx, 380 + i*160, 1160 + 0, 0.32, RP_P if i != 1 else BSC_Y, 7 + i, leg=t*8 + i, bob=-abs(math.sin(t*6 + i))*8,
               face="sick" if i == 1 else "happy")
        ball(ctx, 540 + math.sin(t*2)*150, 1140 - abs(math.sin(t*4))*40, 14, rot=t*5)
    k = prog(t, at(M, "r1", 0.55), 0.5)
    with Pop(ctx, 860, 520, k):
        col(ctx, WHITE); rrect(ctx, 700, 420, 320, 200, 30); ctx.fill()
        text(ctx, "≈4000 м", 860, 510, 64, RP_P); text(ctx, "над уровнем моря", 860, 570, 30, INK, bold=False)
    with Pop(ctx, 220, 500, prog(t, at(M, "r1", 0.2), 0.5)):
        flag(ctx, 110, 400, 220, 140, "BO")
        text(ctx, "Потоси, Боливия", 220, 360, 40, WHITE)
    k = prog(t, at(M, "r2", 0.3), 0.5)
    with Pop(ctx, W/2, 1330, k):
        col(ctx, WHITE); rrect(ctx, 90, 1240, W - 180, 170, 36); ctx.fill()
        col(ctx, RP_P); rrect(ctx, 90, 1240, 26, 170, 13); ctx.fill()
        text(ctx, "2007", 150, 1325, 60, INK, align="left"); text(ctx, "чемпион Боливии (Апертура)", 150, 1375, 36, GREY, bold=False, align="left")
    stamp(ctx, W/2, 760, "СУЩЕСТВУЕТ", hexc("06d6a0"), prog(t, at(M, "r3"), 0.4))

def sc_players(ctx, t, d, M):
    title(ctx, "L. Ñesi и C. Orlando", t, y=230, c=WHITE, size=80)
    for i, (x, shirt, name) in enumerate(((300, BSC_Y, "L. Ñesi"), (780, RP_P, "C. Orlando"))):
        k = prog(t, 0.3 + i*0.3, 0.5)
        with Pop(ctx, x, 900, k):
            ctx.push_group()
            player(ctx, x, 1150, 1.3, shirt, 9 if i == 0 else 11, face="happy", arm_l=20, arm_r=20)
            ctx.pop_group_to_source(); ctx.paint_with_alpha(0.35 if t > at(M, "p2") else 1.0)
            circle(ctx, x, 1150 - 1.3*305, 70, hexc("2b2d42"), 0.85 if t > at(M, "p1", 0.5) else 0)
            if t > at(M, "p1", 0.5): text(ctx, "?", x, 1150 - 1.3*305 + 35, 110, YELLOW)
            col(ctx, WHITE); rrect(ctx, x - 190, 1200, 380, 90, 30); ctx.fill()
            text(ctx, name, x, 1260, 46, INK)
    # лупа ищет
    if at(M, "p1") < t:
        lx = 540 + math.sin(t*2.2)*300; ly = 620 + math.cos(t*1.7)*90
        ctx.new_path(); ctx.set_line_width(22); ctx.arc(lx, ly, 80, 0, 2*math.pi); col(ctx, WHITE); ctx.stroke()
        circle(ctx, lx, ly, 70, SKY, 0.25)
        line(ctx, lx + 58, ly + 58, lx + 120, ly + 120, 30, WHITE)
    k = prog(t, at(M, "p2"), 0.5)
    with Pop(ctx, W/2, 1440, k):
        col(ctx, RED); rrect(ctx, 90, 1350, W - 180, 170, 36); ctx.fill()
        text(ctx, "В составах не найдены", W/2, 1430, 52, WHITE)
        text(ctx, "Barcelona SC · Real Potosí", W/2, 1490, 34, WHITE, bold=False)

def sc_fake(ctx, t, d, M):
    title(ctx, "Матч 3:3?", t, y=230, c=INK)
    g = prog(t, at(M, "m1", 0.3), 0.6)
    phone(ctx, W/2, 900, t, 1.0, glitch=g)
    # «слои» как в графическом редакторе
    k = prog(t, at(M, "m1", 0.5), 0.5)
    with Pop(ctx, 860, 520, k):
        for i, ln in enumerate(("Слой: счёт 3–3", "Слой: голы", "Фон")):
            col(ctx, WHITE); rrect(ctx, 690, 400 + i*80, 340, 66, 14); ctx.fill()
            col(ctx, TEAL if i < 2 else GREY); rrect(ctx, 704, 414 + i*80, 38, 38, 8); ctx.fill()
            text(ctx, ln, 756, 445 + i*80, 26, INK, bold=False, align="left")
    stamp(ctx, W/2, 900, "ФОТОМОНТАЖ", RED, prog(t, at(M, "m1", 0.75), 0.4))
    k = prog(t, at(M, "m2", 0.1), 0.5)
    with Pop(ctx, W/2, 1380, k):
        col(ctx, NAVY); rrect(ctx, 90, 1300, W - 180, 150, 36); ctx.fill()
        text(ctx, "🎮", W/2 - 330, 1515, 60, WHITE) if False else None
        ctx.set_line_width(8); rrect(ctx, 140, 1340, 110, 70, 30); col(ctx, WHITE); ctx.stroke()
        circle(ctx, 172, 1375, 8, WHITE); circle(ctx, 220, 1368, 7, CORAL); circle(ctx, 232, 1382, 7, YELLOW)
        text(ctx, "Похоже на «игровые»", 600, 1365, 40, WHITE)
        text(ctx, "имена без лицензии", 600, 1415, 40, WHITE)

def sc_verdict(ctx, t, d, M):
    title(ctx, "Итог", t, y=230, c=WHITE, size=110)
    rows = [("Barcelona SC", True, "v1", 0.15), ("Real Potosí", True, "v1", 0.35),
            ("L. Ñesi", False, "v1", 0.6), ("C. Orlando", False, "v1", 0.75), ("Матч 3:3", False, "v1", 0.9)]
    for i, (name, ok, key, fr) in enumerate(rows):
        k = prog(t, at(M, key, fr), 0.4)
        y = 360 + i*215
        with Pop(ctx, W/2, y + 85, k):
            col(ctx, WHITE); rrect(ctx, 90, y, W - 180, 175, 40); ctx.fill()
            (check if ok else cross)(ctx, 190, y + 88, 1.3)
            text(ctx, name, 280, y + 85, 54, INK, align="left")
            text(ctx, "настоящий клуб" if ok else ("мем" if "Матч" not in name else "фотомонтаж"),
                 280, y + 135, 36, hexc("2a9d8f") if ok else RED, bold=False, align="left")
    k = prog(t, at(M, "v2"), 0.5)
    with Pop(ctx, W/2, 1500, k):
        col(ctx, YELLOW); rrect(ctx, 160, 1440, W - 320, 110, 55); ctx.fill()
        text(ctx, "Проверяй факты!", W/2, 1515, 56, INK)

story.SCENES[:] = [
    S(sc_hook, hexc("ff4d6d"), "happy", [
        ("q1", "N", "В соцсетях завирусился матч: Барселона против Реал Потоси, три-три. "
                    "Все голы забили Эль Ньеси и Си Орландо.", 0.8),
        ("q2", "N", "Но существуют ли эти клубы и игроки на самом деле?", 0.3)]),
    S(sc_bsc, hexc("fff3b0"), "happy", [
        ("b1", "N", "Барселона Спортинг Клаб — настоящий клуб из Гуаякиля, Эквадор. Основан в тысяча девятьсот двадцать пятом году.", 0.4),
        ("b2", "N", "Играет на стадионе Монументаль и дважды доходил до финала Кубка Либертадорес.", 0.3),
        ("b3", "N", "Существует!", 0.2)]),
    S(sc_rp, hexc("3c096c"), "happy", [
        ("r1", "N", "Реал Потоси — настоящий клуб из Боливии. Его стадион находится почти в четырёх тысячах метров над уровнем моря.", 0.4),
        ("r2", "N", "В две тысячи седьмом году клуб стал чемпионом Боливии.", 0.3),
        ("r3", "N", "Тоже существует!", 0.2)]),
    S(sc_players, hexc("2b2d42"), "dark", [
        ("p1", "N", "А вот Эль Ньеси и Си Орландо?", 0.4),
        ("p2", "N", "Игроков с такими именами в составах этих клубов не найти.", 0.4)]),
    S(sc_fake, hexc("caf0f8"), "calm", [
        ("m1", "N", "Картинка с матчем три-три и двумя хет-триками — это фотомонтаж, который стал мемом.", 0.4),
        ("m2", "N", "Такие имена напоминают выдуманных игроков из футбольных видеоигр без лицензии.", 0.4)]),
    S(sc_verdict, hexc("06d6a0"), "happy", [
        ("v1", "N", "Итог: Барселона и Реал Потоси — настоящие клубы. А Ньеси, Орландо и матч три-три — просто мем.", 0.4),
        ("v2", "N", "Проверяй факты, прежде чем верить!", 0.3)], tail=1.8),
]
story.OUT = os.path.join(story.HERE, "football_9x16.mp4")

if __name__ == "__main__":
    story.main()
