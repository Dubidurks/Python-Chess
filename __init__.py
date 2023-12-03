#!/usr/bin/env python3
from random import choice
import os
from stockfish import Stockfish
#Dont show initial banner of pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame as pg
from multiprocessing import Process, Queue
from game import GameState
from moves import Move, coordX, coordY
import AImove as ai
from graphics import CELL_SIZE, FULL_WIDTH, WIDTH, HEIGHT, IMAGES, ANIMATIONS, \
    loadPieces, animateMove, drawGame


#"human" or "cpu" or "stockfish"
blacks_player = "stockfish"
whites_player = "cpu"

stockfishOn = True if blacks_player == "stockfish" or whites_player == "stockfish" else False

if stockfishOn:
    stockfish = Stockfish(path="Engine/stockfish/stockfish-windows-x86-64-avx2.exe", depth=20, parameters={"Threads": 2})

def stockfishBestMove(gamestate, returnQueue=None):

    fen = f'{gamestate.current_FEN} 0 1'
    stockfish.set_fen_position(fen)
    engineMove = stockfish.get_best_move()

    validMoves = gamestate.validMoves
    
    bestMove = object
    for move in validMoves:
        startCol = move.startCol
        startRow = move.startRow
        endCol = move.endCol
        endRow = move.endRow
        
        moveNotation = f'{str(coordX[startCol]) + str(coordY[startRow])}{str(coordX[endCol])}{str(coordY[endRow])}'
        
        if moveNotation == engineMove:
            bestMove = move
            break
    nextMove = bestMove
    evaluation = stockfish.get_evaluation()['value']
    print(nextMove, evaluation)

    if returnQueue != None:
        return returnQueue.put(nextMove)
    else:
        return nextMove

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
            
            #See if human to play
            human_toPlay = True if (gamestate.player_toMove == "w" and whites_player == "human") or (gamestate.player_toMove == "b" and blacks_player == "human") else False
            
            if move in gamestate.validMoves and human_toPlay:
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

    #To bein able to interact with the board while the ai thinks
    AiThinking = False
    moveFinderProcess = None

    run = True
    while run:
        clock.tick(FPS)
        screen.fill(0)
        drawGame(screen, gamestate, sqClicked)

        # Allow to use the X to close the window
        for event in pg.event.get():  
            if event.type == pg.QUIT:
                run = False
                if AiThinking:
                        validMoveProcess.terminate()

            #---------------------Undo Move and reset game -------------------------------------------------------
            if event.type == pg.KEYDOWN:
                # Undo Move if game continues
                if event.key == pg.K_SPACE and not gamestate.gameOver:  # K_SPACE can be replaced by any key
                    if blacks_player == whites_player == "cpu":
                        # undo last two moves
                        if len(gamestate.history_Boards) > 2:
                            gamestate.undoMove()
                            gamestate.undoMove()

                    else:
                    # So i cant undo if only the initial board has been played
                        if len(gamestate.history_Boards) > 1:
                            last_played = gamestate.undoMove()
                    
                    if AiThinking:
                        validMoveProcess.terminate()
                        AiThinking = False
                
                # Reset Game... press 'r'
                if event.key == pg.K_r:
                    gamestate = GameState()

                    sqClicked = ()  # last click of the user
                    history_sqClicked = []  # keeps track of player clicks in tuples ()
                    moveMade = False
                    animate = False
                if event.key == pg.K_s:
                    print(gamestate.current_FEN)

                #Random Move
                if event.key == pg.K_n:
                    #validMove = ai.random_move(gamestate.validMoves)
                    validMove = ai.findBestMove(gamestate)
                    moveMade = True

            elif event.type == pg.MOUSEBUTTONDOWN:
                if not gamestate.gameOver:
                    validMove, moveMade, sqClicked, history_sqClicked = player_move(gamestate, moveMade, sqClicked, history_sqClicked)
        #---------------------------------------------------------------------------------


        #--------------AI PLAYING---------------------------------------------
        
        #Cpu controlls two players or 1    
        cpu_toPlay = True if (gamestate.player_toMove == "w" and whites_player == "cpu") or (gamestate.player_toMove == "b" and blacks_player == "cpu") or\
                            (gamestate.player_toMove == "w" and whites_player == "stockfish") or (gamestate.player_toMove == "b" and blacks_player == "stockfish")\
                        else False
        
        stockfishMove = True if (gamestate.player_toMove == "w" and whites_player == "stockfish") or (gamestate.player_toMove == "b" and blacks_player == "stockfish") else False
        
        #If cpus turns to move and game not over and not thinking
        if cpu_toPlay and not gamestate.gameOver: 


            if not AiThinking:
                AiThinking = True
                #print("Thinking...")
                #Used to pass data between threads
                returnQueue = Queue()
                
                if stockfishMove:
                    validMoveProcess = Process(target=stockfishBestMove, args=(gamestate, returnQueue))
                else:
                    validMoveProcess = Process(target=ai.findBestMove, args=(gamestate, returnQueue))
                #Call with the parameters
                validMoveProcess.start()

            if not validMoveProcess.is_alive():
                #print("Done thinking")
                validMove = returnQueue.get()
                if validMove is None:
                    validMove = ai.random_move(gamestate.validMoves)

                moveMade = True
                AiThinking = False
            
        #-----------------------------------------------------------------------                

        if moveMade and not gamestate.gameOver:
            gamestate.update(gamestate.makeMove(validMove))
            
            moveMade = False
            if ANIMATIONS:
                animateMove(screen, gamestate.history_Moves[-1], gamestate, clock, FPS)
        
        if gamestate.gameOver and AiThinking:
            validMoveProcess.terminate()
            AiThinking = False
        
if __name__ == "__main__":
    
    main()
