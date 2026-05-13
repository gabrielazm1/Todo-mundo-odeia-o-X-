import os
import sys
import math
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Todo mundo odeia o X")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 50)
PURPLE = (120, 60, 200)
LIGHT_PURPLE = (180, 120, 255)
DARK_BLUE = (5, 5, 30)
BTN_COLOR = (60, 20, 120)
BTN_HOVER = (90, 40, 180)
BTN_BORDER = (200, 150, 255)

NUM_STARS = 200
stars = [
    {
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "r": random.uniform(0.5, 2.5),
        "speed": random.uniform(0.02, 0.08),
        "brightness": random.randint(150, 255),
        "phase": random.uniform(0, math.pi * 2),
    }
    for _ in range(NUM_STARS)
]

nebulae = [
    {"x": 150, "y": 200, "rx": 180, "ry": 100, "color": (80, 0, 120)},
    {"x": 700, "y": 150, "rx": 140, "ry": 80, "color": (0, 50, 130)},
    {"x": 500, "y": 450, "rx": 200, "ry": 90, "color": (60, 0, 100)},
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

import subprocess

def _extrair_metrocity():
    metro_dir = os.path.join(BASE_DIR, "MetroCity")
    rar_path = os.path.join(BASE_DIR, "MetroCity.rar")

    if os.path.isdir(metro_dir):
        return True
    if not os.path.isfile(rar_path):
        return False

    winrar_paths = [
        r"C:\Program Files\WinRAR\WinRAR.exe",
        r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
    ]
    sevenz_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ]

    for winrar in winrar_paths:
        if os.path.isfile(winrar):
            try:
                subprocess.run([winrar, "x", "-y", rar_path, BASE_DIR + "\\"], check=True, timeout=60)
                return True
            except Exception:
                pass

    for sevenz in sevenz_paths:
        if os.path.isfile(sevenz):
            try:
                subprocess.run([sevenz, "x", rar_path, f"-o{BASE_DIR}", "-y"], check=True, timeout=60)
                return True
            except Exception:
                pass

    try:
        import rarfile
        with rarfile.RarFile(rar_path) as rf:
            rf.extractall(BASE_DIR)
        return True
    except Exception:
        pass

    return False

_extrair_metrocity()

_FILE_INDEX = {}

def _build_index():
    search_roots = [BASE_DIR]
    for root_name in os.listdir(BASE_DIR):
        full = os.path.join(BASE_DIR, root_name)
        if os.path.isdir(full) and not root_name.startswith("."):
            search_roots.append(full)
    for root in search_roots:
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                key = fname.lower()
                full_path = os.path.join(dirpath, fname)
                if key not in _FILE_INDEX:
                    _FILE_INDEX[key] = full_path

_build_index()


def find_asset(*parts):
    filename = parts[-1]
    exact_candidates = [
        os.path.join(BASE_DIR, "MetroCity", *parts),
        os.path.join(BASE_DIR, "metrocity_extracted", "MetroCity", *parts),
        os.path.join(BASE_DIR, *parts),
    ]
    for path in exact_candidates:
        if os.path.exists(path):
            return path
    found = _FILE_INDEX.get(filename.lower())
    if found:
        return found
    return exact_candidates[0]


def load_image(path, size=None, fallback_label="imagem"):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size is not None:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        if size is None:
            size = (160, 160)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((35, 35, 55, 255))
        pygame.draw.rect(surf, BTN_BORDER, surf.get_rect(), width=2, border_radius=12)
        font = pygame.font.SysFont("segoeui", 16, bold=True)
        txt = font.render(f"faltando {fallback_label}", True, WHITE)
        surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
        return surf


def trim_alpha(surf):
    try:
        rect = surf.get_bounding_rect()
        if rect.width > 0 and rect.height > 0:
            return surf.subsurface(rect).copy()
    except Exception:
        pass
    return surf.copy()


def smart_crop(surf):
    surf = trim_alpha(surf)
    w, h = surf.get_size()
    if w == 0 or h == 0:
        return surf

    if w > h * 1.15 or h > w * 1.15:
        side = min(w, h)
        left = max(0, (w - side) // 2)
        top = max(0, (h - side) // 2)
        return surf.subsurface(pygame.Rect(left, top, side, side)).copy()

    return surf


def scale_to_fit(surf, max_w, max_h):
    w, h = surf.get_size()
    if w == 0 or h == 0:
        return surf
    ratio = min(max_w / w, max_h / h)
    size = (max(1, int(w * ratio)), max(1, int(h * ratio)))
    return pygame.transform.scale(surf, size)


def draw_galaxy_bg(t):
    screen.fill(DARK_BLUE)

    nebula_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for neb in nebulae:
        pulse = 0.7 + 0.3 * math.sin(t * 0.5 + neb["x"])
        color = (*neb["color"], int(60 * pulse))
        pygame.draw.ellipse(
            nebula_surf,
            color,
            (neb["x"] - neb["rx"], neb["y"] - neb["ry"], neb["rx"] * 2, neb["ry"] * 2),
        )
    screen.blit(nebula_surf, (0, 0))

    for star in stars:
        blink = 0.5 + 0.5 * math.sin(t * star["speed"] * 10 + star["phase"])
        alpha = int(star["brightness"] * blink)
        c = (alpha, alpha, alpha)
        pygame.draw.circle(screen, c, (int(star["x"]), int(star["y"])), max(1, int(star["r"])))


def draw_title(t):
    glow = int(180 + 75 * math.sin(t * 1.5))
    title_color = (255, glow, 50)

    font_big = pygame.font.SysFont("impact", 64, bold=False)
    font_sub = pygame.font.SysFont("impact", 68, bold=False)

    line1 = font_big.render("Todo mundo odeia o", True, title_color)
    line2 = font_sub.render("X", True, (255, 80, 80))

    halo_surf = pygame.Surface((120, 100), pygame.SRCALPHA)
    halo_alpha = int(100 + 80 * math.sin(t * 2))
    pygame.draw.ellipse(halo_surf, (255, 60, 60, halo_alpha), (0, 0, 120, 100))

    cx = WIDTH // 2
    y1 = 140
    screen.blit(line1, line1.get_rect(center=(cx, y1)))

    x2 = cx + line2.get_width() // 2
    screen.blit(halo_surf, (x2 - 10, y1 + 50))
    screen.blit(line2, line2.get_rect(center=(cx, y1 + 70)))


def draw_button(text, rect, hovered, t, font_size=30):
    color = BTN_HOVER if hovered else BTN_COLOR

    border_alpha = int(180 + 75 * math.sin(t * 2))
    border_color = (
        min(255, BTN_BORDER[0]),
        min(255, int(BTN_BORDER[1] * border_alpha / 255)),
        min(255, BTN_BORDER[2]),
    )

    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=14)

    font = pygame.font.SysFont("segoeui", font_size, bold=True)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def split_vertical_sheet(sheet, count):
    frames = []
    if count <= 0:
        return frames

    w, h = sheet.get_size()
    step = max(1, h // count)

    for i in range(count):
        top = i * step
        bottom = h if i == count - 1 else min(h, (i + 1) * step)
        rect = pygame.Rect(0, top, w, max(1, bottom - top))
        try:
            frame = sheet.subsurface(rect).copy()
        except Exception:
            frame = sheet.copy()
        frames.append(smart_crop(frame))

    return frames


def draw_option_grid(items, selected_idx, cols, title, subtitle, label_prefix, start_y=170, card_w=150, card_h=160):
    title_font = pygame.font.SysFont("impact", 46)
    sub_font = pygame.font.SysFont("segoeui", 18)
    label_font = pygame.font.SysFont("segoeui", 16, bold=True)

    title_surf = title_font.render(title, True, YELLOW)
    sub_surf = sub_font.render(subtitle, True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 70)))
    screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, 110)))

    total_w = cols * card_w + (cols - 1) * 18
    start_x = (WIDTH - total_w) // 2

    rects = []
    for idx, item in enumerate(items):
        row = idx // cols
        col = idx % cols
        rect = pygame.Rect(
            start_x + col * (card_w + 18),
            start_y + row * (card_h + 18),
            card_w,
            card_h,
        )
        rects.append(rect)

        pygame.draw.rect(screen, (40, 30, 80), rect, border_radius=14)
        border = BTN_BORDER if idx == selected_idx else (100, 100, 150)
        pygame.draw.rect(screen, border, rect, width=3 if idx == selected_idx else 2, border_radius=14)

        img = smart_crop(item)
        img = scale_to_fit(img, card_w - 24, card_h - 48)
        screen.blit(img, img.get_rect(center=(rect.centerx, rect.y + (card_h - 22) // 2 - 4)))

        label = label_font.render(f"{label_prefix} {idx + 1}", True, WHITE)
        screen.blit(label, label.get_rect(center=(rect.centerx, rect.bottom - 16)))

    return rects


def compose_character(body_img, outfit_img, hair_img):
    canvas = pygame.Surface((360, 460), pygame.SRCALPHA)
    cx = canvas.get_width() // 2

    shadow_path = find_asset("CharacterModel", "Shadow.png")
    shadow = load_image(shadow_path, fallback_label="Shadow")

    shadow = scale_to_fit(smart_crop(shadow), 170, 70)
    body = scale_to_fit(smart_crop(body_img), 180, 260)
    outfit = scale_to_fit(smart_crop(outfit_img), 180, 260)
    hair = scale_to_fit(smart_crop(hair_img), 130, 130)

    canvas.blit(shadow, shadow.get_rect(center=(cx, 392)))
    canvas.blit(body, body.get_rect(center=(cx, 270)))
    canvas.blit(outfit, outfit.get_rect(center=(cx, 270)))
    canvas.blit(hair, hair.get_rect(center=(cx, 115)))

    return canvas


def tela_instrucoes():
    font_title = pygame.font.SysFont("impact", 40)
    font_text = pygame.font.SysFont("segoeui", 22)
    btn_back = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 80, 180, 48)

    instrucoes = [
        "Objetivo: Mate o X!",
        "",
        "• Use o mouse para atirar no X.",
        "• Conforme o X perde vidas ele se move mais rápido.",
        "• Você tem um número limitado de munições, atire com precisão.",
        "• Atire nas estrelas para ganhar mais munições.",
        "",
    ]

    running = True
    while running:
        t = pygame.time.get_ticks() / 1000
        draw_galaxy_bg(t)

        title_surf = font_title.render("Instruções", True, YELLOW)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 80)))

        for i, linha in enumerate(instrucoes):
            surf = font_text.render(linha, True, WHITE)
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 160 + i * 36)))

        mouse = pygame.mouse.get_pos()
        hovered = btn_back.collidepoint(mouse)
        draw_button("Voltar", btn_back, hovered, t)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and hovered:
                running = False

        pygame.display.flip()
        clock.tick(60)


def tela_escolha_x():
    font_title = pygame.font.SysFont("impact", 46)
    font_input = pygame.font.SysFont("segoeui", 28)
    font_hint = pygame.font.SysFont("segoeui", 18)

    input_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 20, 440, 60)
    btn_next = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 70, 220, 52)

    texto = ""
    active = False
    running = True

    while running:
        t = pygame.time.get_ticks() / 1000
        draw_galaxy_bg(t)

        title_surf = font_title.render("Todo mundo odeia o X", True, YELLOW)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 70)))

        hint_surf = font_hint.render("Digite o nome do seu X:", True, WHITE)
        screen.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, 165)))

        mouse = pygame.mouse.get_pos()
        hovered_btn = btn_next.collidepoint(mouse)

        box_color = BTN_HOVER if active else BTN_COLOR
        pygame.draw.rect(screen, box_color, input_rect, border_radius=14)
        pygame.draw.rect(screen, BTN_BORDER, input_rect, width=2, border_radius=14)

        if texto == "":
            placeholder = font_input.render("Escolha seu X", True, (180, 180, 180))
            screen.blit(placeholder, (input_rect.x + 18, input_rect.y + 15))
        else:
            txt_surf = font_input.render(texto, True, WHITE)
            screen.blit(txt_surf, (input_rect.x + 18, input_rect.y + 15))

        draw_button("Próximo", btn_next, hovered_btn, t)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_rect.collidepoint(event.pos)
                if btn_next.collidepoint(event.pos):
                    nome_x = texto.strip()
                    if nome_x:
                        return nome_x

            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_BACKSPACE:
                    texto = texto[:-1]
                elif event.key == pygame.K_RETURN:
                    nome_x = texto.strip()
                    if nome_x:
                        return nome_x
                else:
                    if len(texto) < 20 and event.unicode.isprintable():
                        texto += event.unicode

        pygame.display.flip()
        clock.tick(60)


BODY_SHEET = load_image(find_asset("CharacterModel", "Character Model.png"), fallback_label="Character Model")
BODY_OPTIONS = split_vertical_sheet(BODY_SHEET, 4)

HAIR_OPTIONS = [
    load_image(find_asset("Hair", f"Hair{i}.png"), fallback_label=f"Hair{i}")
    for i in range(1, 8)
]

OUTFIT_OPTIONS = [
    load_image(find_asset("Outfits", f"Outfit{i}.png"), fallback_label=f"Outfit{i}")
    for i in range(1, 7)
]


def tela_montagem_x(nome_x):
    stage = 1
    selected_body = 0
    selected_outfit = 0
    selected_hair = 0

    btn_back = pygame.Rect(30, HEIGHT - 78, 160, 46)
    btn_next = pygame.Rect(WIDTH - 190, HEIGHT - 78, 160, 46)
    btn_prev = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 78, 160, 46)

    while True:
        t = pygame.time.get_ticks() / 1000
        draw_galaxy_bg(t)
        mouse = pygame.mouse.get_pos()

        if stage == 1:
            rects = draw_option_grid(
                BODY_OPTIONS,
                selected_body,
                2,
                "Escolha o corpo do X",
                "Use as 4 opções que vêm no arquivo.",
                "Corpo",
                start_y=170,
                card_w=170,
                card_h=185,
            )

            hovered_back = btn_back.collidepoint(mouse)
            hovered_next = btn_next.collidepoint(mouse)
            draw_button("Voltar", btn_back, hovered_back, t, font_size=24)
            draw_button("Próximo", btn_next, hovered_next, t, font_size=24)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_back.collidepoint(event.pos):
                        return None
                    if btn_next.collidepoint(event.pos):
                        stage = 2
                    else:
                        for idx, rect in enumerate(rects):
                            if rect.collidepoint(event.pos):
                                selected_body = idx

        elif stage == 2:
            rects = draw_option_grid(
                OUTFIT_OPTIONS,
                selected_outfit,
                3,
                "Escolha a roupa do X",
                "Clique em uma roupa e depois em Próximo.",
                "Roupa",
                start_y=170,
                card_w=150,
                card_h=160,
            )

            hovered_back = btn_back.collidepoint(mouse)
            hovered_next = btn_next.collidepoint(mouse)
            draw_button("Voltar", btn_back, hovered_back, t, font_size=24)
            draw_button("Próximo", btn_next, hovered_next, t, font_size=24)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_back.collidepoint(event.pos):
                        stage = 1
                    elif btn_next.collidepoint(event.pos):
                        stage = 3
                    else:
                        for idx, rect in enumerate(rects):
                            if rect.collidepoint(event.pos):
                                selected_outfit = idx

        elif stage == 3:
            rects = draw_option_grid(
                HAIR_OPTIONS,
                selected_hair,
                3,
                "Escolha o cabelo do X",
                "Clique em um cabelo e depois em Próximo.",
                "Cabelo",
                start_y=170,
                card_w=150,
                card_h=160,
            )

            hovered_back = btn_back.collidepoint(mouse)
            hovered_next = btn_next.collidepoint(mouse)
            draw_button("Voltar", btn_back, hovered_back, t, font_size=24)
            draw_button("Próximo", btn_next, hovered_next, t, font_size=24)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_back.collidepoint(event.pos):
                        stage = 2
                    elif btn_next.collidepoint(event.pos):
                        stage = 4
                    else:
                        for idx, rect in enumerate(rects):
                            if rect.collidepoint(event.pos):
                                selected_hair = idx

        else:
            body = BODY_OPTIONS[selected_body]
            outfit = OUTFIT_OPTIONS[selected_outfit]
            hair = HAIR_OPTIONS[selected_hair]

            composed = compose_character(body, outfit, hair)

            title_font = pygame.font.SysFont("impact", 40)
            text_font = pygame.font.SysFont("segoeui", 24)
            small_font = pygame.font.SysFont("segoeui", 18)

            title = title_font.render("Confira o seu X", True, YELLOW)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 62)))

            name_surf = text_font.render(f"Nome escolhido: {nome_x}", True, WHITE)
            screen.blit(name_surf, name_surf.get_rect(center=(WIDTH // 2, 110)))

            preview_box = pygame.Rect(WIDTH // 2 - 180, 150, 360, 460)
            pygame.draw.rect(screen, (30, 24, 65), preview_box, border_radius=20)
            pygame.draw.rect(screen, BTN_BORDER, preview_box, width=2, border_radius=20)

            screen.blit(composed, composed.get_rect(center=preview_box.center))

            info = small_font.render("Clique em Começar para iniciar o jogo.", True, WHITE)
            screen.blit(info, info.get_rect(center=(WIDTH // 2, 525)))

            hovered_prev = btn_prev.collidepoint(mouse)
            hovered_start = btn_next.collidepoint(mouse)
            draw_button("Voltar", btn_prev, hovered_prev, t, font_size=24)
            draw_button("Começar", btn_next, hovered_start, t, font_size=24)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_prev.collidepoint(event.pos):
                        stage = 3
                    elif btn_next.collidepoint(event.pos) or preview_box.collidepoint(event.pos):
                        return composed

        pygame.display.flip()
        clock.tick(60)


def tela_jogo(nome_x, avatar):
    alvo = scale_to_fit(avatar, 120, 160)
    alvo_rect = alvo.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    score = 0
    last_move = 0
    move_delay = 1200

    font_title = pygame.font.SysFont("impact", 38)
    font_text = pygame.font.SysFont("segoeui", 22)
    btn_back = pygame.Rect(20, 20, 140, 42)

    running = True
    while running:
        t = pygame.time.get_ticks() / 1000
        now = pygame.time.get_ticks()

        draw_galaxy_bg(t)

        if now - last_move > move_delay:
            last_move = now
            alvo_rect.center = (
                random.randint(150, WIDTH - 150),
                random.randint(180, HEIGHT - 120),
            )
            move_delay = max(450, 1200 - score * 80)

        title = font_title.render(f"Alvo: {nome_x}", True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 45)))

        score_surf = font_text.render(f"Acertos: {score}", True, WHITE)
        screen.blit(score_surf, (20, 70))

        mouse = pygame.mouse.get_pos()
        hovered_back = btn_back.collidepoint(mouse)
        draw_button("Menu", btn_back, hovered_back, t, font_size=20)

        screen.blit(alvo, alvo_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(event.pos):
                    return
                if alvo_rect.collidepoint(event.pos):
                    score += 1
                    alvo_rect.center = (
                        random.randint(150, WIDTH - 150),
                        random.randint(180, HEIGHT - 120),
                    )

        pygame.display.flip()
        clock.tick(60)


def menu_principal():
    btn_instrucoes = pygame.Rect(WIDTH // 2 - 130, 360, 260, 56)
    btn_jogar = pygame.Rect(WIDTH // 2 - 130, 440, 260, 56)

    running = True
    while running:
        t = pygame.time.get_ticks() / 1000

        draw_galaxy_bg(t)
        draw_title(t)

        mouse = pygame.mouse.get_pos()
        h_inst = btn_instrucoes.collidepoint(mouse)
        h_jogar = btn_jogar.collidepoint(mouse)

        draw_button("Instruções", btn_instrucoes, h_inst, t)
        draw_button("Jogar", btn_jogar, h_jogar, t)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if h_inst:
                    tela_instrucoes()
                elif h_jogar:
                    nome_x = tela_escolha_x()
                    if nome_x:
                        avatar = tela_montagem_x(nome_x)
                        if avatar is not None:
                            tela_jogo(nome_x, avatar)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    menu_principal()