coordY = (8, 7, 6, 5, 4, 3, 2, 1)
coordX = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')


class PieceMoves():

    # Get all pawn moves for a certain square and add them to the moves list

    def getPawnMoves(self, row, col, moves):
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]

        en_passant = self.fake_FEN.split(" ")[3]

        # If exists en_passant
        if en_passant != "-":
            # Need to convert from chees notation to the one i use (flip the values)
            en_passantRow = coordY.index(int(en_passant[::-1][0]))
            en_passantCol = coordX.index(en_passant[::-1][1])

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if 0 <= row < 8 and 0 <= col < 8:
            # White to move
            if self.player_toMove == "w":

                # If 1 square ahead is empty, add that to the possible moves
                if row - 1 >= 0:
                    if splited_Board[row - 1][col] == "1":
                        if not piecePinned or pinDirection == (-1, 0):
                            moves.append(
                                Move((row, col), (row - 1, col), self.fake_FEN))

                        # Two squares ahead
                        if row == 6 and splited_Board[row - 2][col] == "1" and (not piecePinned or pinDirection == (-1, 0)):
                            moves.append(
                                Move((row, col), (row - 2, col), self.fake_FEN))

                # Dont capture if offboard to the left
                if col - 1 >= 0:
                    # If piece is black, capture
                    if row - 1 >= 0 and col - 1 >= 0:
                        if splited_Board[row - 1][col - 1].islower():
                            if not piecePinned or pinDirection == (-1, -1):
                                moves.append(
                                    Move((row, col), (row - 1, col - 1), self.fake_FEN))

                # Dont capture if offboard to the right
                if col + 1 < len(splited_Board[row]):
                    if row - 1 >= 0 and col + 1 < len(splited_Board[row - 1]):
                        if splited_Board[row - 1][col + 1].islower():
                            if not piecePinned or pinDirection == (-1, 1):
                                moves.append(Move((row, col), (row - 1, col + 1), self.fake_FEN))

                # Add move if can capture en_passant
                if en_passant != "-":
                    if row - 1 == en_passantRow:
                        # If can capture en_passant and piece to the side is enemy
                        if (col + 1 == en_passantCol and splited_Board[row][col + 1].islower()):
                            # Pawn to capture if en_passant move
                            pawn = (row - 1, col + 1)
                            moves.append(Move((row, col), (row - 1, col + 1), self.fake_FEN, passant=pawn))
                        elif (col - 1 == en_passantCol and splited_Board[row][col - 1].islower()):
                            pawn = (row - 1, col - 1)
                            moves.append(Move((row, col), (row - 1, col - 1), self.fake_FEN, passant=pawn))

        ########### Black to move#######################################
            if self.player_toMove == "b":
                # If 1 square ahead is empty, add that to the possible moves
                if row + 1 < len(splited_Board):
                    if splited_Board[row + 1][col] == "1":
                        if not piecePinned or pinDirection == (1, 0):
                            moves.append(Move((row, col), (row + 1, col), self.fake_FEN))

                        # Two squares ahead
                        if row == 1 and splited_Board[row + 2][col] == "1" and (not piecePinned or pinDirection == (1, 0)):
                            moves.append(Move((row, col), (row + 2, col), self.fake_FEN))

                # Dont capture if offboard to the left
                if col - 1 >= 0:
                    # If piece is black, capture
                    if row + 1 < len(splited_Board) and col - 1 >= 0:
                        if splited_Board[row + 1][col - 1].isupper():
                            if not piecePinned or pinDirection == (1, -1):
                                moves.append(Move((row, col), (row + 1, col - 1), self.fake_FEN))

                # Dont capture if offboard to the right
                if col + 1 < len(splited_Board[row]):
                    if row + 1 < len(splited_Board) and col + 1 < len(splited_Board[row + 1]):
                        if splited_Board[row + 1][col + 1].isupper():
                            if not piecePinned or pinDirection == (1, 1):
                                moves.append(
                                    Move((row, col), (row + 1, col + 1), self.fake_FEN))

                # Add move if can capture en_passant
                if en_passant != "-":
                    if row + 1 == en_passantRow:
                        # If can capture en_passant and piece to the side is enemy
                        if (col + 1 == en_passantCol and splited_Board[row][col + 1].isupper()):
                            # Pawn to capture if en_passant
                            pawn = (row + 1, col + 1)
                            moves.append(Move((row, col), (row + 1, col + 1), self.fake_FEN, passant=pawn))
                        elif (col - 1 == en_passantCol and splited_Board[row][col - 1].isupper()):
                            pawn = (row + 1, col - 1)
                            moves.append(Move((row, col), (row + 1, col - 1), self.fake_FEN, passant=pawn))

# Get all rook moves for a certain square and add them to the moves list

    def getRookMoves(self, row, col, moves):

        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])

                # Cant remove queen from pin on rook moves, only remove it on bishop moves
                if splited_Board[row][col].upper() != "Q":
                    self.pins.remove(self.pins[i])
                break

        moveDirections = ((-1, 0), (0, -1), (1, 0), (0, 1))

        for move in moveDirections:
            for squares in range(1, 8):
                endRow = row + move[0] * squares
                endCol = col + move[1] * squares

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    next_SquareOnFEN = splited_Board[endRow][endCol]
                    if not piecePinned or pinDirection == move or pinDirection == (-move[0], -move[1]):
                        if next_SquareOnFEN == "1":
                            moves.append(Move((row, col), (endRow, endCol), self.fake_FEN))

                        elif (self.player_toMove == "w" and next_SquareOnFEN.islower()) or \
                            (self.player_toMove == "b" and next_SquareOnFEN.isupper()):

                            moves.append(Move((row, col), (endRow, endCol), self.fake_FEN))
                            break
                        # Friendly piece
                        else:
                            break
                # off board
                else:
                    break


# Get all bishop moves for a certain square and add them to the moves list


    def getBishopMoves(self, row, col, moves):

        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        moveDirections = ((-1, -1), (1, -1), (-1, 1), (1, 1))

        for move in moveDirections:
            for squares in range(1, 8):
                endRow = row + move[0] * squares
                endCol = col + move[1] * squares

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == move or pinDirection == (-move[0], -move[1]):
                        endPiece = splited_Board[endRow][endCol]

                        if endPiece == "1":
                            moves.append(
                                Move((row, col), (endRow, endCol), self.fake_FEN))

                        elif (self.player_toMove == "w" and endPiece.islower()) or (self.player_toMove == "b" and endPiece.isupper()):
                            moves.append(Move((row, col), (endRow, endCol), self.fake_FEN))
                            break
                        else:
                            break
                # off board
                else:
                    break

# Get all Knight moves for a certain square and add them to the moves list

    def getKnightMoves(self, row, col, moves):
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]

        piecePinned = False

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        moveDirections = ((-2, 1), (-2, -1), (1, 2), (-1, 2),
                          (1, -2), (-1, -2), (2, 1), (2, -1))

        for move in moveDirections:

            endRow = row + move[0]
            endCol = col + move[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = splited_Board[endRow][endCol]

                    # Enemy piece or empty space
                    if (self.player_toMove == "w" and (endPiece.islower() or endPiece == "1")) or \
                        (self.player_toMove == "b" and (endPiece.isupper() or endPiece == "1")):
                        moves.append(
                            Move((row, col), (endRow, endCol), self.fake_FEN))


# Get all queen moves for a certain square and add them to the moves list


    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

# Get all king moves for a certain square and add them to the moves list

    def getKingMoves(self, row, col, moves):
        splited_Board = self.fake_FEN.split(" ")[0].split("/")[0: 8]

        moveDirections = [(-1, 0), (0, -1), (1, 0), (0, 1),
                          (-1, -1), (1, -1), (-1, 1), (1, 1)]

        castling = self.fake_FEN.split(" ")[2]

        if castling != "-":
            # Need to check if no pieces in between
            for character in castling:
                if (self.player_toMove == "w" and character.isupper()) or (self.player_toMove == "b" and character.islower()):
                    player_king = self.whiteKingLocation if self.player_toMove == "w" else self.blackKingLocation
                    # King Side castling
                    if character.lower() == "k":
                        canCastle = True
                        #If no pieces in between or incheck currently
                        for i in range(1, 3):
                            (x, y) = (player_king[0], player_king[1] + i)

                            # Can't castle if in check
                            if (splited_Board[x][y] != "1") or self.inCheck:
                                canCastle = False
                                break

                        # If rock will be attacked when castle, can't
                        rock_end = (player_king[0], player_king[1] + 1)
                        inCheck, _, _ = self.checkForPinsAndChecks(checkSquare=rock_end)
                        if inCheck:
                            canCastle = False

                        if canCastle:
                            moveDirections.append((0, 2))

                    # Queen side castle
                    if character.lower() == "q":
                        canCastle = True
                        for i in range(1, 4):
                            (x, y) = (player_king[0], player_king[1] - i)

                            if (splited_Board[x][y] != "1") or self.inCheck:
                                canCastle = False
                                break

                        # If rock will be attacked when castle, can't
                        rock_end = (player_king[0], player_king[1] - 1)
                        inCheck, _, _ = self.checkForPinsAndChecks(checkSquare=rock_end)
                        if inCheck:
                            canCastle = False

                        if canCastle:
                            moveDirections.append((0, -2))

        for move in moveDirections:

            endRow = row + move[0]
            endCol = col + move[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = splited_Board[endRow][endCol]

                # Not an ally piece
                if (self.player_toMove == "w" and not endPiece.isupper()) or (self.player_toMove == "b" and not endPiece.islower()):

                    # if move -2 blocks (this moveDirection only appears if can castle queenSide)
                    if move[1] == -2:
                        moves.append(Move((row, col), (endRow, endCol), self.fake_FEN, castle="queen"))

                    # if move 2 blocks (this moveDirection only appears if can castle kingSide)
                    elif move[1] == 2:
                        moves.append(Move((row, col), (endRow, endCol), self.fake_FEN, castle="king"))

                    else:
                        moves.append(Move((row, col), (endRow, endCol), self.fake_FEN))


class Move():

    def __init__(self, initial_square, end_square, board, castle=None, passant=None):

        board = board.split(" ")[0].split("/")
        self.startRow = initial_square[0]
        self.startCol = initial_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.castle = castle
        self.en_passant = passant

        #This two values only convert to true if the move is made. By default always gonna be False
        #(I use it to display on the panel moves checks with '+' and checkmate '#')
        self.check = False
        self.checkMate = False

        # ID allows  to keep track of a certain move determined by the squares
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol

    # Override equals method #Is used for comparing objects
    # This is useful for looking if a  certain move is in the list of valid moves
    def __eq__(self, other):
        # if other is instance of Move
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):

        pieceMoved = "" if self.pieceMoved.lower() == "p" else self.pieceMoved.upper()
        #if piece captured
        capturedPiece = "x" if self.pieceCaptured != "1" else ""
        endSquare = self.getRankFile(self.endCol, self.endRow)
        
        if self.castle == "queen":
            chessNotationMove = "O-O-O"
        elif self.castle == "king":
            chessNotationMove = "O-O"
        else:
            #if pawn captures
            if capturedPiece == "x" and pieceMoved == "":
                pieceMoved = self.getRankFile(self.startCol, self.startRow)[0]

            chessNotationMove = f"{pieceMoved}{capturedPiece}{endSquare}"

            #This values only will be true if the game is updated, by default none move has value of checkmate or check = True
            if not self.checkMate and self.check:
                chessNotationMove += "+"
            elif self.checkMate:
                chessNotationMove += "#"

        return chessNotationMove
        #return self.getRankFile(self.startCol, self.startRow) + self.getRankFile(self.endCol, self.endRow)

    def getRankFile(self, row, col):

        return str(coordX[row]) + str(coordY[col])
