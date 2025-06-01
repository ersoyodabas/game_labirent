import pygame
import speech_recognition as sr
import threading
import time
from gtts import gTTS
import os

# --- Oyun Ayarları ---
ROWS, COLS = 10, 10
CELL_SIZE = 60
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + 40
WHITE, BLACK, BLUE, GREEN, RED = (255, 255, 255), (0, 0, 0), (0, 100, 255), (0, 255, 0), (255, 0, 0)

maze = [
    [0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
]

player_pos = [0, 0]
goal = [9, 9]
last_command = ""
game_over = False

# --- Pygame Başlat ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Sesli Labirent (Google Speech)")
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

# --- Pygame Müzik Başlat ---
pygame.mixer.init()

def draw_maze():
    screen.fill(WHITE)
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = BLACK if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    py, px = player_pos
    pygame.draw.rect(screen, BLUE, (px * CELL_SIZE + 8, py * CELL_SIZE + 8, CELL_SIZE - 16, CELL_SIZE - 16))
    gy, gx = goal
    pygame.draw.rect(screen, GREEN, (gx * CELL_SIZE + 10, gy * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20))
    label = font.render(f"🎙️ {last_command}", True, RED)
    screen.blit(label, (10, HEIGHT - 30))

def play_win_sound():
    tts = gTTS("Tebrikler, hedefe ulaştınız.", lang="tr")
    tts.save("win.mp3")
    pygame.mixer.music.load("win.mp3")
    pygame.mixer.music.play()

def move(direction, is_max=False):
    global game_over
    y, x = player_pos
    while True:
        new_y, new_x = y, x
        if direction == "yukarı": new_y -= 1
        elif direction == "aşağı": new_y += 1
        elif direction == "sol": new_x -= 1
        elif direction == "sağ": new_x += 1

        if 0 <= new_y < ROWS and 0 <= new_x < COLS and maze[new_y][new_x] == 0:
            player_pos[0], player_pos[1] = new_y, new_x
            y, x = new_y, new_x

            # ✅ Hedefe ulaşıldıysa
            if [y, x] == goal:
                print("🎉 Tebrikler! Hedefe ulaştınız.")
                threading.Thread(target=play_win_sound, daemon=True).start()
                game_over = True
                break

            if is_max:
                draw_maze()
                pygame.display.flip()
                time.sleep(0.2)
            else:
                break
        else:
            break

def listen_commands():
    global last_command, game_over
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    command_map = {
        "yukarı": ["yukarı", "yukari", "yukarıya", "yukar", "yükarı"],
        "aşağı": ["aşağı", "asagi", "aşşağı", "aşşa", "aşa", "aşagı", "aşığı"],
        "sol": ["sol", "soll", "sola", "sool", "soul"],
        "sağ": ["sağ", "sag", "sa", "sağa", "saağ", "sağa", "saha"]
    }

    with mic as source:
        print("🎤 Mikrofon ayarlanıyor (gürültü kalibrasyonu)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Hazır. Komut bekleniyor...")

        while not game_over:
            try:
                print("🎙️ Dinleniyor...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)
                text = recognizer.recognize_google(audio, language="tr-TR").lower()
                print(f"🗣️ Algılanan: {text}")
                last_command = text

                for word in text.split():
                    for direction, aliases in command_map.items():
                        if word in aliases:
                            move(direction, is_max="en" in text)
                            time.sleep(0.2)
                            break

            except sr.WaitTimeoutError:
                print("⏱️ Zaman aşımı, tekrar dinleniyor...")
            except sr.UnknownValueError:
                print("🤷 Anlaşılamadı.")
            except sr.RequestError as e:
                print(f"❌ Google Hatası: {e}")

# --- Dinleme iş parçacığını başlat ---
threading.Thread(target=listen_commands, daemon=True).start()

# --- Ana Döngü ---
running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or game_over:
            running = False

    draw_maze()
    pygame.display.flip()

pygame.quit()
