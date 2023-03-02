#!/usr/bin/env python3
from random import choice
import pygame as pg
from game import GameState
from moves import Move
import AImove as ai
from graphics import CELL_SIZE, FULL_WIDTH, WIDTH, HEIGHT, IMAGES, ANIMATIONS, \
    loadPieces, animateMove, drawGame

# If 1 cpu is on, it would take this player ("b" = black, "w" = white)
default_cpu = "b"
# 0 to 2 cpus
cpus = 0

def player_move(gamestate, moveMade, sqClicked, history_sqClicked):

    location = pg.mouse.get_pos()  # (x , y)
    validMove = ""

    if 0 <= location[0] <= WIDTH:
        col = location[0] // CELL_SIZE
        row = location[1] // CELL_SIZE
        if sqClicked == (row, col):  # if click same square twice
            sqClicked = ()
            history_sqClicked = []

        else:  # if you do two different square clicks

            sqClicked = (row, col)
            history_sqClicked.append(sqClicked)

        if len(history_sqClicked) == 2:  # after 2nd click
            move = Move(history_sqClicked[0], history_sqClicked[1], gamestate.fake_FEN)

            
            if move in gamestate.validMoves:
                #Need to send the valid move, not the move i just created
                selectedMove = gamestate.validMoves.index(move) 
                
                validMove = gamestate.validMoves[selectedMove]
                moveMade = True

                sqClicked = ()
                history_sqClicked = []

            else:

                history_sqClicked = [sqClicked]

    return validMove, moveMade, sqClicked, history_sqClicked

def main():

    pg.init()
    screen = pg.display.set_mode((FULL_WIDTH, HEIGHT))
    clock = pg.time.Clock()
    FPS = 60
    screen.fill(0)
    
    loadPieces(IMAGES)

    gamestate = GameState()
    sqClicked = ()  # last click of the user
    history_sqClicked = []  # keeps track of player clicks in tuples ()
    moveMade = False
    animate = False

    # Initialize the scroll position to zero
    scroll_pos = 0

    run = True
    while run:
        clock.tick(FPS)
        screen.fill(0)
        drawGame(screen, gamestate, sqClicked)


        for event in pg.event.get():  # Esto te permite usar la X pa salir del programa
            if event.type == pg.QUIT:
                print(gamestate.fake_FEN)
                run = False

            #---------------------Undo Move and reset game -------------------------------------------------------
            if event.type == pg.KEYDOWN:
                # Undo Move if game continues
                if event.key == pg.K_SPACE and not gamestate.gameOver:  # K_SPACE can be replaced by any key
                    # So i cant undo if only the initial board has been played
                    if cpus != 0:
                        # undo last two moves
                        if len(gamestate.history_Boards) > 2:
                            last_played = gamestate.undoMove()
                            last_played = gamestate.undoMove()
                    else:
                        if len(gamestate.history_Boards) > 1:
                            last_played = gamestate.undoMove()
                
                # Reset Game... press 'r'
                if event.key == pg.K_r:
                    gamestate = GameState()

                    sqClicked = ()  # last click of the user
                    history_sqClicked = []  # keeps track of player clicks in tuples ()
                    moveMade = False
                    animate = False

                #Random Move
                if event.key == pg.K_n:
                    validMove = ai.random_move(gamestate.validMoves)
                    moveMade = True

            elif event.type == pg.MOUSEBUTTONDOWN:
                validMove, moveMade, sqClicked, history_sqClicked = player_move(gamestate, moveMade, sqClicked, history_sqClicked)
        #---------------------------------------------------------------------------------


        #--------------AI PLAYING---------------------------------------------
        if 0 < cpus < 3:

            #Cpu controlls two players or 1            
            vsCpus = (gamestate.player_toMove == default_cpu or "w") if cpus == 2 else (gamestate.player_toMove == default_cpu)                          

            #If cpus turns to move and game not over
            if vsCpus and not gamestate.gameOver:
                #validMove = ai.simple_minmax_algorithm(gamestate)
                validMove = ai.findBestMove(gamestate)
                if validMove is None:
                    validMove = ai.greedy_algorithm(gamestate)

                moveMade = True
                
        #-----------------------------------------------------------------------                

        if moveMade and not gamestate.gameOver:
            gamestate.update(gamestate.makeMove(validMove))
            moveMade = False
            if ANIMATIONS:
                animateMove(screen, gamestate.history_Moves[-1], gamestate, clock, FPS)
            



if __name__ == "__main__":
    main()
