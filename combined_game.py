import pygame # מייבא את ספריית pygame המאפשרת פיתוח משחקים וגרפיקה
import random # מייבא את ספריית random לעבודה עם מספרים רנדומליים
import sys # מייבא את ספריית sys לשימוש בפונקציות מערכת כמו sys.exit()
import os # מייבא את ספריית os המאפשרת עבודה עם נתיבי קבצים

pygame.init() # אתחול המערכת הראשית של pygame
pygame.mixer.init() # אתחול המיקסר של pygame (שולט על צלילים ומוזיקה)

WIDTH = 800 # הגדרת רוחב חלון המשחק בפיקסלים
HEIGHT = 600 # הגדרת גובה חלון המשחק בפיקסלים
FPS = 30 # הגדרת קצב פריימים לשנייה (frames per second)

WHITE = (255, 255, 255) # צבע לבן 

PLAYER_LIVES = 3 # מספר החיים של השחקן
PLAYER_SIZE = 90 # גודל השחקן (משמש בסקיילינג של תמונת השחקן)
PLAYER_VEL = 7 # מהירות תנועת השחקן (פיקסלים לפריים)

ENEMY_SPEED = 5 # מהירות בסיסית לאויבים (נפילה למטה)
MAX_ENEMIES_ON_SCREEN = 10 # כמות אויבים מקסימלית שעלולה להיות על המסך
ENEMY_SIZE = 80 # גודל האויב (משמש בסקיילינג של תמונת האויב)
ENEMY_LIST = [] # רשימה שתכיל את מיקומי האויבים על המסך (x, y)

BULLET_WIDTH = 25 # רוחב הקליע (תואם לתמונת הקליע)
BULLET_HEIGHT = 25 # גובה הקליע (תואם לתמונת הקליע)
BULLET_VEL = 15 # מהירות תנועת הקליע (פיקסלים לפריים כל פעם)
BULLET_LIST = [] # רשימה של כל הקליעים הפעילים
MAX_BULLETS = 5 # כמות מקסימלית של קליעים בו-זמנית על המסך

SCORE = 0 # הניקוד הגלובלי (כברירת מחדל מתחיל ב-0)
POINTS_PER_HIT = 2 # נקודות שהשחקן מקבל על פגיעה באויב
POINTS_PER_ESCAPE = 1 # נקודות אם אויב בורח מהמסך למטה מבלי לפגוע בשחקן

BACKGROUND = pygame.transform.scale(
    pygame.image.load(os.path.join('Assets', 'myBackgr.jpg')),  # טוען רקע
    (WIDTH, HEIGHT)) # מותאם לגודל המסך

PLAYER_IMAGE_RAW = pygame.image.load(os.path.join('Assets', 'player.png')) # טעינת תמונת השחקן
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE_RAW, (PLAYER_SIZE, PLAYER_SIZE)) # שינוי גודל השחקן

ENEMY_IMAGE_RAW = pygame.image.load(os.path.join('Assets', 'terrorist.png'))  # טעינת תמונת האויב
ENEMY_IMAGE = pygame.transform.scale(ENEMY_IMAGE_RAW, (ENEMY_SIZE, ENEMY_SIZE))  # שינוי גודל האויב

BULLET_IMAGE_RAW = pygame.image.load(os.path.join('Assets', 'fire.png'))  # טעינת תמונת הקליע
BULLET_IMAGE = pygame.transform.scale(BULLET_IMAGE_RAW, (BULLET_WIDTH, BULLET_HEIGHT))  # שינוי גודל הקליע

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Pain_Sound.mp3'))  # צליל פגיעה
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Shot_Sound.mp3'))  # צליל ירי

NO_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'No_Sound.mp3'))  # צליל פסילה (כשאויב פוגע בשחקן)
GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Game_Over_Sound.mp3'))  # צליל סיום משחק

GAME_OVER_BG = pygame.transform.scale(
    pygame.image.load(os.path.join('Assets', 'game_over.JPG')),  #טעינת רקע למסך ה Game Over
    (WIDTH, HEIGHT)  # מקננים לגודל המסך
)

pygame.font.init()  # אתחול של פונקציות הפונט
FONT = pygame.font.SysFont('comicsans', 30) # גופן בסיסי בגודל 30
BIG_FONT = pygame.font.SysFont('comicsans', 60) # גופן גדול בגודל 60

screen = pygame.display.set_mode((WIDTH, HEIGHT)) # יצירת חלון המשחק ברזולוציה המתאימה
pygame.display.set_caption("Combined Game - Tank Version") # כותרת החלון
clock = pygame.time.Clock()  # שעון המשמש להגבלת FPS

def set_level(score):
    
    # משדרג את המהירות (enemy_speed) וכמות האויבים (max_enemies) בכל 50 נקודות
    # ככל שהניקוד עולה, רמת הקושי עולה
    base_speed = 5   # מהירות בסיסית
    base_enemies = 5 # כמות אויבים בסיסית
    increments = score // 50  # כמה פעמים עברת 50 נקודות 
    new_speed = base_speed + increments * 5 # בכל מעבר 50 נק' מגדיל ב-5
    new_max_enemies = base_enemies + increments * 5 # וכן לכמות האויבים
    return new_speed, new_max_enemies

def draw_centered_text(surface, text, font, color, y):
    render = font.render(text, True, color) # מייצר אובייקט טקסט
    text_width = render.get_width() # בודק את רוחב הטקסט
    x = (WIDTH - text_width) // 2 # חישוב נקודת הציור באמצע המסך
    surface.blit(render, (x, y)) # מייצר את הטקסט במיקום המחושב

def draw_text(surface, text, font, color, x, y):
    label = font.render(text, True, color) # מייצר את אובייקט הטקסט
    surface.blit(label, (x, y)) # מייצר אותו במיקום המבוקש

def drop_enemies(enemy_list, enemy_size, current_max_enemies):
    # פונקציה ליצירת אויבים חדשים רנדומליים בראש המסך 
    # בודקת אם כמות האויבים < המקסימום, וכן מוסיפה אויב בהסתברות 20% (delay<0.2).
    delay = random.random() # מספר רנדומלי בין 0 ל-1
    if len(enemy_list) < current_max_enemies and delay < 0.2:
        x_pos = random.randint(0, WIDTH - enemy_size) # מיקום X אקראי
        y_pos = 0 # בראש המסך
        enemy_list.append([x_pos, y_pos]) # מוסיף לרשימת האויבים

def draw_enemies(surface, enemy_list, enemy_size):
    # מצייר את כל האויבים מהרשימה (לפי הקואורדינטות שלהם)
    for enemy_pos in enemy_list:
        surface.blit(ENEMY_IMAGE, (enemy_pos[0], enemy_pos[1]))

def update_enemy_positions(enemy_list, enemy_size, score, player_rect, lives, enemy_speed):
    for idx, enemy_pos in enumerate(enemy_list):
        if 0 <= enemy_pos[1] < HEIGHT:
            enemy_pos[1] += enemy_speed  # מזיז את האויב למטה לפי enemy_speed
        else:
            enemy_list.pop(idx) # האויב יצא מהמסך
            score += POINTS_PER_ESCAPE # קבלת נקודות על כל התחמקות מהאויב

    new_enemy_list = []
    for enemy_pos in enemy_list:
        enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
        # בודקים התנגשות בין מלבן האויב למלבן השחקן (player_rect)
        if player_rect.colliderect(enemy_rect):
            lives -= 1 # פגיעה בשחקן
            NO_SOUND.play() # צליל פסילה
        else:
            new_enemy_list.append(enemy_pos)

    enemy_list = new_enemy_list
    return score, lives, enemy_list

def draw_player(surface, player_rect):
    # מצייר את השחקן לפי המיקום של player_rect (x,y).
    surface.blit(PLAYER_IMAGE, (player_rect.x, player_rect.y))

def draw_bullets(surface, bullets):
    # מייצר את כל הקליעים לפי מיקומם ברשימה.
    for bullet in bullets:
        surface.blit(BULLET_IMAGE, (bullet.x, bullet.y))
def handle_bullets(bullet_list, enemy_list, score):
    # מעדכן תנועת הקליעים כלפי מעלה ובודק פגיעות באויבים
    # על פגיעה באויב => הניקוד עולה ב-2, משמיעים צליל BULLET_HIT_SOUND
    # מחזיר רשימות מעודכנות ואת הניקוד    
    new_bullet_list = []
    for bullet in bullet_list:
        bullet.y -= BULLET_VEL  # מזיז את הקליע מעלה ב-BULLET_VEL
        if bullet.y < 0:
            # אם יצא מעל המסך
            continue
        hit_index = None
        for i, enemy_pos in enumerate(enemy_list):
            enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], ENEMY_SIZE, ENEMY_SIZE)
            # אם הקליע פוגע באויב
            if bullet.colliderect(enemy_rect):
                BULLET_HIT_SOUND.play()
                score += POINTS_PER_HIT
                hit_index = i
                break
        if hit_index is not None:
            enemy_list.pop(hit_index) # מסירים את האויב שנפגע
        else:
            new_bullet_list.append(bullet)
    return new_bullet_list, enemy_list, score

def game_over_screen(final_score):
    GAME_OVER_SOUND.play()  # קול פסילה

    # מציג רקע Game Over + הודעה להמתין
    screen.blit(GAME_OVER_BG, (0, 0))
    draw_centered_text(screen, "Game Over!", BIG_FONT, WHITE, HEIGHT//2 - 80)
    draw_centered_text(screen, f"Your score: {final_score}", FONT, WHITE, HEIGHT//2 - 20)
    draw_centered_text(screen, "Please wait 3 seconds...", FONT, WHITE, HEIGHT//2 + 20)
    pygame.display.update()

    pygame.time.delay(3000)   # השהייה של 3 שניות
    pygame.event.clear()      # מנקים את תור האירועים כדי שלא ילחצו דברים ישנים

    # כעת מציג תפריט הודעה ללחוץ מקש כדי לשחק שוב
    screen.blit(GAME_OVER_BG, (0, 0))
    draw_centered_text(screen, "Game Over!", BIG_FONT, WHITE, HEIGHT//2 - 80)
    draw_centered_text(screen, f"Your score: {final_score}", FONT, WHITE, HEIGHT//2 - 20)
    draw_centered_text(screen, "Press any key to play again or ESC to quit", FONT, WHITE, HEIGHT//2 + 20)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # אם סוגרים את החלון
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # אם לוחצים מקש כלשהו
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    waiting = False  # יוצאים מהלולאה, ממשיכים למשחק חדש

def main_game():

    # מפעיל ריצת משחק אחת מאפס:
    # - מאפס ניקוד, אויבים, קליעים, וחיים.
    # - רץ בלולאה עד שהחיים נגמרים או סוגרים את המשחק.
    # - בסיום קורא ל-game_over_screen(SCORE).
    
    global SCORE, ENEMY_LIST, BULLET_LIST  # מצהיר שמשתמשים במשתנים גלובליים

    SCORE = 0 # ניקוד התחלתי
    ENEMY_LIST = [] # איפוס רשימת האויבים
    BULLET_LIST = [] # איפוס רשימת הקליעים
    lives = PLAYER_LIVES  # כמות החיים ההתחלתית

    # הגדרת מלבן המייצג את מיקום וגודל השחקן
    player_rect = pygame.Rect(
        WIDTH // 2 - (PLAYER_SIZE // 2), # מיקום X (אמצע המסך)
        HEIGHT - 2 * PLAYER_SIZE, # מיקום Y (קרוב לתחתית)
        PLAYER_SIZE, # רוחב
        PLAYER_SIZE) # גובה

    running = True # בודק אם המשחק עדיין רץ
    while running:
        clock.tick(FPS) # הגבלת קצב הפריימים ל

        # מחשב רמת קושי בהתאם לניקוד
        enemy_speed, current_max_enemies = set_level(SCORE)

        # קלט אירועים (סגירת חלון, לחיצות מקשים)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # אם נסגר חלון
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(BULLET_LIST) < MAX_BULLETS:
                    # אם לחצו רווח ויש פחות מ-5 קליעים
                    bullet = pygame.Rect(
                        player_rect.x + player_rect.width // 2 - BULLET_WIDTH // 2,
                        player_rect.y,
                        BULLET_WIDTH,
                        BULLET_HEIGHT
                    )
                    BULLET_LIST.append(bullet)
                    BULLET_FIRE_SOUND.play()  # צליל ירי

        # תנועת השחקן בעזרת החצים
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.x - PLAYER_VEL > 0:
            player_rect.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player_rect.x + PLAYER_VEL + player_rect.width < WIDTH:
            player_rect.x += PLAYER_VEL
        if keys[pygame.K_UP] and player_rect.y - PLAYER_VEL > 0:
            player_rect.y -= PLAYER_VEL
        if keys[pygame.K_DOWN] and player_rect.y + PLAYER_VEL + player_rect.height < HEIGHT:
            player_rect.y += PLAYER_VEL

        # מחיקת אויבים
        drop_enemies(ENEMY_LIST, ENEMY_SIZE, current_max_enemies)

        # עדכון מיקום האויבים + חיים וניקוד
        SCORE, lives, ENEMY_LIST = update_enemy_positions(
            ENEMY_LIST,
            ENEMY_SIZE,
            SCORE,
            player_rect,
            lives,
            enemy_speed
        )

        # עדכון הקליעים (תנועה מעלה + בדיקת פגיעה באויבים)
        BULLET_LIST, ENEMY_LIST, SCORE = handle_bullets(BULLET_LIST, ENEMY_LIST, SCORE)

        # אם החיים נגמרו => סוף משחק
        if lives <= 0:
            running = False
            game_over_screen(SCORE)  # מציג מסך Game Over
            break

        # יצירת רקע
        screen.blit(BACKGROUND, (0, 0))
        # יצירת השחקן
        draw_player(screen, player_rect)
        # יצירת האויבים
        draw_enemies(screen, ENEMY_LIST, ENEMY_SIZE)
        # יצירת הקליעים
        draw_bullets(screen, BULLET_LIST)

        # הצגת כמות החיים והניקוד
        draw_text(screen, f"Lives: {lives}", FONT, WHITE, 10, 10)
        draw_text(screen, f"Score: {SCORE}", FONT, WHITE, WIDTH - 150, 10)

        pygame.display.update()  # עדכון המסך בפריים
def main():
    
    # לולאה אינסופית המריצה את main_game  שוב ושוב
    # לאחר כל סיום משחק (Game Over), חוזר לכאן ומתחיל משחק חדש
    
    while True:
        main_game()

if __name__ == "__main__":
    main()  # מפעיל את הפונקציה הראשית
