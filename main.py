# AINLOCKER — безопасная визуальная симуляция
# Установка: pip install pygame
# Запуск: python ainlocker.py
# ESC — выход в любой момент, F11 — полноэкранный режим.

import math
import random
import sys
import time
import pygame

pygame.init()
pygame.display.set_caption("AINLOCKER — SIMULATION")
W, H = 1100, 680
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
clock = pygame.time.Clock()

BLACK = (3, 3, 6)
RED = (255, 28, 38)
WHITE = (235, 238, 245)
DIM = (100, 12, 20)
FONT_NAME = "consolas"

def font(size, bold=False):
    return pygame.font.SysFont(FONT_NAME, size, bold=bold)

def centered(text, y, fnt, color, surface=screen):
    img = fnt.render(text, True, color)
    surface.blit(img, (surface.get_width()//2-img.get_width()//2, y))

def draw_scanlines(surface):
    w, h = surface.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 4):
        pygame.draw.line(overlay, (0, 0, 0, 75), (0, y), (w, y))
    surface.blit(overlay, (0, 0))

def project(point, angle, cx, cy, scale):
    x, y, z = point
    ca, sa = math.cos(angle), math.sin(angle)
    x, z = x*ca-z*sa, x*sa+z*ca
    # slight vertical tilt
    cb, sb = math.cos(-0.18), math.sin(-0.18)
    y, z = y*cb-z*sb, y*sb+z*cb
    depth = 4.2 + z
    factor = scale / max(1.0, depth)
    return int(cx + x*factor), int(cy + y*factor), depth

def make_skull_points():
    pts = []
    # Cranium: dense ellipsoid shell
    for lat_i in range(1, 25):
        lat = -math.pi/2 + math.pi*lat_i/26
        for lon_i in range(64):
            lon = 2*math.pi*lon_i/64
            x = 1.08*math.cos(lat)*math.cos(lon)
            y = 1.18*math.sin(lat) - 0.10
            z = 0.82*math.cos(lat)*math.sin(lon)
            # lower face narrows into jaw
            if y > 0.48:
                x *= 0.78
            pts.append((x, y, z, random.choice("$@#%&*+=:.()")))
    # cheek bones and jaw rim
    for side in (-1, 1):
        for i in range(35):
            t = i/34
            pts.append((side*(0.18+0.73*t), 0.42+0.38*math.sin(t*math.pi), 0.55+0.12*math.sin(t*math.pi), random.choice("$#.:")))
        for i in range(24):
            t = i/23
            pts.append((side*(0.18+0.52*t), 0.78+0.28*math.sin(t*math.pi), 0.52, random.choice("()[]")))
    # eye socket rings, dark voids are suggested by missing interior points
    for side in (-1, 1):
        for i in range(42):
            a = 2*math.pi*i/42
            x = side*0.43 + 0.28*math.cos(a)
            y = 0.05 + 0.30*math.sin(a)
            z = 0.70 + 0.04*math.cos(a)
            pts.append((x, y, z, random.choice("$@%&")))
    # nose bridge / triangular nose
    for i in range(18):
        t = i/17
        pts.append((0, -0.13+t*0.55, 0.78-0.12*t, random.choice(":;.")))
    # teeth rows
    for i in range(13):
        x = -0.48 + i*0.08
        for j in range(3):
            pts.append((x, 0.80+j*0.09, 0.58, random.choice("I|:")))
    return pts

SKULL = make_skull_points()
start = time.time()
phase = "intro"
phase_started = start
fullscreen = False
running = True
particles = [(random.randrange(W), random.randrange(H), random.uniform(0.3, 1.5)) for _ in range(90)]
countdown_start = time.time()

while running:
    dt = clock.tick(60) / 1000
    now = time.time()
    elapsed = now - phase_started
    width, height = screen.get_size()
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_F11:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if fullscreen else pygame.display.set_mode((W, H), pygame.RESIZABLE)

    # Floating digital dust
    for i, (px, py, speed) in enumerate(particles):
        py += speed
        if py > height:
            px, py = random.randrange(width), -5
        particles[i] = (px, py, speed)
        pygame.draw.circle(screen, (45, 8, 14), (int(px), int(py)), 1)

    angle = now * 0.72
    cx, cy = int(width*0.32), int(height*0.49)
    scale = min(width, height) * 1.38

    # 3D ASCII skull, depth-sorted for a real rotating point-cloud effect
    projected = []
    for x, y, z, glyph in SKULL:
        sx, sy, depth = project((x, y, z), angle, cx, cy, scale)
        if 0 <= sx < width and 0 <= sy < height:
            projected.append((depth, sx, sy, glyph))
    projected.sort(reverse=True)
    pulse = (math.sin(now*4.0)+1)/2
    for depth, sx, sy, glyph in projected:
        front = max(0.15, min(1.0, 1.45-depth/6))
        flicker = random.random() > 0.035
        if flicker:
            if int(now*3) % 3 == 0:
                base = WHITE
            elif int(now*3) % 3 == 1:
                base = RED
            else:
                base = (25, 25, 30)
            color = tuple(int(c*front) for c in base)
            ch = font(max(9, int(13*front)), True).render(glyph, True, color)
            screen.blit(ch, (sx, sy))

    # Header
    pygame.draw.line(screen, RED, (22, 48), (width-22, 48), 1)
    screen.blit(font(19, True).render("AINLOCKER v1.0.0  //  3D ASCII CORE", True, RED), (25, 17))
    right = font(17, True).render("[ SIMULATION MODE ]", True, WHITE)
    screen.blit(right, (width-right.get_width()-25, 19))

    if phase == "intro":
        centered("INITIALIZING VISUAL SEQUENCE...", int(height*0.82), font(22, True), WHITE)
        centered("ESC  —  EXIT SIMULATION", int(height*0.89), font(15), RED)
        if elapsed > 8:
            phase = "lockscreen"
            phase_started = now
    else:
        panel_x = int(width*0.57)
        panel_w = width-panel_x-28
        panel_y = int(height*0.14)
        pygame.draw.rect(screen, (95, 10, 18), (panel_x, panel_y, panel_w, int(height*0.28)), 2)
        centered("⚠ ВАШ ПК ЗАБЛОКИРОВАН ⚠", panel_y+20, font(max(20, int(width/47)), True), RED)
        centered("ВАШ КОМПЬЮТЕР ПОДВЕРГСЯ", panel_y+78, font(max(15, int(width/66)), True), WHITE)
        centered("ХАКЕРСКОЙ АТАКЕ!", panel_y+108, font(max(20, int(width/52)), True), RED)

        # Fake status log — purely visual, no files are touched.
        log_y = int(height*0.49)
        log_lines = [
            "[+] Инициализация интерфейса...",
            "[+] Проверка системных модулей...",
            "[+] Имитация сканирования дисков...",
            "[!] ФАЙЛЫ НЕ ИЗМЕНЯЮТСЯ — DEMO",
        ]
        for i, line in enumerate(log_lines):
            color = RED if i == 3 else WHITE
            screen.blit(font(max(14, int(width/82))).render(line, True, color), (panel_x+12, log_y+i*29))

        remaining = max(0, 24*3600 - int(now-countdown_start))
        hh, rem = divmod(remaining, 3600)
        mm, ss = divmod(rem, 60)
        timer_text = f"{hh:02d}:{mm:02d}:{ss:02d}"
        centered("ДЛЯ РАЗБЛОКИРОВКИ ПИШИТЕ В TELEGRAM:", int(height*0.70), font(max(15, int(width/75))), WHITE)
        centered("@DeaDKM", int(height*0.76), font(max(28, int(width/30)), True), RED)
        centered(timer_text, int(height*0.86), font(max(23, int(width/48)), True), WHITE)
        centered("AINLOCKER // БЕЗОПАСНАЯ СИМУЛЯЦИЯ — ESC ДЛЯ ВЫХОДА", height-29, font(14), RED)

    # Brief horizontal glitch bars
    if random.random() < 0.07:
        gy = random.randrange(55, max(56, height-40))
        gw = random.randrange(max(20, width//12), max(21, width//2))
        gx = random.randrange(0, max(1, width-gw))
        pygame.draw.rect(screen, random.choice([RED, WHITE]), (gx, gy, gw, 1))
    draw_scanlines(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
