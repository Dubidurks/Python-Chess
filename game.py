#!/usr/bin/env python3
from moves import PieceMoves, coordX, coordY

# Still need to add:
# 1. Add way to select Pawn Promotion in gui
# 2. Stalemate logic for more than 50 moves or insufficient material
#Fix
# 1. Castle rights doesn't work if start position has rocks in different columns. The same would happen if kings start on different columns
#    Need to differentiate between queenside and kingside castle for black and white separately. 
#    rock king col and rock queen col must be different for white and black
# 2. Some positions are falselly read as being in check, such as 
        #self.current_FEN = "1r1k3r/2p5/8/3P4/4pp2/8/3P4/R3K2R b KQ -"


class GameState(PieceMoves):
    def __init__(self):
        self.current_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        #self.current_FEN = "r3k2r/pppp2p1/8/8/8/8/1PPP4/R3K2R b KQq -"

        # fake_FEN sirve para reemplazar los números originales de la fen por tantos 1 como número aparezca
        # (debido a que un 3 significaría 3 epacios vacios (o 1's) por ejemplo)
        self.fake_FEN = ""
        self.player_toMove = ""

        self.inCheck = False
        self.pins = []
        self.checks = []

        self.gameOver = False
        self.checkMate = False
        self.staleMate = False

        self.validMoves = []
        # So i dont call every function per piece
        self.moveFunctions = {'p': self.getPawnMoves, 'b': self.getBishopMoves, 'r': self.getRookMoves,
                              'k': self.getKingMoves, 'q': self.getQueenMoves, 'n': self.getKnightMoves}

        #Game History (Moves and gamestate with FEN notation)
        self.history_Moves = []
        self.history_Boards = []

        # Setting some values for initial king location
        self.whiteKingLocation = (0, 0)
        self.blackKingLocation = (0, 0)

        # Make the first update before the castling stuff (it needs the king column and fake_fen)
        self.update(self.current_FEN)

        # --------------------Castling Stuff----------------
        self.kingSide_rockCol = 7
        self.queenSide_rockCol = 0
        # -------------------------------------------------

    def update(self, new_fen, undoing=False, ai=False):
        
        self.current_FEN = new_fen
        self.player_toMove = self.current_FEN.split(" ")[1]

        # Sometimes the FEN notation gets bugged and the player is added on the first part of the FEN
        # This conditional realigns it
        splited_fen = self.faked_FEN(new_fen).split(" ")
        fen_board = splited_fen[0].split("/")
        if len(fen_board) > 8:
            
            board = "/".join(fen_board[0:8])
            to_play = fen_board[-1]
            castle = splited_fen[1]
            passant = splited_fen[2]

            self.fake_FEN = f"{board} {to_play} {castle} {passant}"

        else:
            self.fake_FEN = " ".join(splited_fen)

        # ---------------------------------------------------------------
        # Update Valid Moves
        self.validMoves = self.getValidMoves()

        # This is to avoid append new board when undoing, since it's the last
        if not undoing:
            self.history_Boards.append(new_fen)

        # Updating values for kings location
        splited_fen = self.fake_FEN.split(" ")[0].split("/")
        for x, row in enumerate(splited_fen):
            for y, square in enumerate(splited_fen[x]):
                if splited_fen[x][y] == "K":
                    self.whiteKingLocation = (x, y)

                elif splited_fen[x][y] == "k":
                    self.blackKingLocation = (x, y)

        #Last move must be registered as making a check (for the displaying moves panel) if inCheck
        if self.inCheck:
            self.history_Moves[-1].check = True

        if len(self.validMoves) == 0:
            #Checkmate
            if self.inCheck:
                self.checkMate = True
                self.history_Moves[-1].checkMate = True
            
                #Stalemate
            else:        
                self.staleMate = True

        #If not doing ai recurssion
        if not ai and (self.checkMate or self.staleMate):
            self.gameOver = True
        
    def faked_FEN(self, rial_fen):
        # For a fen that can be interpreted bya index (with 1's instead of raw numbers)
        fake_FEN = ""
        FEN_notation_Splitted = rial_fen.split(" ")[0].split("/")[0:8]
        castling = rial_fen.split(" ")[2]
        en_passant = rial_fen.split(" ")[3]

        # lastPiece_FENotation = fake_FEN.split(" ")[1]
        # Need to transform fen notation to exchange numbers per random numbers
        for row_FEN in FEN_notation_Splitted:
            for character in row_FEN:
                if character.isdigit():  # reemplaza los números por 1
                    index_character = row_FEN.index(character)
                    for i in range(int(character)):
                        fake_FEN += "1"
                else:
                    fake_FEN += character

            # Añadir espacio vacio pa la siguiente parte de la notacion
            if FEN_notation_Splitted.index(row_FEN) == len(FEN_notation_Splitted) - 1:
                fake_FEN += " "
            else:
                fake_FEN += "/"

        # add player to move
        fake_FEN += self.player_toMove

        # add castling
        fake_FEN += " "
        fake_FEN += castling

        # add en passant
        fake_FEN += " "
        fake_FEN += en_passant

        return fake_FEN

    # Returns a FEN with the move made
    def makeMove(self, move):
        fake_fen = self.fake_FEN
        currentBoard_Splited = fake_fen.split(" ")[0].split("/")
        castling = fake_fen.split(" ")[2]
        en_passant = fake_fen.split(" ")[3]

        # Need to remove it from fen if it's for more that 2 moves
        if len(self.history_Boards) > 1 and en_passant != "-":
            if fake_fen.split(" ")[3] == (self.history_Boards[-2].split(" ")[3]):
                en_passant = "-"

        # Convierte el octeto en lista para poder reemplazar el "bit correcto"
        list_ofCharacters = list(currentBoard_Splited[move.startRow])

        # Esta variable servirá para crear los nuevos octetos que modificarán el original
        new_octeto = list_ofCharacters[:]  # make a copy of the list
        new_octeto[move.startCol] = "1"

        # Reforma el octeto relacionado con el cuadro de comienzo (desde donde mueves la pieza y debes dejar vacio (un numero))
        currentBoard_Splited[move.startRow] = "".join(new_octeto)

        # Llena el espacio hacia donde va la pieza con la pieza movida
        # Convierte el octeto indicado por end square[0] en lista para poder reemplazar el "bit correcto"
        list_ofCharacters = list(currentBoard_Splited[int(move.endRow)])

        # transforma el "bit" del octeto indicado por end_square[1] en la pieza tomada
        list_ofCharacters[move.endCol] = move.pieceMoved
        new_octeto = list_ofCharacters

        # Reforma el octeto relacionado con el cuadro de termino (a donde mueves la pieza y debes dejar la pieza)
        currentBoard_Splited[move.endRow] = "".join(new_octeto)

        currentBoard = "/".join(currentBoard_Splited)
        self.history_Moves.append(move)

        # Change Players
        currentBoard += " "
        currentBoard += "b" if self.player_toMove == "w" else "w"

        # --------------- CASTLING LOGIC BOARD----------------------
        if move.castle != None:
            # black
            if move.pieceMoved == 'k':
                row = list(currentBoard_Splited[self.blackKingLocation[0]])
                rock = "r"
                king_row = self.blackKingLocation[0]

                # white
            elif move.pieceMoved == 'K':
                row = list(currentBoard_Splited[self.whiteKingLocation[0]])
                rock = "R"
                king_row = self.whiteKingLocation[0]

            # Castling kingside
            if move.castle == "king":
                # move rock
                row[self.kingSide_rockCol] = "1"
                row[move.endCol - 1] = rock
                currentBoard_Splited[king_row] = "".join(
                    row)
            # Castling queenside
            elif move.castle == "queen":
                row[self.queenSide_rockCol] = "1"
                row[move.endCol + 1] = rock
                currentBoard_Splited[king_row] = "".join(
                    row)
        # ------------------------------------------------------------------------------------

        # ------------------Modify FEN castling part if rock and king movements---------------
        if castling != "-":
            check_character = ""

            if move.pieceMoved == "K":
                # Remove castling from fen if white king move
                for character in castling:
                    if character.isupper():
                        castling = castling.replace(character, "")
            elif move.pieceMoved == "k":
                # Remove castling from fen if black king move
                for character in castling:
                    if character.islower():
                        castling = castling.replace(character, "")

                # If move a rock
            elif move.pieceMoved.lower() == "r":
                if move.startCol == self.kingSide_rockCol:
                    check_character = "k"
                elif move.startCol == self.queenSide_rockCol:
                    check_character = "q"

                for character in castling:
                    if move.pieceMoved.islower():
                        toCheck = character.islower()
                    elif move.pieceMoved.isupper():
                        toCheck = character.isupper()

                    # Replace the character on the FEN's castle string
                    if toCheck and character.lower() == check_character:
                        castling = castling.replace(character, "")

            # Capturing Rocks
            if move.pieceCaptured.lower() == "r":
                if move.endCol == self.kingSide_rockCol:
                    check_character = "k"
                elif move.endCol == self.queenSide_rockCol:
                    check_character = "q"

                for character in castling:
                    if move.pieceCaptured.islower():
                        toCheck = character.islower()

                    elif move.pieceCaptured.isupper():
                        toCheck = character.isupper()

                    if toCheck and character.lower() == check_character:
                        castling = castling.replace(character, "")

        # If castling empty
        if castling == "":
            castling = "-"

        # ------------------------Pawn Promotion --------------------------
        current_board = currentBoard_Splited

        to_play = currentBoard.split(' ')[1]
        default_promotion = "q"
        promotion = ""
        white_topRank = 0
        black_topRank = 7

        # Keep track when a pawn gets to the back rank (it would be different for black and white)
        if self.player_toMove == "w" and "P" in current_board[white_topRank]:
            check = white_topRank
            pawn = "P"
            promotion = default_promotion.upper()

        elif self.player_toMove == "b" and "p" in current_board[black_topRank]:
            check = black_topRank
            pawn = "p"
            promotion = default_promotion.lower()

        # If pawn promotes
        if promotion != "":
            current_board[check] = current_board[check].replace(
                pawn, promotion)
            # Change currentBoard if necessary
            currentBoard_Splited = current_board
        # ---------------------------------------------------------------------
        # ---------------------------En Passant FEN--------------------------------
            # Create en_passant in the FEN notation with the variable en_passant if needed (if a pawn move two squares)
        if move.pieceMoved.lower() == "p" and abs(move.endRow - move.startRow) == 2:
            passant_col = move.startCol
            # Black
            if move.pieceMoved.islower():
                passant_row = move.startRow + 1
            # White
            else:
                passant_row = move.startRow - 1
            # To get this chess notation, i need to flip columns and rows. Later on i need to transform this chess notation
            en_passant = str(coordX[passant_col]) + str(coordY[passant_row])
        # ---------------------------En Passant Board--------------------------------
        # If the move made is en_passant
        if move.en_passant != None:
            en_passantRow = move.en_passant[0]
            en_passantCol = move.en_passant[1]

            if self.player_toMove == "b":
                pawn_row = -1
            else:
                pawn_row = 1

            # If go to the passant square being a pawn
            if ((move.endRow, move.endCol) == (en_passantRow, en_passantCol) and move.pieceMoved.upper() == "P"):
                row = list(currentBoard_Splited[en_passantRow + pawn_row])
                row[en_passantCol] = "1"
                currentBoard_Splited[en_passantRow + pawn_row] = "".join(row)
                en_passant = "-"

        if en_passant == "":
            en_passant == "-"

        # ---------------------------------------------------------------------

        new_fen = "/".join(currentBoard_Splited)
        new_fen += f" {to_play}"
        new_fen += f" {castling}"
        new_fen += f" {en_passant}"

        return new_fen

    def undoMove(self):

        prev_board = self.history_Boards[-2]
        self.history_Boards.pop()

        move = self.history_Moves.pop()
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0:8]

        # Relocate the king if needed
        if splited_Board[move.endRow][move.endCol] == 'k':
            self.blackKingLocation = (move.startRow, move.startCol)

        if splited_Board[move.endRow][move.endCol] == 'K':
            self.whiteKingLocation = (move.startRow, move.startCol)


        self.checkMate = False    
        self.staleMate = False

        
        self.update(prev_board, undoing=True)

    def getValidMoves(self):
        moves = []
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0:8]
        # This shit doesnt work right, it returns check when there is none
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.player_toMove == "w":
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        if self.player_toMove == "b":
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            # Only 1 check. Block check or move the king
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # To block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # Enemy piece causing check and standarized to avoid make if for lowercasse and if for uppercasse
                pieceChecking = splited_Board[checkRow][checkCol].upper()
                # Squares that pieces can move to
                validSquares = []
                # IF knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # Check2 and check3 are checkdirections
                        validSquare = (
                            kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)

                        # Once you get to piece end check
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                # Get rid of any moves that dont block check or move king
                # Go through backwards when you are removing items from a list as iterating
                for i in range(len(moves) - 1, -1, -1):
                    # Move doesnt move the king so it must block or capture
                    # Piece standarized to avoid making for K and k
                    if moves[i].pieceMoved.upper() != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])

                    # If the move leaves the king in check, remove it
                    elif moves[i].pieceMoved.upper() == "K":
                        inCheck = False
                        checkSquare = (moves[i].endRow,
                                       moves[i].endCol)
                        inCheck, _, _ = self.checkForPinsAndChecks(
                            checkSquare=checkSquare)
                        if inCheck:
                            moves.remove(moves[i])
            # Double check, king has to move
            else:
                moves = self.getAllPossibleMoves()
                # Want to remove movements from the king that leaves him in check
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved.upper() == "K":
                        inCheck = False
                        checkSquare = (moves[i].endRow,
                                       moves[i].endCol)
                        inCheck, _, _ = self.checkForPinsAndChecks(
                            checkSquare=checkSquare)
                        if inCheck:
                            moves.remove(moves[i])
                    # Since it's double check, i can remove anything that doesn't move the king
                    else:
                        moves.remove(moves[i])

        # Not in check so all moves are fine except those that leave you in check
        else:
            moves = self.getAllPossibleMoves()
            # Want to remove movements from the king that leaves him in check
            for i in range(len(moves) - 1, -1, -1):
                if moves[i].pieceMoved.upper() == "K":
                    inCheck = False
                    checkSquare = (moves[i].endRow,
                                   moves[i].endCol)
                    inCheck, _, _ = self.checkForPinsAndChecks(
                        checkSquare=checkSquare)
                    if inCheck:
                        moves.remove(moves[i])

        return moves

    def getAllPossibleMoves(self):
        moves = []
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]
        for row in range(len(splited_Board)):
            for col in range(len(splited_Board[row])):
                piece = splited_Board[row][col]
                # Check if the piece to move corresponds to the player to play
                # and use moveFunctions dictionary to replace the piece for the corresponding funct
                if (self.player_toMove == "w" and piece.isupper()) or (self.player_toMove == "b" and piece.islower()):
                    # piece in the dictionary are lowercasse
                    piece = piece.lower()
                    self.moveFunctions[piece](row, col, moves)

        return moves

    # Checksquare allows me to check if a particular square is being attacked (taking in consideration current player_toMove)
    # So i can remove movements that leaves the king in check from the valid moves
    def checkForPinsAndChecks(self, checkSquare=None):

        pins = []
        checks = []
        inCheck = False
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]
        # Should change the splited board based on checksquare?

        if self.player_toMove == "w":
            # Ally Pieces will be Upper
            # Enemy pieces will be lowerr
            colorOf_Piece = "w"
            enemyColor = "b"

            if checkSquare == None:
                startRow = self.whiteKingLocation[0]
                startCol = self.whiteKingLocation[1]
            else:
                startRow = checkSquare[0]
                startCol = checkSquare[1]

        else:
            # Ally Pieces will be Lower
            # Enemy pieces will be Upper
            colorOf_Piece = "b"
            enemyColor = "w"

            if checkSquare == None:
                startRow = self.blackKingLocation[0]
                startCol = self.blackKingLocation[1]
            else:
                startRow = checkSquare[0]
                startCol = checkSquare[1]

        # Check directions from king's perspective (or other square with checksquare parameter) for pins and checks
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j, direction in enumerate(directions):
            # Reset possiblePins
            possiblePin = ()
            for i in range(1, 8):
                end_row = startRow + direction[0]*i
                end_col = startCol + direction[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = splited_Board[end_row][end_col]
                    if end_piece.isdigit():
                        continue

                    # Allied Piece blocking (Pin piece)
                    # Can't be pinned if it's a king (need that for the checksquare. If not, when checking square, it will count the current king position as a pin that protects you from |)
                    # For AI development the "K" can be changed for a certain piece that has been moved
                    elif ((end_piece.isupper() and colorOf_Piece == "w" and end_piece != "K") or
                          (end_piece.islower() and colorOf_Piece == "b" and end_piece != "k")):
                        if possiblePin == ():
                            possiblePin = (end_row, end_col,
                                           direction[0], direction[1])
                        else:
                            break

                    # Enemy piece
                    elif (end_piece.isupper() and enemyColor == "w") or (end_piece.islower() and enemyColor == "b"):
                        piece_type = end_piece.lower()

                        # Different Rules for each type of piece. r, b, p, q, k
                        # j is the index for the directions. They're in order.
                        if ((0 <= j <= 3 and piece_type == "r") or  # rock
                            (4 <= j <= 7 and piece_type == "b") or  # bishop
                            # black pawn
                            (4 <= j <= 5 and end_piece == "p" and i == 1) or
                            # white pawn
                            (6 <= j <= 7 and end_piece == "P" and i == 1) or
                            (piece_type == "q") or  # queen
                                (piece_type == "k" and i == 1)):  # king

                            # If there's no piece in between (pinned)
                            if possiblePin == ():
                                inCheck = True
                                checks.append(
                                    (end_row, end_col, direction[0], direction[1]))
                                break
                            # Piece pinned
                            else:
                                pins.append(possiblePin)
                                break
                        # No enemy pieces applying checks
                        else:
                            break
                else:
                    # We have gone off the board
                    break

        # Check For Knight checks
        horsi_moveDirections = (
            (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in horsi_moveDirections:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = splited_Board[endRow][endCol]

                # If enemy piece and knight
                if ((enemyColor == "w" and endPiece.isupper()) or (enemyColor == "b" and endPiece.islower())) and endPiece.lower() == "n":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks
        
