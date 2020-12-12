import asyncio
import json
from random import randint
import sys
import websockets
    #El programa hace el movimiento que resulte en el mayor puntaje en este momento.
    #La estrategia es mover los reyes para acumular la mayor cantidad de puntos posible, y solo capturar
    #cuando el enemigo avance.
    #Las reinas usan un puntaje especial para priorizar comer una reina enemiga antes que mover un rey
score_table = {'p':10 ,'h': 30, 'b': 40, 'r': 60, 'q': 10, 'k':100, 'P':10, 'H':30, 'B':40, 'R':60, 'Q':10, 'K':100, ' ':0}

def calc_row(position): #Calcula la fila de una posición
    return position//16

def calc_col(position): #Calcula la columna de una posición
    return position%16

def calc_score(board, from_pos, to_pos):
    score = score_table[board[from_pos]] + score_table[board[to_pos]] * 10
    return score
def move_pawn(board, isWhite, position, best_score):
    to_pos = -1 #Posición que vamos a retornar si encontramos un movimiento con
                #mayor puntaje que best_score
    local_score = -1
    local_col = calc_col(position)
    local_row = calc_row(position)

    if isWhite:
        if (board[position-16] == ' '): #Podemos movernos hacia adelante?
            move_score = score_table['p']   #Puntaje que obtendríamos en este movimiento
            if (move_score > best_score): #Es el mejor movimiento hasta ahora?
                to_pos = position - 16
                local_score = move_score

        if ((local_row == 12) and (board[position - 32] == ' ')):     #Puedo realizar un paso doble?
            move_score = score_table['p'] + 1 #Sumo 1 para dar prioridad a saltos dobles
            
            if(move_score > best_score and move_score > local_score):
                to_pos = position - 32
                local_score = move_score
        
        if (local_col > 0 and board[position - 17].islower()): #A mi izquierda existe una pieza negra?
            move_score = score_table[board[position - 17]] * 10 + score_table['p']
            if (move_score > best_score and move_score > local_score):
                to_pos = position -17
                local_score = move_score

        if (local_col < 15 and board[position - 15].islower()): #A mi derecha existe una pieza negra?
            move_score = score_table[board[position - 15]] * 10 + score_table['p']
            if (move_score > best_score and move_score > local_score):
                to_pos = position -15
                local_score = move_score


    else:                               #Misma lógica invertida para fichas negras
        if (board[position+16] == ' '):
            move_score = score_table['p']
            if (move_score > best_score):
                to_pos = position + 16
                local_score = move_score

        if (local_row == 3 and board[position + 32] == ' '):     #Puedo realizar un paso doble?
            move_score = score_table['p'] + 1 #Sumo 1 para dar prioridad a saltos dobles
            
            if(move_score > best_score and move_score > local_score):
                to_pos = position + 32
                local_score = move_score

        if (local_col > 0 and board[position + 15].isupper()): 
            move_score = score_table[board[position +15]] * 10 + score_table['p']
            if (move_score > best_score and move_score > local_score):
                to_pos = position +15
                local_score = move_score


        if (local_col < 15 and board[position + 17].isupper()): 
            move_score = score_table[board[position +17]] * 10 + score_table['p']
            if (move_score > best_score and move_score > local_score):
                to_pos = position +17
                local_score = move_score


    return to_pos
        
def move_knight(board, isWhite, position, best_score):
    to_pos = -1

    local_score = -1
    local_col = calc_col(position)
    local_row = calc_row(position)

    #Hay que intentar mover a las posiciones -14, -18, -31, -33, +14, +18, +31, +33

    if(local_col>0): #En este caso es posible visitar las posiciones -33, +31
        #Revisar posición -33
        if (
            (local_row >1)
            and
            (   not board[position-33].islower() and not isWhite
                or
                not board[position-33].isupper() and isWhite
            )): #Puedo mover a esa posición?
                
            local_score = calc_score(board, position, position-33)
            if (local_score>best_score):
                to_pos = position-33
        #Revisar posición +31
        if ((local_row<14) 
            and
            (   not board[position+31].islower() and not isWhite
                or
                not board[position+31].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position+31)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+31
    #Revisar posiciones -18, +14
    if(local_col>1):
        #Revisar posición -18
        if (
            (local_row >0)
            and
            (   not board[position-18].islower() and not isWhite
                or
                not board[position-18].isupper() and isWhite
            )): #Puedo mover a esa posición?
            move_score = calc_score(board, position, position-18)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position-18
        #Revisar posición +14
        if (
            (local_row <15)
            and
            (   not board[position+14].islower() and not isWhite
                or
                not board[position+14].isupper() and isWhite
            )): #Puedo mover a esa posición?
            move_score = calc_score(board, position, position+14)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+14
    #Revisar posiciones -31, +33
    if(local_col<15):
        #Revisar posición -31
        if (
            (local_row >1)
            and
            (   not board[position-31].islower() and not isWhite
                or
                not board[position-31].isupper() and isWhite
            )): #Puedo mover a esa posición?
            move_score = calc_score(board, position, position-31)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position-31
        #Revisar posición +33
        if (
            (local_row <14)
            and
            (   not board[position+33].islower() and not isWhite
                or
                not board[position+33].isupper() and isWhite
            )): #Puedo mover a esa posición?
            move_score = calc_score(board, position, position+33)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+33
    #Revisar posiciones -14, +18
    if(local_col<14):
        #Revisar posición -14
        if (
            (local_row >0)
            and
            (   not board[position-14].islower() and not isWhite
                or
                not board[position-14].isupper() and isWhite
            )): #Puedo mover a esa posición?
            move_score = calc_score(board, position, position-14)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position-14
        #Revisar posición +18
        if (
            (local_row <15)
            and
            (   not board[position+18].islower() and not isWhite
                or
                not board[position+18].isupper() and isWhite
            )): #Puedo mover a esa posición?
            move_score = calc_score(board, position, position+18)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+18

    return to_pos

def move_king(board, isWhite, position, best_score):
    to_pos = -1

    local_score = -1
    local_col = calc_col(position)
    local_row = calc_row(position)
    #Un rey se puede mover a las posiciones +1, -1, -17, -16, -15, +15, +16, +17
    if(local_col>0): #Revisar posiciones -17, -1, +15
        #Revisar posición -17
        if (
            (local_row >0)
            and
            (   not board[position-17].islower() and not isWhite
                or
                not board[position-17].isupper() and isWhite
            )): #Puedo mover a esa posición?
                
            local_score = calc_score(board, position, position-17)
            if (local_score>best_score):
                to_pos = position-17
        #Revisar posición -1
        if (
            (   not board[position-1].islower() and not isWhite
                or
                not board[position-1].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position-1)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position-1

        #Revisar posición +15
        if ((local_row<15) 
            and
            (   not board[position+15].islower() and not isWhite
                or
                not board[position+15].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position+15)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+15
    #Revisar posiciones -15, +1, +17
    if (local_col<15):
        #Revisar posición -15
        if ((local_row>0) 
            and
            (   not board[position-15].islower() and not isWhite
                or
                not board[position-15].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position-15)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position-15
        #Revisar posición +17
        if ((local_row<15) 
            and
            (   not board[position+17].islower() and not isWhite
                or
                not board[position+17].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position+17)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+17
        #Revisar posición +1
        if ( 
            
            (   not board[position+1].islower() and not isWhite
                or
                not board[position+1].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position+1)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+1
    #Revisar posición +16
    if ((local_row<15) 
            and
            (   not board[position+16].islower() and not isWhite
                or
                not board[position+16].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position+16)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position+16
    #Revisar posición -16            
    if ((local_row>0) 
            and
            (   not board[position-16].islower() and not isWhite
                or
                not board[position-16].isupper() and isWhite)):
            
            move_score = calc_score(board, position, position-16)
            if (move_score > max(local_score, best_score)):
                local_score = move_score
                to_pos = position-16
    return to_pos

def move_bishop(board, isWhite, position, best_score):
    to_pos = -1

    local_score = -1
    local_col = calc_col(position)
    local_row = calc_row(position)
    local_score = 0

    cols_left = local_col -1
    cols_right = 15 - local_col
    rows_up = local_row -1
    rows_down = 15 - local_row
    i = 1
    #Los alfiles se mueven +/- N filas y +/- N columnas
    #Movimiento arriba izquierda
    moves = min(rows_up, cols_left)
    while(moves > 0):
        check_pos = (local_row - i)*16 + local_col - i #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break



        i += 1
        moves -= 1
    #Movimiento arriba derecha
    i = 1
    moves = min(rows_up, cols_right)
    while(moves > 0):
        check_pos = (local_row - i)*16 + local_col + i #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break



        i += 1
        moves -= 1
    #Movimiento abajo izquierda
    i = 1
    moves = min(rows_down, cols_left)
    while(moves > 0):
        check_pos = (local_row + i)*16 + local_col - i #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break



        i += 1
        moves -= 1
    #Movimiento abajo derecha
    i = 1
    moves = min(rows_down, cols_right)
    while(moves > 0):
        check_pos = (local_row + i)*16 + local_col + i #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break



        i += 1
        moves -= 1
    #
    return to_pos

def move_rook(board, isWhite, position, best_score):
    to_pos = -1

    local_score = -1
    local_col = calc_col(position)
    local_row = calc_row(position)
    local_score = 0

    cols_left = local_col -1
    cols_right = 15 - local_col
    rows_up = local_row -1
    rows_down = 15 - local_row
    i = 1
    #Revisar movimiento a la izquierda
    while(cols_left > 0):
        check_pos = local_row*16 + local_col - i #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break



        i += 1
        cols_left -= 1
    #Revisar movimiento a la derecha
    i=1
    while(cols_right > 0):
        check_pos = local_row*16 + local_col + i #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break

        i += 1
        cols_right -= 1

    #Revisar movimiento hacia arriba
    i=1
    while(rows_up > 0):
        check_pos = (local_row-i)*16 + local_col #Posición a revisar
        if(board[check_pos].islower() and not isWhite or board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break

        i += 1
        rows_up -= 1
    #Revisar movimiento hacia abajo
    i=1
    while(rows_down > 0):
        check_pos = (local_row+i)*16 + local_col #Posición a revisar
        if( board[check_pos].islower() and not isWhite 
            or 
            board[check_pos].isupper() and isWhite): #No se pueden pisar fichas propias
                break
        if(not board[check_pos].islower() and not isWhite
            or
            not board[check_pos].isupper() and isWhite): #Puedo mover a esa posición?
            move_score = calc_score(board, position, check_pos)
            if(move_score > max(best_score,local_score)):
                local_score = move_score
                to_pos = check_pos
                if(board[check_pos] != " "): #No se pueden saltar fichas enemigas
                    break

        i += 1
        rows_down -= 1
    return to_pos

def move_queen(board, isWhite, position, best_score):
    to_pos = -1

    local_score = -1
    local_col = calc_col(position)
    local_row = calc_row(position)
    #
    
    to_pos = move_rook(board, isWhite, position, best_score)
    local_score = calc_score(board, position, to_pos)
    local_score = max(local_score, best_score)
    alt_move = move_bishop(board, isWhite, position, local_score) #Devuelve -1 si el movimiento de torre es mejor, o si no supera a best_score
    
    if(alt_move>0):
        return alt_move
    else:
        return to_pos

async def send(websocket, action, data):
    message = json.dumps(
        {
            'action': action,
            'data': data,
        }
    )
    print(message)
    await websocket.send(message)


async def start(auth_token):
    uri = "ws://megachess.herokuapp.com/service?authtoken={}".format(auth_token)
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                response = await websocket.recv()
                print(f"< {response}")
                data = json.loads(response)
                if data['event'] == 'update_user_list':
                    print(data['data'])
                    continue
                if data['event'] == 'gameover':
                    print("Game over.")
                    print(data['data'])
                    continue
                if data['event'] == 'ask_challenge':
                    await send(
                        websocket,
                        'accept_challenge',
                        {
                            'board_id': data['data']['board_id'],
                        },
                    )
                    continue
                if data['event'] == 'your_turn':
                    turn_board = data['data']['board']
                    isWhite = data['data']['actual_turn'] == 'white'
                    
                    expected_score = 0
                    from_pos = -1
                    to_pos = -1
                    piece_index = 0
                    for piece in turn_board:
                        #Move pawns
                        if(piece == 'p' and not isWhite or piece == 'P' and isWhite):
                            move_to = move_pawn(turn_board, isWhite, piece_index, expected_score)
                            if move_to > 0:
                                from_pos =  piece_index
                                to_pos = move_to
                                expected_score = calc_score(turn_board, from_pos, to_pos)
                        #Move knights
                        if(piece == 'h' and not isWhite or piece == 'H' and isWhite):
                            move_to = move_knight(turn_board, isWhite, piece_index, expected_score)
                            if move_to > 0:
                                from_pos =  piece_index
                                to_pos = move_to
                                expected_score = calc_score(turn_board, from_pos, to_pos)
                        #Move rooks
                        if(piece == 'r' and not isWhite or piece == 'R' and isWhite):
                            move_to = move_rook(turn_board, isWhite, piece_index, expected_score)
                            if move_to > 0:
                                from_pos =  piece_index
                                to_pos = move_to
                                expected_score = calc_score(turn_board, from_pos, to_pos)
                        #Move bishops
                        if(piece == 'b' and not isWhite or piece == 'B' and isWhite):
                            move_to = move_bishop(turn_board, isWhite, piece_index, expected_score)
                            if move_to > 0:
                                from_pos =  piece_index
                                to_pos = move_to
                                expected_score = calc_score(turn_board, from_pos, to_pos)
                        #Move queens
                        if(piece == 'q' and not isWhite or piece == 'Q' and isWhite):
                            move_to = move_queen(turn_board, isWhite, piece_index, expected_score)
                            if move_to > 0:
                                from_pos =  piece_index
                                to_pos = move_to
                                expected_score = calc_score(turn_board, from_pos, to_pos)
                        #Move kings
                        if(piece == 'k' and not isWhite or piece == 'K' and isWhite):
                            move_to = move_king(turn_board, isWhite, piece_index, expected_score)
                            if move_to > 0:
                                from_pos =  piece_index
                                to_pos = move_to
                                expected_score = calc_score(turn_board, from_pos, to_pos)
                        piece_index += 1

                    #Transformar coordenadas
                    from_row = calc_row(from_pos)
                    from_col = calc_col(from_pos)
                    to_row = calc_row(to_pos)
                    to_col = calc_col(to_pos)
                    #Lógica de primer y segundo movimiento para liberar reyes
                    if(isWhite):
                        if(turn_board[216]== "P"):
                            from_row = 13
                            from_col = 8
                            to_row = 12
                            to_col = 8
                            if(turn_board[200]== "P"):
                                from_row = 12
                                from_col = 8
                                to_row = 11
                                to_col = 8
                    else:
                        if(turn_board[40]== "p"):
                            from_row = 2
                            from_col = 8
                            to_row = 3
                            to_col = 8
                            if(turn_board[56]== "p"):
                                from_row = 3
                                from_col = 8
                                to_row = 4
                                to_col = 8

                    await send(
                        websocket,
                        'move',
                        {
                            'board_id': data['data']['board_id'],
                            'turn_token': data['data']['turn_token'],
                            'from_row': from_row,
                            'from_col': from_col,
                            'to_row': to_row,
                            'to_col': to_col,
                        },
                    )
                    print("Moved from: "+str(from_row) + ","+str(from_col))

            except Exception as e:
                print(e)
                


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        auth_token = sys.argv[1]
        asyncio.get_event_loop().run_until_complete(start(auth_token))
    else:
        print('please provide your auth_token')
