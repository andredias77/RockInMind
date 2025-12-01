class Musica:

    def __init__(self):
        self.indice_musica = 1
        self.dificuldade = 1
    
    def guardar_indice_musica(self, index):
        if index == "Smoke on the Water":
            self.indice_musica = 1

        elif index == "Seven Nation Army":
            self.indice_musica = 2
        
        elif index == "Anunciação":
            self.indice_musica = 3
        
        else:
            self.indice_musica = 1

        print("Música selecionada índice =", index)

    def guardar_dificuldade(self, index):
        self.dificuldade = int(index)
