#!/usr/bin/env python3
"""NEWS-23 B163 heroes-scene: THE WORLD TODAY, Monday 23 November 2026."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
NAVY = (14, 26, 46)
NAVY2 = (24, 42, 74)
GOLD = (201, 162, 39)
GOLD_L = (232, 196, 90)
RED = (176, 30, 36)
RED_BG = (246, 226, 226)
TEAL = (16, 92, 96)
GREEN = (22, 120, 66)
GREY = (90, 90, 90)
LINE = (200, 192, 175)
CARD_BG = (255, 255, 255)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(draw, text, f):
    return draw.textlength(text, font=f)


def fit(draw, text, f, maxw, min_size=9):
    """Shrink font size until text fits maxw."""
    size = f.size
    while size > min_size and tw(draw, text, font(f.path, size)) > maxw:
        size -= 1
    return font(f.path, size)


def wrap(draw, text, f, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(draw, t, f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def chip(draw, x, y, label, fill):
    f = font(F_SANSB, 10)
    w = int(tw(draw, label, f)) + 10
    draw.rounded_rectangle([x, y, x + w, y + 14], radius=3, fill=fill)
    draw.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- MASTHEAD ----------
    d.rectangle([0, 0, W, 56], fill=NAVY)
    f_mast = font(F_SERIF, 34)
    d.text((16, 8), "THE WORLD TODAY", font=f_mast, fill=(255, 255, 255))
    f_date = font(F_SANSB, 14)
    d.text((W - 16 - tw(d, "MONDAY 23 NOVEMBER 2026", f_date), 20),
           "MONDAY 23 NOVEMBER 2026", font=f_date, fill=GOLD_L)
    d.rectangle([0, 56, W, 59], fill=GOLD)

    # ---------- KICKER ----------
    f_kick = font(F_SANSB, 12)
    kick = "THE DAY IN ONE PAGE  —  MARKETS, POWER AND THE RACE TO GOVERN AI"
    d.text((16, 66), kick, font=f_kick, fill=RED)

    # ---------- NUMBER STRIP ----------
    nums = [("-3.3%", "KOSPI FALLS"), ("5.3", "US-CHINA GAP"),
            ("11,762", "EBOLA CASES, DRC"), ("10T WON", "SEOUL RESCUE FUND"),
            ("2%", "BILLIONAIRE TAX"), ("$450M", "SKUBAL DEAL"),
            ("165", "MISSILES / WEEK"), ("12,000", "MANCHESTER CLEARED"),
            ("264 KG", "LEBANON SEIZURE"), ("$107.3B", "ANTHROPIC IPO")]
    d.rectangle([0, 86, W, 132], fill=(255, 255, 255))
    d.line([0, 86, W, 86], fill=LINE, width=1)
    d.line([0, 132, W, 132], fill=LINE, width=1)
    colw = (W - 32) / 5
    for i, (v, lab) in enumerate(nums):
        row, col = divmod(i, 5)
        x = 16 + col * colw
        y = 88 + row * 22
        fv = font(F_SANSB, 15)
        fl = font(F_SANS, 8)
        d.text((x, y), v, font=fv, fill=NAVY)
        d.text((x, y + 1), " " * 0, font=fl, fill=GREY)
        # label under value, right-aligned to value width is risky; place below
        d.text((x, y + 15), lab, font=fl, fill=GREY) if False else None
    # redo strip cleanly: value row then label row per cell
    d.rectangle([0, 86, W, 132], fill=(255, 255, 255))
    d.line([0, 86, W, 86], fill=LINE, width=1)
    d.line([0, 132, W, 132], fill=LINE, width=1)
    for i, (v, lab) in enumerate(nums):
        row, col = divmod(i, 5)
        x = 16 + col * colw
        y = 88 + row * 22
        fv = font(F_SANSB, 14)
        fl = font(F_SANS, 8)
        d.text((x, y), v, font=fv, fill=NAVY)
        d.text((x, y + 14), lab, font=fl, fill=GREY)

    # ---------- REGION BAR ----------
    f_reg = font(F_SANSB, 11)
    regions = "ASIA-PACIFIC 7   ·   AMERICAS 8   ·   MIDDLE EAST 6   ·   EUROPE 5   ·   AFRICA 3   ·   WORLD 2"
    d.rectangle([0, 134, W, 154], fill=NAVY2)
    d.text((16, 139), regions, font=f_reg, fill=(255, 255, 255))

    # ---------- HEROES ----------
    heroes = [
        dict(head="AI ROUT HITS ASIA",
             body="Kospi sheds 161 pts; Samsung -3.1%, SK Hynix -2.5%.",
             src="REUTERS", kind="kospi"),
        dict(head="GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
             body="150 delegates back a risk framework in Bridgetown.",
             src="AP", kind="guterres"),
        dict(head="US LEAD OVER CHINA AT RECORD LOW",
             body="Gap 5.3, narrowest since 2018; India 3rd at 40.5.",
             src="LOWY INSTITUTE", kind="power"),
    ]
    hx0, hy0 = 16, 160
    hcol = 324
    hgap = 8
    scene_h = 150
    for i, hero in enumerate(heroes):
        x = hx0 + i * (hcol + hgap)
        y = hy0
        # scene
        if hero["kind"] == "kospi":
            draw_kospi(d, x, y, hcol, scene_h)
        elif hero["kind"] == "guterres":
            draw_guterres(d, x, y, hcol, scene_h)
        else:
            draw_power(d, x, y, hcol, scene_h)
        # headline below scene
        fh = font(F_SANSB, 15)
        lines = wrap(d, hero["head"], fh, hcol)
        yy = y + scene_h + 6
        for ln in lines[:2]:
            d.text((x, yy), ln, font=fh, fill=INK)
            yy += 18
        fb = font(F_SANS, 11)
        blines = wrap(d, hero["body"], fb, hcol)
        for ln in blines[:2]:
            d.text((x, yy), ln, font=fb, fill=(40, 40, 40))
            yy += 14
        # source + chip
        fs = font(F_SANSB, 9)
        d.text((x, yy + 2), hero["src"], font=fs, fill=GREY)
        chip(d, x + tw(d, hero["src"], fs) + 8, yy, "REPORTED", GREEN)

    # ---------- MORE OF THE DAY BAR ----------
    d.rectangle([0, 396, W, 416], fill=INK)
    d.text((16, 401), "MORE OF THE DAY", font=font(F_SANSB, 12), fill=(255, 255, 255))

    # ---------- CARDS (10) ----------
    cards = [
        ("BESSENT DEMANDS NVIDIA ANSWERS", "Treasury presses chipmaker.", "REPORTED"),
        ("FBI PROBES NCIC HACK", "Police database breach probed.", "REPORTED"),
        ("IRAN STRIKES MAY RESUME", "Trump: may resume in New Year.", "REPORTED"),
        ("NASDAQ FUTURES +3%", "Holiday week lifts futures.", "REPORTED"),
        ("SKUBAL'S $450M METS DEAL", "Nine years, pitcher record.", "REPORTED"),
        ("TOM JACKSON DIES AT 75", "NFL star turned broadcaster.", "REPORTED"),
        ("STATES SUE SPACEX", "AI safety claims challenged.", "REPORTED"),
        ("ANTHROPIC IPO $107.3B", "Priced $83; debut close $97.17.", "REPORTED"),
        ("POLAND: 3 KH-101 CROSSED", "Missiles crossed airspace.", "CLAIM"),
        ("RUSSIAN NUCLEAR SATELLITE?", "Intel warns of orbital threat.", "CLAIM"),
    ]
    cw = (W - 32 - 4 * 8) / 5
    chh = 62
    for i, (head, body, tag) in enumerate(cards):
        row, col = divmod(i, 5)
        x = 16 + col * (cw + 8)
        y = 424 + row * (chh + 8)
        d.rectangle([x, y, x + cw, y + chh], fill=CARD_BG, outline=LINE)
        fh = font(F_SANSB, 11)
        fhb = fit(d, head, fh, cw - 10)
        d.text((x + 5, y + 4), head, font=fhb, fill=INK)
        fb = font(F_SANS, 10)
        d.text((x + 5, y + 22), body, font=fb, fill=(60, 60, 60))
        chip(d, x + 5, y + chh - 19, tag, GREEN if tag == "REPORTED" else RED)

    # ---------- MAP + ALSO ----------
    my = 566
    d.text((16, my), "THE WORLD IN 13 PINS", font=font(F_SANSB, 12), fill=NAVY)
    d.text((516, my), "ALSO ON MONDAY", font=font(F_SANSB, 12), fill=NAVY)
    map_x0, map_y0, map_x1, map_y1 = 16, my + 20, 500, 836
    d.rectangle([map_x0, map_y0, map_x1, map_y1], fill=(232, 238, 244),
                outline=LINE)
    draw_map(d, map_x0, map_y0, map_x1, map_y1)
    also = [
        "Paris: 100+ back 2% billionaire tax",
        "Manchester: 12,000 cleared",
        "Zelenskyy: 165 Russian missiles in a week",
        "COP31: the day after Antalya pact rejected",
        "Israel unity talks resume",
        "Gaza: two killed in Israeli strike",
        "West Bank settler attacks",
        "Iran war: no deal in sight",
        "Lebanon seizes 264 kg explosives",
        "Bahrain: Iranian strike hits plant, 2 hurt",
        "Benghazi: UN demands port probe [CLAIM]",
        "Sudan: drones downed over Khartoum [CLAIM]",
        "DRC: fighting traps Ebola teams",
        "Bangladesh: Hasina jailed if she returns",
        "Seoul minister quits over AI exam chaos",
        "SK Telecom -7.3%",
        "China eases margin rules to 80%",
        "Seoul readies 10T-won stabilisation fund",
    ]
    fa = font(F_SANS, 11)
    for i, item in enumerate(also):
        col, row = divmod(i, 9)
        x = 516 + col * 250
        y = my + 22 + row * 17
        fitem = fit(d, item, fa, 244)
        d.text((x, y), item, font=fitem, fill=INK)

    # ---------- DATE CHECK ----------
    dy = 848
    d.rectangle([16, dy, W - 16, 968], fill=RED_BG, outline=RED, width=2)
    d.text((24, dy + 6), "DATE CHECK — LEFT OUT (NOT 23 NOVEMBER)",
           font=font(F_SANSB, 12), fill=RED)
    left = ["Democrats reach 258  (22 Nov)", "Sparta II fire  (22 Nov)",
            "El Chapo Isidro captured  (22 Nov)", "EU-Indonesia pact  (21 Nov)",
            "Nigeria boat  (21 Nov)", "ICJ Myanmar ruling  (19 Nov)"]
    fd = font(F_SANS, 11)
    for i, item in enumerate(left):
        col, row = divmod(i, 3)
        d.text((24 + col * 330, dy + 26 + row * 15), "✕  " + item, font=fd, fill=INK)
    d.text((24, dy + 76), "NOT YET:",
           font=font(F_SANSB, 11), fill=RED)
    notyet = ["Dymer search continues (14 missing)", "4 House races uncalled",
              "COP32 venue not set", "WHO evacuating trapped Ebola staff"]
    for i, item in enumerate(notyet):
        col, row = divmod(i, 2)
        d.text((24 + col * 330, dy + 92 + row * 15), "○  " + item, font=fd, fill=INK)

    # ---------- FOOTER ----------
    d.rectangle([0, 976, W, H], fill=NAVY)
    d.text((16, 984), "SOURCES: REUTERS · AP · LOWY INSTITUTE · WIRE REPORTS",
           font=font(F_SANS, 10), fill=(200, 200, 200))
    d.text((16, 1000), "THE WORLD TODAY · Monday 23 November 2026 · 31 stories · 6 regions",
           font=font(F_SANSB, 10), fill=GOLD_L)
    d.line([0, 976, W, 976], fill=GOLD, width=2)
    return img


def draw_kospi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # skyline
    import random
    rnd = random.Random(7)
    bx = x + 6
    while bx < x + w - 30:
        bw = rnd.randint(18, 30)
        bh = rnd.randint(45, 95)
        by = y + h - bh - 22
        d.rectangle([bx, by, bx + bw, y + h - 22], fill=(30, 52, 92))
        for wy in range(by + 6, y + h - 26, 10):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rnd.random() < 0.6:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=GOLD_L)
        bx += bw + 4
    # chart line descending, kept in upper area away from big number
    pts = [(x + 10, y + 30), (x + 70, y + 42), (x + 130, y + 38),
           (x + 190, y + 55), (x + 250, y + 70), (x + 310, y + 88)]
    d.line(pts, fill=(255, 120, 40), width=3)
    d.text((x + 10, y + 6), "-3.3%", font=font(F_SANSB, 26), fill=(255, 255, 255))
    # caption band at bottom
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(10, 18, 34))
    fc = font(F_SANSB, 10)
    cap = "KOSPI 4,708.54 · -161 PTS · SAMSUNG -3.1% · HYNIX -2.5%"
    fcap = fit(d, cap, fc, w - 8)
    d.text((x + 4, y + h - 18), cap, font=fcap, fill=GOLD_L)


def draw_guterres(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TEAL)
    # globe on right
    cx, cy, r = x + w - 62, y + 62, 44
    mask = Image.new("L", (2 * r, 2 * r), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, 2 * r, 2 * r], fill=255)
    globe = Image.new("RGB", (2 * r, 2 * r), (46, 130, 160))
    gd = ImageDraw.Draw(globe)
    for k in range(-2, 3):
        gd.ellipse([r + k * 18 - 10, 4, r + k * 18 + 10, 2 * r - 4],
                   outline=(180, 220, 230))
    for k in range(1, 4):
        gd.line([4, k * r // 2, 2 * r - 4, k * r // 2], fill=(180, 220, 230))
    gd.ellipse([r - 26, r - 30, r + 6, r + 18], fill=(90, 170, 110))
    d._image.paste(globe, (cx - r, cy - r), mask)
    # gold headline text on left
    fg = font(F_SANSB, 17)
    d.text((x + 8, y + 10), "REGULATE AI", font=fg, fill=GOLD_L)
    d.text((x + 8, y + 32), "BEFORE IT'S", font=fg, fill=GOLD_L)
    d.text((x + 8, y + 54), "TOO LATE", font=fg, fill=GOLD_L)
    d.text((x + 8, y + 82), "150 DELEGATES", font=font(F_SANSB, 12), fill=(255, 255, 255))
    d.text((x + 8, y + 100), "BRIDGETOWN", font=font(F_SANSB, 12), fill=(255, 255, 255))
    # small flags row at bottom
    cols = [(200, 60, 60), (255, 255, 255), (60, 120, 200), (255, 200, 60)]
    for i, c in enumerate(cols):
        fx = x + 8 + i * 26
        d.rectangle([fx, y + h - 20, fx + 20, y + h - 8], fill=c, outline=(255, 255, 255))


def draw_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=LINE)
    d.text((x + 8, y + 8), "ASIA POWER INDEX 2026", font=font(F_SANSB, 12), fill=NAVY)
    bars = [("US", 78.9, NAVY), ("CHINA", 73.6, RED), ("INDIA", 40.5, GOLD)]
    maxw = w - 90
    for i, (name, val, col) in enumerate(bars):
        by = y + 36 + i * 32
        d.text((x + 8, by), name, font=font(F_SANSB, 12), fill=INK)
        bw = int(maxw * val / 80)
        d.rectangle([x + 70, by + 2, x + 70 + bw, by + 16], fill=col)
        d.text((x + 76 + bw, by + 1), f"{val}", font=font(F_SANSB, 12), fill=INK)
    d.text((x + 8, y + h - 24), "GAP 5.3 — NARROWEST SINCE 2018",
           font=font(F_SANSB, 11), fill=RED)


def draw_map(d, x0, y0, x1, y1):
    # rough continent blobs
    d.polygon([(x0 + 30, y0 + 60), (x0 + 90, y0 + 30), (x0 + 150, y0 + 55),
               (x0 + 140, y0 + 130), (x0 + 110, y0 + 200), (x0 + 60, y0 + 190),
               (x0 + 35, y0 + 130)], fill=(190, 205, 190))
    d.polygon([(x0 + 200, y0 + 40), (x0 + 330, y0 + 25), (x0 + 450, y0 + 45),
               (x0 + 460, y0 + 110), (x0 + 380, y0 + 130), (x0 + 300, y0 + 120),
               (x0 + 220, y0 + 100)], fill=(190, 205, 190))
    d.polygon([(x0 + 250, y0 + 140), (x0 + 310, y0 + 135), (x0 + 330, y0 + 180),
               (x0 + 300, y0 + 210), (x0 + 260, y0 + 205)], fill=(190, 205, 190))
    pins = [
        (1, "Seoul", 420, 660), (2, "Bridgetown", 120, 760),
        (3, "Washington", 90, 640), (4, "Paris", 262, 672),
        (5, "London", 245, 645), (6, "Manchester", 215, 632),
        (7, "Gaza", 295, 712), (8, "Beirut", 312, 682),
        (9, "Kyiv", 335, 640), (10, "Khartoum", 310, 770),
        (11, "Kinshasa", 272, 775), (12, "Benghazi", 282, 738),
        (13, "Bahrain", 330, 715),
    ]
    # pins are in absolute coords relative to image; map box starts at (16,586)
    f_pin = font(F_SANSB, 9)
    for n, name, px, py in pins:
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        d.text((px - 3, py - 7), str(n), font=f_pin, fill=(255, 255, 255))
    # legend rows under blob
    legend = [
        "1 Seoul  2 Bridgetown  3 Washington  4 Paris  5 London",
        "6 Manchester  7 Gaza  8 Beirut  9 Kyiv  10 Khartoum",
        "11 Kinshasa  12 Benghazi  13 Bahrain",
    ]
    fl = font(F_SANS, 10)
    ly = y1 - 44
    for ln in legend:
        d.text((x0 + 8, ly), ln, font=fl, fill=(40, 40, 40))
        ly += 15


if __name__ == "__main__":
    img = draw()
    img.save("entry.png")
    print("saved entry.png", img.size)
