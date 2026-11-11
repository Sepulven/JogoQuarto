from jogos_melhor import *
from quarto import *
# from novicius import *
# from optimus import *
# from basicus import *


Piece_64726 = tuple[int, int, int, int]
Position_64726 = tuple[int, int]
Board_64726 = dict[Position_64726, Piece_64726]
Move_64726 = tuple[Position_64726 | None, Piece_64726 | None]


"""
Helper class for the project.
"""
class Utils_64726:
    @staticmethod
    def can_win(state: EstadoQuarto) -> bool:
        piece: Piece_64726 | None = state.piece_in_hand
        if piece is None:
            return False

        pos: Position_64726
        # NOTE: 
        for pos in ALL_POSITIONS:
            if pos in state.board: continue

            board: Board_64726 = dict(state.board)
            board[pos] = piece
            test: EstadoQuarto = EstadoQuarto(state.to_move, board, None, ())
            if any(test.check_line_win(line) for line in LINES if pos in line):
                return True

        return False

def func_alumnus(estado: EstadoQuarto, jogador: str) -> float:
    winner: str | None = estado.winner()
    if winner == jogador: return infinity
    if winner == estado.other(jogador): return -infinity
    if winner == 'Draw': return 0
    ## Creates an alias to the static class
    H: type[Utils_64726] = Utils_64726

    if (H.can_win(estado)):
        return infinity if estado.to_move == jogador else -infinity

    return 0

def jogador_alumnus(jogo: JogoQuarto, estado: EstadoQuarto):
    depth: int = 2
    n: int  = len(estado.available_pieces)
    if (n >= 12): depth = 2
    elif (n >= 11): depth = 3
    elif (n >= 9): depth = 3
    elif (n == 8): depth = 4
    elif (n == 7): depth = 4
    elif (n <= 6): depth = n

    return alphabeta_cutoff_search_new(estado, jogo, d=depth, eval_fn=func_alumnus)

if __name__ == "__main__":
    jogo: JogoQuarto = JogoQuarto()
    print(f"Move timeout: {jogo.MOVE_TIMEOUT}s")
