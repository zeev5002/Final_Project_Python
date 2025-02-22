import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

WIDTH = 800
HEIGHT = 600
FPS = 30

WHITE = (255, 255, 255)
BROWN = (165, 42, 42)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GAME_OVER_BACKGROUND = (50, 50, 150)

PLAYER_LIVES = 3
PLAYER_SIZE = 90
PLAYER_VEL = 7

ENEMY_SPEED = 5
MAX_ENEMIES_ON_SCREEN = 10

ENEMY_SIZE = 80
ENEMY_LIST = []

BULLET_WIDTH = 25
BULLET_HEIGHT = 25
BULLET_VEL = 15
BULLET_LIST = []
MAX_BULLETS = 5

SCORE = 0
POINTS_PER_HIT = 2
POINTS_PER_ESCAPE = 1

######################################################################
# טעינת משאבי תמונות וצלילים (עדכן/י את שמות הקבצים לפי הצורך)
######################################################################
try:
    BACKGROUND = pygame.transform.scale(
        pygame.image.load(os.path.join('Assets', 'myBackgr.jpg')),
        (WIDTH, HEIGHT)
    )
except:
    BACKGROUND = None

try:
    PLAYER_IMAGE_RAW = pygame.image.load(os.path.join('Assets', 'player.png'))
    PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE_RAW, (PLAYER_SIZE, PLAYER_SIZE))
except:
    PLAYER_IMAGE = None

try:
    ENEMY_IMAGE_RAW = pygame.image.load(os.path.join('Assets', 'terrorist.png'))
    ENEMY_IMAGE = pygame.transform.scale(ENEMY_IMAGE_RAW, (ENEMY_SIZE, ENEMY_SIZE))
except:
    ENEMY_IMAGE = None

try:
    BULLET_IMAGE_RAW = pygame.image.load(os.path.join('Assets', 'fire.png'))
    BULLET_IMAGE = pygame.transform.scale(BULLET_IMAGE_RAW, (BULLET_WIDTH, BULLET_HEIGHT))
except:
    BULLET_IMAGE = None

try:
    BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Pain_Sound.mp3'))
    BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Shot_Sound.mp3'))
except:
    BULLET_HIT_SOUND = None
    BULLET_FIRE_SOUND = None

try:
    NO_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'No_Sound.mp3'))
except:
    NO_SOUND = None

try:
    GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Game_Over_Sound.mp3'))
except:
    GAME_OVER_SOUND = None

try:
    GAME_OVER_BG = pygame.transform.scale(
        pygame.image.load(os.path.join('Assets', 'game_over.JPG')),
        (WIDTH, HEIGHT)
    )
except:
    GAME_OVER_BG = None

pygame.font.init()
FONT = pygame.font.SysFont('comicsans', 30)
BIG_FONT = pygame.font.SysFont('comicsans', 60)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Combined Game - Tank Version")
clock = pygame.time.Clock()

######################################################################
# פונקציות עזר
######################################################################

def set_level(score):
    """
    משדרג את מהירות האויבים וכמות האויבים כל 50 נקודות.
    """
    base_speed = 5
    base_enemies = 5
    increments = score // 50
    new_speed = base_speed + increments * 5
    new_max_enemies = base_enemies + increments * 5
    return new_speed, new_max_enemies

def draw_centered_text(surface, text, font, color, y):
    """
    פונקציה שמרכזת טקסט לרוחב המסך (X).
    """
    render = font.render(text, True, color)
    text_width = render.get_width()
    x = (WIDTH - text_width) // 2
    surface.blit(render, (x, y))

def draw_text(surface, text, font, color, x, y):
    """
    פונקציה כללית לציור טקסט במיקום ספציפי.
    """
    label = font.render(text, True, color)
    surface.blit(label, (x, y))

def drop_enemies(enemy_list, enemy_size, current_max_enemies):
    delay = random.random()
    # אפשר להגדיל את הסיכוי ליצירת אויבים (למשל < 0.2) אם רוצים יותר
    if len(enemy_list) < current_max_enemies and delay < 0.2:
        x_pos = random.randint(0, WIDTH - enemy_size)
        y_pos = 0
        enemy_list.append([x_pos, y_pos])

def draw_enemies(surface, enemy_list, enemy_size):
    for enemy_pos in enemy_list:
        if ENEMY_IMAGE:
            surface.blit(ENEMY_IMAGE, (enemy_pos[0], enemy_pos[1]))
        else:
            pygame.draw.rect(surface, BLUE, (enemy_pos[0], enemy_pos[1], enemy_size, enemy_size))

def update_enemy_positions(enemy_list, enemy_size, score, player_rect, lives, enemy_speed):
    """
    enemy_speed: מהירות נפילה, מחושב ב-set_level
    """
    for idx, enemy_pos in enumerate(enemy_list):
        if 0 <= enemy_pos[1] < HEIGHT:
            enemy_pos[1] += enemy_speed
        else:
            enemy_list.pop(idx)
            score += POINTS_PER_ESCAPE

    new_enemy_list = []
    for enemy_pos in enemy_list:
        enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect):
            lives -= 1
            if NO_SOUND:
                NO_SOUND.play()
        else:
            new_enemy_list.append(enemy_pos)

    enemy_list = new_enemy_list
    return score, lives, enemy_list

def draw_player(surface, player_rect):
    if PLAYER_IMAGE:
        surface.blit(PLAYER_IMAGE, (player_rect.x, player_rect.y))
    else:
        pygame.draw.rect(surface, RED, player_rect)

def draw_bullets(surface, bullets):
    for bullet in bullets:
        if BULLET_IMAGE:
            surface.blit(BULLET_IMAGE, (bullet.x, bullet.y))
        else:
            pygame.draw.rect(surface, YELLOW, bullet)

def handle_bullets(bullet_list, enemy_list, score):
    new_bullet_list = []
    for bullet in bullet_list:
        bullet.y -= BULLET_VEL
        if bullet.y < 0:
            continue
        hit_index = None
        for i, enemy_pos in enumerate(enemy_list):
            enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], ENEMY_SIZE, ENEMY_SIZE)
            if bullet.colliderect(enemy_rect):
                # פגיעה באויב
                if BULLET_HIT_SOUND:
                    BULLET_HIT_SOUND.play()
                score += POINTS_PER_HIT
                hit_index = i
                break
        if hit_index is not None:
            enemy_list.pop(hit_index)
        else:
            new_bullet_list.append(bullet)
    return new_bullet_list, enemy_list, score

def game_over_screen(final_score):
    """
    מציג מסך סיום, עושה השהיה של 3 שניות,
    מנקה אירועים ישנים ואז מחכה ללחיצה חדשה.
    """
    if GAME_OVER_SOUND:
        GAME_OVER_SOUND.play()

    # רקע למסך סיום
    if GAME_OVER_BG:
        screen.blit(GAME_OVER_BG, (0, 0))
    else:
        screen.fill(GAME_OVER_BACKGROUND)

    # מציג טקסט ממורכז: Game Over, ניקוד, והודעה להמתין 3 שניות
    draw_centered_text(screen, "Game Over!", BIG_FONT, WHITE, HEIGHT//2 - 80)
    draw_centered_text(screen, f"Your score: {final_score}", FONT, WHITE, HEIGHT//2 - 20)
    draw_centered_text(screen, "Please wait 3 seconds...", FONT, WHITE, HEIGHT//2 + 20)
    pygame.display.update()

    # השהיה 3 שניות
    pygame.time.delay(3000)

    # נקה את תור האירועים כדי לא לספור לחיצות שהגיעו בזמן ההשהיה
    pygame.event.clear()

    # מציג שוב את המסך, כעת עם הנחיה ללחוץ מקש
    if GAME_OVER_BG:
        screen.blit(GAME_OVER_BG, (0, 0))
    else:
        screen.fill(GAME_OVER_BACKGROUND)

    draw_centered_text(screen, "Game Over!", BIG_FONT, WHITE, HEIGHT//2 - 80)
    draw_centered_text(screen, f"Your score: {final_score}", FONT, WHITE, HEIGHT//2 - 20)
    draw_centered_text(screen, "Press any key to play again or ESC to quit", FONT, WHITE, HEIGHT//2 + 20)
    pygame.display.update()

    # כעת מחכים ללחיצה חדשה
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    waiting = False

def main_game():
    global SCORE, ENEMY_LIST, BULLET_LIST

    SCORE = 0
    ENEMY_LIST = []
    BULLET_LIST = []
    lives = PLAYER_LIVES

    player_rect = pygame.Rect(
        WIDTH // 2 - (PLAYER_SIZE // 2),
        HEIGHT - 2 * PLAYER_SIZE,
        PLAYER_SIZE,
        PLAYER_SIZE
    )

    running = True
    while running:
        clock.tick(FPS)

        enemy_speed, current_max_enemies = set_level(SCORE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(BULLET_LIST) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        player_rect.x + player_rect.width // 2 - BULLET_WIDTH // 2,
                        player_rect.y,
                        BULLET_WIDTH,
                        BULLET_HEIGHT
                    )
                    BULLET_LIST.append(bullet)
                    if BULLET_FIRE_SOUND:
                        BULLET_FIRE_SOUND.play()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.x - PLAYER_VEL > 0:
            player_rect.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player_rect.x + PLAYER_VEL + player_rect.width < WIDTH:
            player_rect.x += PLAYER_VEL
        if keys[pygame.K_UP] and player_rect.y - PLAYER_VEL > 0:
            player_rect.y -= PLAYER_VEL
        if keys[pygame.K_DOWN] and player_rect.y + PLAYER_VEL + player_rect.height < HEIGHT:
            player_rect.y += PLAYER_VEL

        drop_enemies(ENEMY_LIST, ENEMY_SIZE, current_max_enemies)

        SCORE, lives, ENEMY_LIST = update_enemy_positions(
            ENEMY_LIST,
            ENEMY_SIZE,
            SCORE,
            player_rect,
            lives,
            enemy_speed
        )

        BULLET_LIST, ENEMY_LIST, SCORE = handle_bullets(BULLET_LIST, ENEMY_LIST, SCORE)

        if lives <= 0:
            running = False
            game_over_screen(SCORE)
            break

        if BACKGROUND:
            screen.blit(BACKGROUND, (0, 0))
        else:
            screen.fill(BROWN)

        draw_player(screen, player_rect)
        draw_enemies(screen, ENEMY_LIST, ENEMY_SIZE)
        draw_bullets(screen, BULLET_LIST)

        # ציור טקסט של חיים וניקוד בפינות
        draw_text(screen, f"Lives: {lives}", FONT, WHITE, 10, 10)
        draw_text(screen, f"Score: {SCORE}", FONT, WHITE, WIDTH - 150, 10)

        pygame.display.update()

def main():
    while True:
        main_game()

if __name__ == "__main__":
    main()
