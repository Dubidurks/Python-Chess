import pygame as pg
from moves import coordX, coordY


MOVES_PANEL_WIDTH = 200 
WIDTH = HEIGHT = 800
FULL_WIDTH = WIDTH + MOVES_PANEL_WIDTH
DIMENSION = 8
CELL_SIZE = HEIGHT // DIMENSION
IMAGES = {}

# For move animations
ANIMATIONS = True

#Board Colors
COLORS = ((255, 204, 153), (204, 102, 0))

#Rectangle for the image of the piece
def rectImage(col, row):
    k = WIDTH / 40
    return pg.Rect(col * CELL_SIZE + k, row * CELL_SIZE + k, CELL_SIZE + k / 2, CELL_SIZE + k / 2)

#Load images
def loadPieces(IMAGES):
    pieces = ['bb', 'bk', 'bq', 'bn', 'bp',
              'br', 'wb', 'wk', 'wn', 'wp', 'wq', 'wr']
    for piece in pieces:
        IMAGES[piece] = pg.image.load("images/" + piece + ".png")

def moves_panel(screen, gamestate):
    # panel rectangle. Starts where the board ends (at WIDTH)
    panel_rect = pg.Rect(WIDTH, 0, MOVES_PANEL_WIDTH, HEIGHT)
    panel_color = (0, 0, 0)
    text_color = (255, 255, 255)
    panel_surface = pg.Surface(panel_rect.size)
    panel_surface.fill(panel_color)

    # set up the title
    title_font = pg.font.SysFont('Times New Roman', 22)
    title_font.set_underline(True)
    title_font.set_italic(True)    
    log_moves_title = title_font.render("Moves Log", True, (155, 0, 155))
    panel_surface.blit(log_moves_title, (50, log_moves_title.get_height()))

    # Moves. 2 moves per turn
    moves_font = pg.font.SysFont('Times New Roman', 22)
    log_moves = gamestate.history_Moves
    between_turns = 10 + moves_font.get_height()
    between_moves = 10
    # max number of moves that can fit in the panel (1 turn, 2 moves (that's why * 2 and the -2 is to not go pass the panel height))
    max_moves = (panel_surface.get_height() // between_turns) * 2 - 2  

    # If there are more moves than can fit, only show the most recent moves
    num_moves = min(max_moves, len(log_moves))
    start_move = len(log_moves) - num_moves
    end_move = len(log_moves)

    #This variable is to avoid writing a black move if there's no white move showing. Same withe if move_label != "" above
    past_move_label_width = None

    #Height starts past the title + 10
    height = log_moves_title.get_height() + 10
    #One label for each move (2 moves = 1 turn)
    for x in range(start_move, end_move):
        move_label = ""
        width = 30
        
        #White move
        if x % 2 == 0:
            turn_index = x // 2 + 1
            #New Turn
            move_label = f"{turn_index}. {log_moves[x].getChessNotation()}"
            height += between_turns

            past_move_label_width = moves_font.render(move_label, True, text_color).get_width()

        #Black Move
            #Avoid writing black move if not past_move_label
        elif x % 2 == 1 and past_move_label_width != None:
            #New Move, same Turn
            move_label = f"{log_moves[x].getChessNotation()}"
            #Use the white move label to manage the distance between moves
            width = width + past_move_label_width + between_moves

            #Reset past_move_label
            past_move_label_width = None
         
        #Avoid showing the first black move at the top when at the bottom ther's only a white move
        if move_label != "":
            move_label_surface = moves_font.render(move_label, True, text_color)
            panel_surface.blit(move_label_surface, (width, height))

    # Display the panel
    screen.blit(panel_surface, panel_rect)


def end_game(screen, gamestate):

    font = pg.font.SysFont('Times New Roman', 40)
    if gamestate.checkMate:
        winner = "Black" if gamestate.player_toMove == "w" else "White"
        end_game = f"Checkmate: {winner} wins."
    
    elif gamestate.staleMate:
        end_game = "Stalemate."

    width, height = WIDTH / 2 - 200, HEIGHT / 2 - 10
    color = (0, 0, 0)
    
    end_game_label = font.render(end_game, True, color)
    screen.blit(end_game_label, (width, height))

    restart_label = font.render("Press 'r' to restart...", True, color)
    screen.blit(restart_label, (width + 40, height + end_game_label.get_height() + 10))


def drawGame(screen, gamestate, sqClicked):
    drawBoard(screen)
    addCoords(screen)
    drawPieces(screen, gamestate)
    # Paint square selected, make circles for the possible moves if click, and highlight last move
    highlight_moves(screen, gamestate, sqClicked)
    moves_panel(screen, gamestate)

    if gamestate.gameOver:
        end_game(screen, gamestate)

    pg.display.flip()


# Animate Move
#This function redraws the board to make the animation
def animateMove(screen, move, gamestate, clock, FPS):

    board = gamestate.fake_FEN.split("/")
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    framesPerSquare = 3 # frames to move one square
    frameCount = (abs(deltaRow) + abs(deltaCol)) * framesPerSquare  # total animation

    for frame in range(frameCount ):
        row, col = ((move.startRow + deltaRow * frame / frameCount,
                     move.startCol + deltaCol * frame / frameCount))
        drawBoard(screen)
        drawPieces(screen, gamestate)
        # erase piece already moved
        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = pg.Rect(move.endCol * CELL_SIZE, move.endRow * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pg.draw.rect(screen, color, endSquare)
        addCoords(screen)        

        # draw captured piece onto rectangle so it doesn't disappear
        if move.pieceCaptured != "1":
            piece_capturedImage = conversionFENotation(move.pieceCaptured)
            screen.blit(IMAGES[piece_capturedImage], rectImage(move.endCol, move.endRow))
        # draw moving piece
        piece_movedImage = conversionFENotation(move.pieceMoved)
        screen.blit(IMAGES[piece_movedImage], rectImage(col, row))
        clock.tick(FPS)
        pg.display.flip()

# Highlight clicked square and possible moves
def highlight_moves(screen, gamestate, sqClicked):

    if sqClicked != ():
        piece = gamestate.fake_FEN.split("/")[sqClicked[0]][sqClicked[1]]
        to_move = gamestate.player_toMove
        # If click and square not empty and same color as current player
        if (not piece.isdigit() and
                ((piece.islower() and to_move == "b") or
                 (piece.isupper() and to_move == "w"))):

            selectedSquare = pg.Surface((CELL_SIZE, CELL_SIZE))
            selectedSquare.set_alpha(120)
            selectedSquare.fill((150, 0, 0))
            screen.blit(selectedSquare, (sqClicked[1] * CELL_SIZE, sqClicked[0] * CELL_SIZE))

            possibleMoves = []
            for move in gamestate.validMoves:
                if (move.startRow, move.startCol) == (sqClicked[0], sqClicked[1]):
                    pg.draw.circle(screen, "green", 
                        (move.endCol * CELL_SIZE + CELL_SIZE / 2, move.endRow * CELL_SIZE + CELL_SIZE / 2), 10)

    #Highlight last piece moved
    #no highlight if just the cpus are playing. EPILEPSY
    if len(gamestate.history_Moves) > 0 and not gamestate.gameOver:
        startRow, startCol = gamestate.history_Moves[-1].startRow, gamestate.history_Moves[-1].startCol
        row, col = gamestate.history_Moves[-1].endRow, gamestate.history_Moves[-1].endCol
        start_square_color = (startRow + startCol) % 2
        square_color = (row + col) % 2
        if square_color == 1:
            alpha = 180
        else:
            alpha = 150
        
        if start_square_color == 1:
            start_alpha = 180
        else:
            start_alpha = 150

        color = (164, 170, 50)

        lastMove_square = pg.Surface((CELL_SIZE, CELL_SIZE))
        lastMove_square.set_alpha(alpha)
        lastMove_square.fill(color)
        
        screen.blit(lastMove_square, (col * CELL_SIZE, row * CELL_SIZE))

        lastMove_startSquare = pg.Surface((CELL_SIZE, CELL_SIZE))
        lastMove_startSquare.set_alpha(start_alpha)
        lastMove_startSquare.fill((164, 170, 50))
        
        screen.blit(lastMove_startSquare, (startCol * CELL_SIZE, startRow * CELL_SIZE))
    

def addCoords(screen):

    for y in range(DIMENSION):
        for x in range(DIMENSION):
            font = pg.font.SysFont('Times new roman', 18)  # coordenadas

            sq_Coords = str(coordX[x]) + str(coordY[y])

            # Just at the edges
            if str(coordX[x]) == 'a' or str(coordY[y]) == '1':
                screen.blit(font.render(str(sq_Coords).upper(), True, 'black'),
                            (x*CELL_SIZE, y*CELL_SIZE))  # Añade coordenadas

def drawPieces(screen, gamestate):

    board_lines = gamestate.fake_FEN.split(" ")[0].split("/")

    
    fen_Final_oct = board_lines[len(board_lines) - 1].split(" ")
    del board_lines[-1]
    board_lines.append(fen_Final_oct[0])

    for y in range(DIMENSION):
        for x in range(DIMENSION):

            row = []
            # Por cada caracter en la notación FEN en la seccion y
            for piece in board_lines[y]:

                if not piece.isdigit():
                    image_pieceName = conversionFENotation(piece)

                    if board_lines[y].count(piece) > 1:
                        row.append(piece)
                        new_index = row.index(piece)
                        new_piece = piece + str(new_index)
                        del row[-1]

                        row.append(new_piece)
                        positionX_piece = row.index(new_piece)
                   # poistionX es en relación a la notación fen entregada
                    else:
                        row.append(piece)
                        positionX_piece = row.index(piece)

                    if positionX_piece == x:
                        # if columna coincide con x se pone la pieza
                        screen.blit(IMAGES[image_pieceName], rectImage(x, y))

                else:  # Osea que el carácter en la notación FEN es un dígito
                    for i in range(int(piece)):
                        # Esto sirve para rellenar los espacios vacios y así poder poner las piezas según su index en row[]
                        row.append(1)

            row = []

def drawBoard(screen):
    
    for y in range(DIMENSION):
        for x in range(DIMENSION):
            color = COLORS[((x+y) % 2)]
            rect = (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Dibuja cada cuadrado de un color distinto
            pg.draw.rect(screen, color, rect)

def conversionFENotation(piece):

    pieces2FEN = {
        "r": "br",
        "n": "bn",
        "b": "bb",
        "q": "bq",
        "k": "bk",
        "p": "bp",

        "P": "wp",
        "R": "wr",
        "N": "wn",
        "B": "wb",
        "K": "wk",
        "Q": "wq",

    }

    return pieces2FEN[piece]
