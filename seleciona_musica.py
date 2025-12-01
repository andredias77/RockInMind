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
    
    def get_nome_musicas(self):
        return ["Smoke on the Water", "Seven Nation Army", "Anunciação"]
    
    def get_nome_imagens_musica(self):
        return [
            "assets/smoke.png",
            "assets/seven.png",
            "assets/anunciacao.png"
        ]

    def guardar_dificuldade(self, index):
        self.dificuldade = int(index)
