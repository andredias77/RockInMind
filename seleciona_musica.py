class Musica:

    def __init__(self):
        self.indice_musica = 1
    
    def guardar_indice_musica(self, index):
        if index == "Clássico 1":
            self.indice_musica = 1

        elif index == "Clássico 2":
            self.indice_musica = 2
        
        elif index == "Personalizada":
            self.indice_musica = 3
        
        else:
            self.indice_musica = 1

        print("Música selecionada índice =", index)
