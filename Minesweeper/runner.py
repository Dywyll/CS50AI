import pygame
import sys
import time

from minesweeper import Minesweeper, MinesweeperAI

HEIGHT = 8
WIDTH = 8
MINES = 8

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

# Create game
pygame.init()

size = width, height = 600, 400

screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"

small_font = pygame.font.Font(OPEN_SANS, 20)
medium_font = pygame.font.Font(OPEN_SANS, 30)
large_font = pygame.font.Font(OPEN_SANS, 40)

# Compute board size
BOARD_PADDING = 20

board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)

cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))

board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))

mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)

ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()

lost = False

# Show instructions initially
instructions = True

while True:
    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    # Show game instructions
    if instructions:
        # Title
        title = large_font.render("Play Minesweeper", True, WHITE)

        title_rect = title.get_rect()
        title_rect.center = ((width / 2), 50)

        screen.blit(title, title_rect)

        # Rules
        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!"
        ]

        for i, rule in enumerate(rules):
            line = small_font.render(rule, True, WHITE)

            line_rect = line.get_rect()
            line_rect.center = ((width / 2), 150 + 30 * i)

            screen.blit(line, line_rect)

        # Play game button
        button_rect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)

        button_text = small_font.render("Play Game", True, BLACK)

        button_text_rect = button_text.get_rect()
        button_text_rect.center = button_rect.center

        pygame.draw.rect(screen, WHITE, button_rect)

        screen.blit(button_text, button_text_rect)

        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()

        if click == 1:
            x, y = pygame.mouse.get_pos()

            if button_rect.collidepoint(x, y):
                instructions = False

                time.sleep(0.3)

        pygame.display.flip()

        continue

    # Draw board
    cells = list()

    for i in range(HEIGHT):
        row = list()

        for j in range(WIDTH):
            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )

            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine, flag, or number if needed
            if game.is_mine((i, j)) and lost:
                screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif (i, j) in revealed:
                neighbors = small_font.render(
                    str(game.nearby_mines((i, j))),
                    True, BLACK
                )

                neighbors_text_rect = neighbors.get_rect()
                neighbors_text_rect.center = rect.center

                screen.blit(neighbors, neighbors_text_rect)

            row.append(rect)

        cells.append(row)

    # AI Move button
    ai_button = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )

    button_text = small_font.render("AI Move", True, BLACK)

    button_rect = button_text.get_rect()
    button_rect.center = ai_button.center

    pygame.draw.rect(screen, WHITE, ai_button)

    screen.blit(button_text, button_rect)

    # Reset button
    reset_button = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )

    button_text = small_font.render("Reset", True, BLACK)

    button_rect = button_text.get_rect()
    button_rect.center = reset_button.center

    pygame.draw.rect(screen, WHITE, reset_button)

    screen.blit(button_text, button_rect)

    # Display text
    text = "Lost..." if lost else "Won!" if game.mines == flags else ""

    text = medium_font.render(text, True, WHITE)

    text_rect = text.get_rect()
    text_rect.center = ((5 / 6) * width, (2 / 3) * height)

    screen.blit(text, text_rect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Check for a right-click to toggle flagging
    if right == 1 and not lost:
        x, y = pygame.mouse.get_pos()

        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(x, y) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))

                    time.sleep(0.2)
    elif left == 1:
        x, y = pygame.mouse.get_pos()

        # If AI button clicked, make an AI move
        if ai_button.collidepoint(x, y) and not lost:
            move = ai.make_safe_move()

            if move is None:
                move = ai.make_random_move()

                if move is None:
                    flags = ai.mines.copy()

                    print("No moves left to make.")
                else:
                    print("No known safe moves, AI making random move.")
            else:
                print("AI making safe move.")

            time.sleep(0.2)
        # Reset game state
        elif reset_button.collidepoint(x, y):
            game = Minesweeper(HEIGHT, WIDTH, MINES)

            ai = MinesweeperAI(HEIGHT, WIDTH)

            revealed = set()
            flags = set()

            lost = False

            continue
        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(x, y)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # Make move and update AI knowledge
    if move:
        if game.is_mine(move):
            lost = True
        else:
            nearby = game.nearby_mines(move)

            revealed.add(move)

            ai.add_knowledge(move, nearby)

    pygame.display.flip()
