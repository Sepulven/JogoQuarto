"""
Jogo Quarto (Quarto Board Game)
Modelação do estado e classe de jogo compatível com a biblioteca AIMA (jogos.py).
Inclui suporte a timeout por jogada definido como constante da classe JogoQuarto.
"""

from collections import namedtuple
import copy
import time
from jogos_melhor import Game, infinity


def tempo_de_execucao(func, *args, **kwargs):
    inicio = time.perf_counter()
    resultado = func(*args, **kwargs)
    fim = time.perf_counter()

    duracao = fim - inicio
    return resultado, duracao


# --- Exemplo de uso ---

def fib(n):
    if n <= 1:
        return 1
    return fib(n-2) + fib(n - 1)

stateQuarto = namedtuple('stateQuarto', 'to_move, board, piece_in_hand, available_pieces')

ALL_PIECES = tuple(
    (a, c, f, t)
    for a in (0, 1)
    for c in (0, 1)
    for f in (0, 1)
    for t in (0, 1)
)

ALL_POSITIONS = tuple((r, c) for r in range(4) for c in range(4))

LINES = [
            [(r, c) for c in range(4)] for r in range(4)
        ] + [
            [(r, c) for r in range(4)] for c in range(4)
        ] + [
            [(i, i) for i in range(4)],
            [(i, 3 - i) for i in range(4)]
        ]


class EstadoQuarto(stateQuarto):
    def other(self, player=None):
        p = player if player is not None else self.to_move
        return 'PLAYER2' if p == 'PLAYER1' else 'PLAYER1'

    def possible_moves(self):
        vagas = [pos for pos in ALL_POSITIONS if self.board.get(pos) is None]

        if self.piece_in_hand is None:
            return [(None, p) for p in self.available_pieces]

        moves = []
        rem_pieces = [p for p in self.available_pieces if p != self.piece_in_hand]

        if not rem_pieces:
            for pos in vagas:
                moves.append((pos, None))
        else:
            for pos in vagas:
                for next_p in rem_pieces:
                    moves.append((pos, next_p))

        return moves

    def next_state(self, action):
        pos, next_piece = action
        new_board = dict(self.board)

        if pos is not None:
            new_board[pos] = self.piece_in_hand

        new_available = tuple(p for p in self.available_pieces if
                              p != self.piece_in_hand) if self.piece_in_hand else self.available_pieces

        next_player = self.other()
        return EstadoQuarto(
            to_move=next_player,
            board=new_board,
            piece_in_hand=next_piece,
            available_pieces=new_available
        )

    def check_line_win(self, line):
        pieces = [self.board.get(pos) for pos in line]
        if any(p is None for p in pieces):
            return False

        for attr_idx in range(4):
            val = pieces[0][attr_idx]
            if all(p[attr_idx] == val for p in pieces[1:]):
                return True
        return False

    def winner(self):
        for line in LINES:
            if self.check_line_win(line):
                return self.other()

        if len(self.board) == 16:
            return 'Draw'

        return None

    def display(self):
        print("    0    1    2    3")
        print("  +----+----+----+----+")
        for r in range(4):
            row_str = f"{r} |"
            for c in range(4):
                p = self.board.get((r, c))
                if p is None:
                    row_str += " .  |"
                else:
                    row_str += f"{p[0]}{p[1]}{p[2]}{p[3]}|"
            print(row_str)
            print("  +----+----+----+----+")
        print(f"Peça na mão do jogador ({self.to_move}): {self.piece_in_hand}")
        print("Posições livres:", set(ALL_POSITIONS)-set(self.board.keys()))
        print(f"Peças disponíveis na reserva ({len(self.available_pieces)}): {self.available_pieces}\n")


class JogoQuarto(Game):
    """
    Implementação da classe de jogo Quarto com gestão de timeout.
    """
    # Constante da classe que define o tempo limite (em segundos) por jogada
    MOVE_TIMEOUT = tempo_de_execucao(fib, 35)[1]

    def __init__(self, timeout=None):
        if timeout is not None:
            self.MOVE_TIMEOUT = timeout

        initial_board = {}
        initial_pieces = ALL_PIECES
        self.initial = EstadoQuarto(
            to_move='PLAYER1',
            board=initial_board,
            piece_in_hand=None,
            available_pieces=initial_pieces
        )
        self.disqualified_player = None

    def actions(self, state):
        return state.possible_moves()

    def result(self, state, move):
        return state.next_state(move)

    def utility(self, state, player):
        if self.disqualified_player is not None:
            return -1 if player == self.disqualified_player else 1

        win = state.winner()
        if win == player:
            return 1
        elif win == state.other(player):
            return -1
        return 0

    def terminal_test(self, state):
        if self.disqualified_player is not None:
            return True
        return state.winner() is not None

    def to_move(self, state):
        return state.to_move

    def display(self, state):
        state.display()

    def jogar(self, jogador1, jogador2, verbose=True):
        """
        Executa uma partida monitorizando o tempo por jogada.
        Se um jogador exceder MOVE_TIMEOUT, é desclassificado (derrota automática).
        """
        try:
            self.nome_player1 = getattr(jogador1, 'name', jogador1.__name__).split('_')[1]
            self.nome_player2 = getattr(jogador2, 'name', jogador2.__name__).split('_')[1]
        except:
            self.nome_player1 = "player 1"
            self.nome_player2 = "player 2"
        estado = self.initial
        self.disqualified_player = None
        if verbose:
            self.display(estado)

        fim = False
        jogadores = (jogador1, jogador2)
        ind_proximo = 0

        while not fim:
            jogador_atual = estado.to_move

            # Medição do tempo de execução da jogada (posicionar peça + escolher próxima)
            start_time = time.time()
            jogada = jogadores[ind_proximo](self, estado)
            elapsed_time = time.time() - start_time

            # Verificação de timeout
            if elapsed_time > self.MOVE_TIMEOUT:
                if verbose:
                    print(f"\n TIMEOUT! O jogador {jogador_atual} demorou {elapsed_time:.3f}s "
                          f"(Limite: {self.MOVE_TIMEOUT:.2f}s) e foi desclassificado!\n")
                self.disqualified_player = jogador_atual
                break

            # NOVA VALIDAÇÃO: Verifica se a jogada faz parte das jogadas legais possíveis
            if jogada not in self.actions(estado):
                if verbose:
                    print(f"\n JOGADA INVÁLIDA! O jogador {jogador_atual} devolveu uma jogada ilegal: {jogada}\n")
                self.disqualified_player = jogador_atual
                break

            estado = self.result(estado, jogada)
            if verbose:
                print(f"Tempo da jogada de {jogador_atual}: {elapsed_time:.3f}s")
                self.display(estado)

            fim = self.terminal_test(estado)
            ind_proximo = 1 - ind_proximo

        utilidade = self.utility(estado, self.to_move(self.initial))
        return utilidade


