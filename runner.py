import pygame
import sys
import time

import tic_tac_toe as ttt

pygame.init()

size = width, height = 600, 400

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

screen = pygame.display.set_mode(size)

medium_font = pygame.font.Font("OpenSans-Regular.ttf", 30)
move_font = pygame.font.Font("OpenSans-Regular.ttf", 60)
small_font = pygame.font.Font("OpenSans-Regular.ttf", 20)

user = None

board = ttt.initial_state()

bot_turn = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)

    # Let user choose a player
    if user is None:
        # Draw title
        title = medium_font.render("Play Tic-Tac-Toe", True, white)

        title_rect = title.get_rect()
        title_rect.center = ((width / 2), 50)

        screen.blit(title, title_rect)

        # X button
        play_X_button = pygame.Rect((width / 8), (height / 2), width / 4, 50)

        play_X = small_font.render("Play as X", True, black)

        play_X_rect = play_X.get_rect()
        play_X_rect.center = play_X_button.center

        pygame.draw.rect(screen, white, play_X_button)

        screen.blit(play_X, play_X_rect)

        # O button
        play_O_button = pygame.Rect(5 * (width / 8), (height / 2), width / 4, 50)

        play_O = small_font.render("Play as O", True, black)

        play_O_rect = play_O.get_rect()
        play_O_rect.center = play_O_button.center

        pygame.draw.rect(screen, white, play_O_button)

        screen.blit(play_O, play_O_rect)

        # Check if button is clicked
        click, _, _ = pygame.mouse.get_pressed()

        if click == 1:
            x, y = pygame.mouse.get_pos()

            if play_X_button.collidepoint(x, y):
                time.sleep(0.2)

                user = ttt.X
            elif play_O_button.collidepoint(x, y):
                time.sleep(0.2)

                user = ttt.O
    else:
        # Draw game board
        tile_size = 80

        tile_origin = (width / 2 - (1.5 * tile_size),
                       height / 2 - (1.5 * tile_size))

        tiles = list()

        for i in range(3):
            row = list()

            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )

                pygame.draw.rect(screen, white, rect, 3)

                if board[i][j] != ttt.EMPTY:
                    move = move_font.render(board[i][j], True, white)

                    move_rect = move.get_rect()
                    move_rect.center = rect.center

                    screen.blit(move, move_rect)

                row.append(rect)

            tiles.append(row)

        game_over = ttt.terminal(board)
        
        player = ttt.player(board)

        # Show title
        if game_over:
            winner = ttt.winner(board)

            if winner is None:
                title = f"Game Over: Tie!"
            else:
                title = f"Game Over: {winner} wins!"
        elif user == player:
            title = f"Playing as {user}"
        else:
            title = f"Computer thinking..."

        title = medium_font.render(title, True, white)

        title_rect = title.get_rect()
        title_rect.center = ((width / 2), 30)

        screen.blit(title, title_rect)

        # Check for AI move
        if user != player and not game_over:
            if bot_turn:
                time.sleep(0.5)

                move = ttt.minimax(board)
                
                board = ttt.result(board, move)

                bot_turn = False
            else:
                bot_turn = True

        # Check for a user move
        click, _, _ = pygame.mouse.get_pressed()

        if click == 1 and user == player and not game_over:
            x, y = pygame.mouse.get_pos()

            for i in range(3):
                for j in range(3):
                    if board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(x, y):
                        board = ttt.result(board, (i, j))

        if game_over:
            again_button = pygame.Rect(width / 3, height - 65, width / 3, 50)

            again = small_font.render("Play Again", True, black)

            again_rect = again.get_rect()
            again_rect.center = again_button.center

            pygame.draw.rect(screen, white, again_button)

            screen.blit(again, again_rect)

            click, _, _ = pygame.mouse.get_pressed()

            if click == 1:
                x, y = pygame.mouse.get_pos()

                if again_button.collidepoint(x, y):
                    time.sleep(0.2)

                    user = None

                    board = ttt.initial_state()

                    bot_turn = False

    pygame.display.flip()
