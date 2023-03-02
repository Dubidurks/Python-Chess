import random

pieceScore = {
    "k" : 0,
    "q" : 15,
    "r" : 5,
    "b" : 3,
    "n" : 3,
    "p" : 1,
}


knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1],
    ]
#Maybe better position on open files
rookScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4],
    ]

whitePawnScores = [
    [10, 10, 10, 10, 10, 10, 10, 10],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    ]
blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [10, 10, 10, 10, 10, 10, 10, 10],
    ]

piecePositionScores = {"N": knightScores, "Q": queenScores, "R": rookScores, "B": bishopScores, "p": blackPawnScores, "P": whitePawnScores}

CHECKMATE = 1000
STALEMATE = 0
MAX_DEPTH = 3

def random_move(validMoves):
    random.shuffle(validMoves)
    return random.choice(validMoves)

def greedy_algorithm(gamestate):
    #White will be positive on the score, and black will be negative
    #White Checkmate = 1000, Black checkmate = -1000

    turn_multiplier = 1 if gamestate.player_toMove == "w" else -1

    #Calculate the score of pieces.
    maxScore = -CHECKMATE
    bestMove = None

    validMoves = gamestate.validMoves
    random.shuffle(validMoves)   
    for playerMove in validMoves:
        gamestate.update(gamestate.makeMove(playerMove), ai=True)
        score = score_material(gamestate)  * turn_multiplier
        
        if score > maxScore:
            maxScore = score
            bestMove = playerMove
        
        gamestate.undoMove()
    
    return bestMove

#No recursion, two moves ahead (1 turn)
def simple_minmax_algorithm(gamestate):
    
    #White will be positive on the score, and black will be negative
        #White Checkmate = 1000, Black checkmate = -1000
    turn_multiplier = 1 if gamestate.player_toMove == "w" else -1

    opponentMinMaxScore = CHECKMATE * -turn_multiplier
    bestPlayerMove = None

    for playerMove in gamestate.validMoves:
        new_fen = gamestate.makeMove(playerMove)
        gamestate.update(new_fen, ai=True)

        if gamestate.staleMate:
            opponentMaxScore = STALEMATE
        
        elif gamestate.checkMate:
            opponentMaxScore = CHECKMATE * turn_multiplier
        
        else:
            opponentMaxScore = CHECKMATE * turn_multiplier
            for opponentMove in gamestate.validMoves:
                new_fen = gamestate.makeMove(opponentMove)
                gamestate.update(new_fen, ai=True)
                
                    #Since is for the opponent, multiply -1 the turn multiplier
                score = score_material(gamestate) * -turn_multiplier
                if score > opponentMaxScore:
                    opponentMaxScore = score
                
                gamestate.undoMove()

        #Minimize score of the opponent
        #(get the move with the max score for the opponent for each of my moves)
        #(return my best move that minimize the maximum possible score of my opponent)
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gamestate.undoMove()
    
    return bestPlayerMove


#ismaximizing is a bool of the player, black tries to minimize, white tries to maximize the score
def minmax_algorithm(gamestate, depth, isMaximizing):
    global nextMove
    turn_multiplier = 1 if isMaximizing else -1

    #First terminal node
    if depth == 0:
        return score_board(gamestate)
    
    validMoves = gamestate.validMoves
    random.shuffle(validMoves)
    if isMaximizing:
        maxScore = -CHECKMATE
        for move in validMoves:
            gamestate.update(gamestate.makeMove(move), ai=True)
            score = minmax_algorithm(gamestate, depth - 1, False)
            if maxScore < score:
                maxScore = score

                if depth == MAX_DEPTH:
                    nextMove = move
            
            gamestate.undoMove()
        
        return maxScore
    
    else:
        #Min score for black is max score of the board
        minScore = CHECKMATE
        for move in validMoves:
            gamestate.update(gamestate.makeMove(move), ai=True)
            score = minmax_algorithm(gamestate, depth - 1, True)
            
            if score < minScore:
                minScore = score

                if depth == MAX_DEPTH:
                    nextMove = move
            
            gamestate.undoMove()
        
        return minScore

#NegaMax is the same as minmax but better writen
def negamax_algorithm(gamestate, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    
    if depth == 0:
        return score_board(gamestate) * turnMultiplier

    validMoves = gamestate.getValidMoves()
    random.shuffle(validMoves)
    maxScore = -CHECKMATE
    #For opponnent
    
    for move in validMoves:
        gamestate.update(gamestate.makeMove(move), ai=True)
        score = -negamax_algorithm(gamestate, depth - 1, -turnMultiplier)
        gamestate.undoMove()

        if maxScore < score:
            maxScore = score

            if depth == MAX_DEPTH:
                nextMove = move

    return maxScore

#First call from init
def findBestMove(gamestate):
    global nextMove, counter
    #To see how many times the method is called
    counter = 0
    nextMove = None


    #isMaximizing = True if gamestate.player_toMove == "w" else False
    #minmax_algorithm(gamestate, MAX_DEPTH, isMaximizing)
    
    isMaximizing = 1 if gamestate.player_toMove == "w" else -1
    #negamax_algorithm(gamestate, MAX_DEPTH, isMaximizing)
    
    #Negamax with alpha beta prunning
    #alpha = current max score (so we start at minimum score), beta = current min score (so we start at the top score)
    negamax_algorithm_ab(gamestate, MAX_DEPTH, isMaximizing, -CHECKMATE, CHECKMATE)
    print(counter)

    return nextMove


#Negamax with alpha beta prunning
def negamax_algorithm_ab(gamestate, depth, turnMultiplier, alpha, beta):
    global nextMove, counter
    counter += 1

    if depth == 0:
        return score_board(gamestate) * turnMultiplier

    validMoves = gamestate.getValidMoves()
    random.shuffle(validMoves)
    #Alpha beta could go more efficient if order moves by score
    maxScore = -CHECKMATE
    #For opponnent's moves
    for move in validMoves:
        gamestate.update(gamestate.makeMove(move), ai=True)
        score = -negamax_algorithm_ab(gamestate, depth - 1, -turnMultiplier, -beta, -alpha)
        gamestate.undoMove()

        if maxScore < score:
            maxScore = score

            if depth == MAX_DEPTH:
                nextMove = move
                print(move, score)
        
        #Prunning
        if alpha < maxScore:
            alpha = maxScore
        
        if beta <= alpha:
            break

    return maxScore

'''
Positive score is good for white, negative score means black is winning
'''
def score_board(gamestate):
    winner_multiplier = -1 if gamestate.player_toMove == "w" else 1

    if gamestate.checkMate:
        return CHECKMATE * winner_multiplier
    
    elif gamestate.staleMate:
        return STALEMATE #Draw
    
    board = gamestate.fake_FEN.split(" ")[0].split("/")[0:8]

    score = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != "1":

                #Score by position of the piece
                piecePositionScore = 0
                #No table for king, avoid errors
                if piece.lower() != "k": 
                    #If pawn need a diferentiate set of keys for the dict for black/pawn
                    if piece.upper() == "P":
                        dict_key = piece
                    else:
                        dict_key = piece.upper()

                    piecePositionScore = piecePositionScores[dict_key][row][col]

                #Black wants to get the score down, white wants to make it higher
                if piece.isupper():
                    score += (pieceScore[piece.lower()] + piecePositionScore * .1)
                elif piece.islower():
                    score -= (pieceScore[piece.lower()] + piecePositionScore * .1)
                
    return score

def score_material(gamestate):

    board = gamestate.fake_FEN.split(" ")[0].split("/")[0:8]
    
    
    score = 0
    if gamestate.checkMate:
        score = CHECKMATE 
    elif gamestate.staleMate:
        score = STALEMATE
    else:   
    
        for x in range(len(board)):
            for y in range(len(board[x])):
                piece = board[x][y]
                if piece != "1":
                    piece_score = pieceScore[piece.lower()]

                    #Black wants to get the score down, white wants to make it higher
                    if piece.isupper():
                        score += piece_score
                    elif piece.islower():
                        score -= piece_score


    return score 