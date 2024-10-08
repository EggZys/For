import pygame
import random
import os

# Инициализация Pygame
pygame.init()

# Определение констант
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Определение пути к папкам с текстурами, звуками и музыкой
TEXTURES_PATH = os.path.join("Textures")
SOUNDS_PATH = os.path.join("Sounds")
MUSIC_PATH = os.path.join("Music")

# Загрузка текстур
def load_image(filename):
    path = os.path.join(TEXTURES_PATH, filename)
    if not os.path.exists(path):
        print(f"Файл {path} не найден")
        pygame.quit()
        quit()
    return pygame.image.load(path)

player_img = load_image("player.png")
enemy_img = load_image("enemy.png")
bullet_img = load_image("bullet.png")

# Загрузка звуков
def load_sound(filename):
    path = os.path.join(SOUNDS_PATH, filename)
    if not os.path.exists(path):
        print(f"Файл {path} не найден")
        pygame.quit()
        quit()
    return pygame.mixer.Sound(path)

bullet_sound = load_sound("bullet.mp3")
explosion_sound = load_sound("explosion.mp3")
game_over_sound = load_sound("game_over.mp3")

# Загрузка музыки
def load_music(filename):
    path = os.path.join(MUSIC_PATH, filename)
    if not os.path.exists(path):
        print(f"Файл {path} не найден")
        pygame.quit()
        quit()
    return path

menu_music = load_music("menu_music.mp3")
game_music = load_music("game_music.mp3")

# Создание окна игры
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Космический защитник")

# Определение классов
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.shoot_delay = 250  # задержка между выстрелами
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # автоматическая стрельба
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            bullet_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 5)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 5)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Создание игрока
player = Player()
all_sprites.add(player)

# Создание врагов
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

RECORD_FILE = "record.txt"

def save_record(record):
    with open(RECORD_FILE, "w") as file:
        file.write(str(record))

def load_record():
    try:
        with open(RECORD_FILE, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0

record = load_record()

# Определение функций
def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def show_menu():
    pygame.mixer.music.load(menu_music)
    pygame.mixer.music.play(-1)  # -1 для зацикливания музыки
    screen.fill(BLACK)
    title_text = "Космический защитник"
    title_font = pygame.font.Font(None, 64)
    title_render = title_font.render(title_text, True, WHITE)
    title_rect = title_render.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_render, title_rect)

    play_button = pygame.Rect(0, 0, 200, 50)
    play_button.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, WHITE, play_button, 2)
    draw_text("Играть", 40, SCREEN_WIDTH // 2 - 35, SCREEN_HEIGHT // 2)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    waiting = False

def show_pause_menu():
    pygame.mixer.music.pause()
    paused = True

    while paused:
        screen.fill(BLACK)
        draw_text("Пауза", 64, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 4)
        draw_text("Нажмите Esc чтобы продолжить", 22, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 40)
        draw_text("Нажмите Q чтобы выйти в главное меню", 22, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 80)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    pygame.mixer.music.unpause()
                if event.key == pygame.K_q:
                    paused = False
                    pygame.mixer.music.stop()
                    return "main_menu"

def show_game_over_menu(score):
    pygame.mixer.music.stop()
    game_over_sound.play()
    screen.fill(BLACK)
    draw_text("Игра окончена", 64, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 4)
    draw_text(f"Очки: {score}", 32, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2)
    draw_text("Нажмите Esc чтобы выйти", 22, SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 40)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False

# Основной игровой цикл
running = True
in_game = False  # флаг, показывающий, находится ли игра в процессе игры или в меню
show_menu()
clock = pygame.time.Clock()

score = 0
record = load_record()

while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)

    if not in_game:  # если игра не активна, показываем главное меню
        show_menu()
        in_game = True
        score = 0

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                result = show_pause_menu()
                if result == "main_menu":
                    in_game = False  # если выходим в главное меню, устанавливаем флаг in_game в False

    if not in_game:  # если игра не активна, переходим к следующей итерации цикла
        continue

    # Создание врага при достижении каждых 1000 очков
    if score % 1000 == 0 and score > 0 and len(enemies) < score // 1000 + 8:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Обновление
    all_sprites.update()

    # Проверка столкновений пуль и врагов
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        explosion_sound.play()
        score += 1

    if score > record:
        record = score
        save_record(record)

    # Проверка столкновения врагов и игрока
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        running = False
        show_game_over_menu(score)

    # Отрисовка
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(f"Очки: {score}", 32, SCREEN_WIDTH - 150, 10)
    draw_text(f"Рекорд: {record}", 32, SCREEN_WIDTH - 150, 50)
    pygame.display.flip()

pygame.quit()