import pygame
import random
import math
import sys

# Inicializa todos os módulos do pygame
pygame.init()

# Define o tamanho da janela do jogo
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Todo mundo odeia o X")

# Relógio para controlar os quadros por segundo (FPS)
clock = pygame.time.Clock()

# Paleta de cores em formato RGB
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
YELLOW       = (255, 220, 50)
PURPLE       = (120, 60, 200)
LIGHT_PURPLE = (180, 120, 255)
DARK_BLUE    = (5, 5, 30)
BTN_COLOR    = (60, 20, 120)
BTN_HOVER    = (90, 40, 180)
BTN_BORDER   = (200, 150, 255)

# --- Estrelas do fundo ---
NUM_STARS = 200
# Gera 200 estrelas com posição, tamanho, velocidade e brilho aleatórios
stars = [
    {
        "x":          random.randint(0, WIDTH),
        "y":          random.randint(0, HEIGHT),
        "r":          random.uniform(0.5, 2.5),    # raio da estrela
        "speed":      random.uniform(0.02, 0.08),  # velocidade de piscar
        "brightness": random.randint(150, 255),    # brilho máximo
        "phase":      random.uniform(0, math.pi * 2),  # fase inicial da animação
    }
    for _ in range(NUM_STARS)
]

# Nebulosas: elipses coloridas semitransparentes para dar profundidade ao fundo
nebulae = [
    {"x": 150, "y": 200, "rx": 180, "ry": 100, "color": (80, 0, 120)},
    {"x": 700, "y": 150, "rx": 140, "ry": 80,  "color": (0, 50, 130)},
    {"x": 500, "y": 450, "rx": 200, "ry": 90,  "color": (60, 0, 100)},
]


def draw_galaxy_bg(t):
    """Desenha o fundo animado com nebulosas e estrelas piscando."""
    # Preenche a tela com azul escuro (cor base do espaço)
    screen.fill(DARK_BLUE)

    # Desenha as nebulosas numa surface com suporte a transparência (alpha)
    nebula_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for neb in nebulae:
        # Faz a nebulosa pulsar suavemente usando seno
        pulse = 0.7 + 0.3 * math.sin(t * 0.5 + neb["x"])
        color = (*neb["color"], int(60 * pulse))  # alpha varia com o pulso
        pygame.draw.ellipse(
            nebula_surf, color,
            (neb["x"] - neb["rx"], neb["y"] - neb["ry"],
             neb["rx"] * 2, neb["ry"] * 2)
        )
    screen.blit(nebula_surf, (0, 0))

    # Desenha cada estrela com brilho pulsante (efeito de piscar)
    for star in stars:
        blink = 0.5 + 0.5 * math.sin(t * star["speed"] * 10 + star["phase"])
        alpha = int(star["brightness"] * blink)
        c = (alpha, alpha, alpha)  # cinza com intensidade variável
        pygame.draw.circle(screen, c, (int(star["x"]), int(star["y"])), int(star["r"]))


def draw_title(t):
    """Desenha o título animado do jogo na tela inicial."""
    # Cor do título oscila entre laranja e amarelo no tempo
    glow = int(180 + 75 * math.sin(t * 1.5))
    title_color = (255, glow, 50)

    # Fontes sem bold para ficarem mais finas e legíveis
    font_big = pygame.font.SysFont("impact", 64, bold=False)
    font_sub = pygame.font.SysFont("impact", 68, bold=False)

    # Renderiza as duas linhas do título
    line1 = font_big.render("Todo mundo odeia o", True, title_color)
    line2 = font_sub.render("X", True, (255, 80, 80))

    # Halo vermelho pulsante atrás da letra "X"
    halo_surf = pygame.Surface((120, 100), pygame.SRCALPHA)
    halo_alpha = int(100 + 80 * math.sin(t * 2))
    pygame.draw.ellipse(halo_surf, (255, 60, 60, halo_alpha), (0, 0, 120, 100))

    # Centraliza e posiciona as linhas verticalmente
    cx = WIDTH // 2
    y1 = 140
    screen.blit(line1, line1.get_rect(center=(cx, y1)))

    # Posiciona o halo logo atrás do "X" e depois desenha o "X" por cima
    x2 = cx + line2.get_width() // 2
    screen.blit(halo_surf, (x2 - 10, y1 + 50))
    screen.blit(line2, line2.get_rect(center=(cx, y1 + 70)))


def draw_button(text, rect, hovered, t):
    """Desenha um botão com borda animada e efeito de hover."""
    # Muda a cor do fundo se o mouse estiver sobre o botão
    color = BTN_HOVER if hovered else BTN_COLOR

    # Borda com brilho pulsante no tempo
    border_alpha = int(180 + 75 * math.sin(t * 2))
    border_color = (
        min(255, BTN_BORDER[0]),
        min(255, int(BTN_BORDER[1] * border_alpha / 255)),
        min(255, BTN_BORDER[2]),
    )

    # Desenha o fundo e a borda com bordas arredondadas
    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=14)

    # Renderiza e centraliza o texto dentro do botão
    font = pygame.font.SysFont("segoeui", 30, bold=True)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def tela_instrucoes():
    """Tela que exibe as instruções do jogo."""
    font_title = pygame.font.SysFont("impact", 40)
    font_text  = pygame.font.SysFont("segoeui", 22)
    btn_back   = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 80, 180, 48)

    # Lista de linhas de instrução (string vazia = linha em branco)
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
        t = pygame.time.get_ticks() / 1000  # tempo em segundos para animações
        draw_galaxy_bg(t)

        # Título da tela
        title_surf = font_title.render("Instruções", True, YELLOW)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 80)))

        # Exibe cada linha de instrução espaçada verticalmente
        for i, linha in enumerate(instrucoes):
            surf = font_text.render(linha, True, WHITE)
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 160 + i * 36)))

        # Verifica se o mouse está sobre o botão Voltar
        mouse = pygame.mouse.get_pos()
        hovered = btn_back.collidepoint(mouse)
        draw_button("Voltar", btn_back, hovered, t)

        # Processa eventos: fechar janela ou clicar em Voltar
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and hovered:
                running = False  # sai do loop e volta ao menu

        pygame.display.flip()
        clock.tick(60)  # limita a 60 quadros por segundo


def tela_jogar():
    """Tela provisória mostrada ao clicar em Jogar (conteúdo ainda não implementado)."""
    font = pygame.font.SysFont("impact", 52)
    msg = font.render("Em breve...", True, YELLOW)
    btn_back = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 80, 180, 48)

    running = True
    while running:
        t = pygame.time.get_ticks() / 1000
        draw_galaxy_bg(t)

        # Exibe a mensagem centralizada na tela
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        # Botão de voltar ao menu
        mouse = pygame.mouse.get_pos()
        hovered = btn_back.collidepoint(mouse)
        draw_button("Voltar", btn_back, hovered, t)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and hovered:
                running = False

        pygame.display.flip()
        clock.tick(60)


def menu_principal():
    """Loop principal do menu inicial com título e botões de navegação."""
    # Define a posição e tamanho dos botões do menu
    btn_instrucoes = pygame.Rect(WIDTH // 2 - 130, 360, 260, 56)
    btn_jogar      = pygame.Rect(WIDTH // 2 - 130, 440, 260, 56)

    running = True
    while running:
        t = pygame.time.get_ticks() / 1000  # tempo usado nas animações

        # Desenha o fundo e o título animados
        draw_galaxy_bg(t)
        draw_title(t)

        # Detecta posição do mouse para efeito de hover nos botões
        mouse = pygame.mouse.get_pos()
        h_inst  = btn_instrucoes.collidepoint(mouse)
        h_jogar = btn_jogar.collidepoint(mouse)

        # Desenha os dois botões do menu
        draw_button("Instruções", btn_instrucoes, h_inst,  t)
        draw_button("Jogar",      btn_jogar,      h_jogar, t)

        # Processa eventos de teclado/mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if h_inst:
                    tela_instrucoes()   # abre a tela de instruções
                elif h_jogar:
                    tela_jogar()        # abre a tela do jogo

        pygame.display.flip()
        clock.tick(60)


# Ponto de entrada do programa
if __name__ == "__main__":
    menu_principal()
