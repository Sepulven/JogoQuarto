from jogos_melhor import *
from quarto import *
# from novicius import *
# from optimus import *
# from basicus import *

def func_alumnus(estado, jogador):
    #TODO
    return 0

def jogador_alumnus(jogo, estado):
    return alphabeta_cutoff_search_new(estado, jogo, d=1, eval_fn=func_alumnus)


jogo = JogoQuarto()
print(f"Move timeout: {jogo.MOVE_TIMEOUT}s")
