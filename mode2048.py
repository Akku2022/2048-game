import pygame
import random
import json
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 500  # Base dimensions
TILE_SIZE = 100
GRID_SIZE = 4
FPS = 60
THEMES = {
    "Light": {
        "background": (255, 255, 255),  # White
        "text": (0, 0, 0),  # Black
        "tiles": {
            0: (204, 192, 179),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46)
        }
    },
    "Dark": {
        "background": (50, 50, 50),  # Dark gray
        "text": (255, 255, 255),  # White
        "tiles": {
            0: (100, 100, 100),
            2: (150, 150, 150),
            4: (200, 200, 200),
            8: (255, 200, 200),
            16: (255, 150, 150),
            32: (255, 100, 100),
            64: (255, 50, 50),
            128: (200, 50, 50),
            256: (150, 50, 50),
            512: (100, 50, 50),
            1024: (50, 50, 50),
            2048: (0, 0, 0)
        }
    }
}
current_theme = "Light"  # Default theme

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("2048 Game")
clock = pygame.time.Clock()

# Initialize the grid, score, and game state
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0
high_score = 0
previous_state = []
undo_limit = 3  # Limit undo moves
moves = 0
start_time = time.time()
time_limit = 300  # 5 minutes for timed mode
timed_mode = False

# Load high score from file
try:
    with open("2048_high_score.json", "r") as f:
        high_score = json.load(f)
except FileNotFoundError:
    pass

# Sound effects
pygame.mixer.init()
move_sound = pygame.mixer.Sound("dragslide3-101237.mp3")
merge_sound = pygame.mixer.Sound("newmerge.mp3")
game_over_sound = pygame.mixer.Sound("game-over-arcade-6435.mp3")

# Function to play sound for 1 second
def play_sound_for_1_second(sound):
    channel = pygame.mixer.find_channel()  # Find an available channel
    if channel:
        channel.play(sound)  # Play the sound
        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Set a timer for 1 second

# Add a random tile (either 2 or 4)
def add_random_tile():
    empty_tiles = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if grid[x][y] == 0]
    if empty_tiles:
        x, y = random.choice(empty_tiles)
        grid[x][y] = random.choice([2, 4])

# Draw the grid, score, and statistics
def draw_grid():
    screen.fill(THEMES[current_theme]["background"])  # Use theme background color
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            value = grid[x][y]
            color = THEMES[current_theme]["tiles"].get(value, THEMES[current_theme]["background"])
            pygame.draw.rect(screen, color, (y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if value != 0:
                font = pygame.font.SysFont("comicsans", 40)
                text = font.render(str(value), True, THEMES[current_theme]["text"])  # Use theme text color
                text_rect = text.get_rect(center=(y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2))
                screen.blit(text, text_rect)
    
    # Draw the score, high score, and statistics
    font = pygame.font.SysFont("comicsans", 30)
    score_text = font.render(f"Score: {score}", True, THEMES[current_theme]["text"])
    high_score_text = font.render(f"High Score: {high_score}", True, THEMES[current_theme]["text"])
    moves_text = font.render(f"Moves: {moves}", True, THEMES[current_theme]["text"])
    time_elapsed = int(time.time() - start_time)
    time_text = font.render(f"Time: {time_elapsed}s", True, THEMES[current_theme]["text"])
    screen.blit(score_text, (10, HEIGHT - 100))
    screen.blit(high_score_text, (10, HEIGHT - 70))
    screen.blit(moves_text, (10, HEIGHT - 40))
    screen.blit(time_text, (10, HEIGHT - 10))

# Move tiles in a direction
def move(direction):
    global score, moves
    moved = False
    if direction == "left":
        for x in range(GRID_SIZE):
            for y in range(1, GRID_SIZE):
                if grid[x][y] != 0:
                    for z in range(y, 0, -1):
                        if grid[x][z - 1] == 0:
                            grid[x][z - 1], grid[x][z] = grid[x][z], grid[x][z - 1]
                            moved = True
                        elif grid[x][z - 1] == grid[x][z]:
                            grid[x][z - 1] *= 2
                            score += grid[x][z - 1]
                            grid[x][z] = 0
                            moved = True
                            play_sound_for_1_second(merge_sound)
                            break
    elif direction == "right":
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE - 2, -1, -1):
                if grid[x][y] != 0:
                    for z in range(y, GRID_SIZE - 1):
                        if grid[x][z + 1] == 0:
                            grid[x][z + 1], grid[x][z] = grid[x][z], grid[x][z + 1]
                            moved = True
                        elif grid[x][z + 1] == grid[x][z]:
                            grid[x][z + 1] *= 2
                            score += grid[x][z + 1]
                            grid[x][z] = 0
                            moved = True
                            play_sound_for_1_second(merge_sound)
                            break
    elif direction == "up":
        for y in range(GRID_SIZE):
            for x in range(1, GRID_SIZE):
                if grid[x][y] != 0:
                    for z in range(x, 0, -1):
                        if grid[z - 1][y] == 0:
                            grid[z - 1][y], grid[z][y] = grid[z][y], grid[z - 1][y]
                            moved = True
                        elif grid[z - 1][y] == grid[z][y]:
                            grid[z - 1][y] *= 2
                            score += grid[z - 1][y]
                            grid[z][y] = 0
                            moved = True
                            play_sound_for_1_second(merge_sound)
                            break
    elif direction == "down":
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE - 2, -1, -1):
                if grid[x][y] != 0:
                    for z in range(x, GRID_SIZE - 1):
                        if grid[z + 1][y] == 0:
                            grid[z + 1][y], grid[z][y] = grid[z][y], grid[z + 1][y]
                            moved = True
                        elif grid[z + 1][y] == grid[z][y]:
                            grid[z + 1][y] *= 2
                            score += grid[z + 1][y]
                            grid[z][y] = 0
                            moved = True
                            play_sound_for_1_second(merge_sound)
                            break
    if moved:
        moves += 1
        play_sound_for_1_second(move_sound)
    return moved

# Check if the player has won
def has_won():
    for row in grid:
        if 2048 in row:
            return True
    return False

# Check if the game is over
def is_game_over():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x][y] == 0:
                return False
            if x < GRID_SIZE - 1 and grid[x][y] == grid[x + 1][y]:
                return False
            if y < GRID_SIZE - 1 and grid[x][y] == grid[x][y + 1]:
                return False
    return True

# Save high score to file
def save_high_score():
    with open("2048_high_score.json", "w") as f:
        json.dump(high_score, f)

# Undo the last move
def undo():
    global grid, score, previous_state
    if previous_state:
        grid, score = previous_state.pop()

# Main game loop
def main():
    global grid, score, high_score, previous_state, moves, start_time, timed_mode, current_theme, TILE_SIZE, WIDTH, HEIGHT

    add_random_tile()
    add_random_tile()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                TILE_SIZE = min(WIDTH, HEIGHT) // GRID_SIZE
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL and len(previous_state) > 0 and undo_limit > 0:  # Ctrl+Z to undo
                    undo()
                    undo_limit -= 1
                elif event.key == pygame.K_t:  # Toggle timed mode
                    timed_mode = not timed_mode
                    start_time = time.time()
                elif event.key == pygame.K_m:  # Toggle light/dark mode
                    current_theme = "Dark" if current_theme == "Light" else "Light"
                else:
                    moved = False
                    if event.key == pygame.K_LEFT:
                        moved = move("left")
                    elif event.key == pygame.K_RIGHT:
                        moved = move("right")
                    elif event.key == pygame.K_UP:
                        moved = move("up")
                    elif event.key == pygame.K_DOWN:
                        moved = move("down")
                    if moved:
                        previous_state.append(([row[:] for row in grid], score))
                        add_random_tile()
                        if has_won():
                            print("You Win!")
                            running = False
                        if is_game_over():
                            print("Game Over!")
                            play_sound_for_1_second(game_over_sound)
                            running = False

        # Check timed mode
        if timed_mode and time.time() - start_time > time_limit:
            print("Time's up!")
            play_sound_for_1_second(game_over_sound)
            running = False

        # Update high score
        if score > high_score:
            high_score = score
            save_high_score()

        draw_grid()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()