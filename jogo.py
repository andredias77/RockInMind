from config import TAMANHO
from seleciona_musica import Musica
class Jogo:

    def _init_(self):
        self.sequencia_atual = []
        self.jogadas = []
        self.livre = False
        self.indice_musica = 1

    def iniciar_rodada(self, sequencia):
        # salva só o pedaço que deve ser tocado nessa rodada
        self.sequencia_atual = sequencia
        self.jogadas = []

    def registrar_jogada(self, msg):
        indice = len(self.jogadas)
        numero = msg[:-1]

        
        # se já acabou, não precisa comparar
        if indice >= len(self.sequencia_atual):
            return False

        correta = self.sequencia_atual[indice][0]  # "numero"
        self.jogadas.append(numero)

        if (correta and len(self.jogadas) == TAMANHO[self.indice_musica]):
            return 2

        return numero == correta
        
    def compara_jogada(self, msg):
        indice = len(self.jogadas)

        estado_bruto = msg[-1].upper()  # último caractere (H ou L)
        numero = msg[:-1]

        if estado_bruto == "L":
            return
        else: 
        
            # se já acabou, não precisa comparar
            if indice >= len(self.sequencia_atual):
                return False

            correta = self.sequencia_atual[indice][0]  # "numero"
            self.jogadas.append(numero)

            return numero == correta
        
    def guarda_modo(self, msg):
        if msg == "livre":
            self.livre = True
            return
        else:
            self.livre = False
            return
    
    def get_modo(self):
        return not(self.livre)


    def terminou(self):
        return len(self.jogadas) == len(self.sequencia_atual)