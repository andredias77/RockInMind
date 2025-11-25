from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from serial_thread import SerialThread
from config import NUMERO_PARA_NOTA, CORES_NOTAS, CORES_TITULO, SEQUENCIAS
from guitarra import SONS
import threading, time
import sounddevice as sd
from jogo import Jogo
import string
import time
from seleciona_musica import Musica
from queue import Queue

class RockInMindGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.jogo = Jogo()
        self.musica = Musica()
        self.fila_serial = Queue()

        # --- música padrão ---
        self.musica.guardar_indice_musica("Clássico 1")
        self.jogo.indice_musica = self.musica.indice_musica

        self.setWindowTitle("Rock In Mind 🎵")
        #self.setFixedSize(650, 650)
        self.setStyleSheet("background-color: black; color: white;")

        self.numero_para_nota = NUMERO_PARA_NOTA
        self.cores_titulo = CORES_TITULO
        self.cor_index = 0

        # ---------- STACKED WIDGET (2 telas) ----------
        self.stacked = QStackedWidget()
        self.tela_menu = self.criar_tela_menu()
        self.tela_jogo = self.criar_tela_jogo()
        self.tela_acertou = self.criar_tela_acertou()
        self.tela_errou = self.criar_tela_errou()

        self.stacked.addWidget(self.tela_menu)  # índice 0
        self.stacked.addWidget(self.tela_jogo)  # índice 1
        self.stacked.addWidget(self.tela_acertou)  # índice 2
        self.stacked.addWidget(self.tela_errou)    # índice 3
        self.stacked.setCurrentIndex(0)

        layout_principal = QVBoxLayout()
        layout_principal.addWidget(self.stacked)
        self.setLayout(layout_principal)

        # ---------- SERIAL ----------
        self.serial_thread = SerialThread(port="COM10", baud=115200)
        self.serial_thread.data_received.connect(self.receive_serial)
        self.serial_thread.start()

        # ---------- TIMER TÍTULO ----------
        self.timer = QTimer()
        self.timer.timeout.connect(self.mudar_cor_titulo)
        self.timer.start(400)

        self.atualizar_botoes()
        self.showMaximized()      # ocupa a tela toda


    # ======================================================
    #  TELA 1 — MENU PRINCIPAL
    # ======================================================
    def criar_tela_menu(self):
        tela = QWidget()
        layout = QVBoxLayout()

        titulo = QLabel("Rock In Mind 🎵")
        titulo.setFont(QFont("Arial", 28, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)

        modo_label = QLabel("Modo de jogo:")
        self.modo_combo = QComboBox()
        self.modo_combo.addItems(["Jogo", "Livre"])
        self.modo_combo.setStyleSheet("QComboBox { background-color: #222; color: white; padding: 4px; }")

        musica_label = QLabel("Música:")
        self.musica_combo = QComboBox()
        self.musica_combo.addItems(["Clássico 1", "Clássico 2", "Personalizada"])
        self.musica_combo.setStyleSheet("QComboBox { background-color: #222; color: white; padding: 4px; }")
        
        #muda a música
        self.musica_combo.currentTextChanged.connect(self.on_musica_change)



        # --- NOVO BOTÃO ---
        self.botao_serial = QPushButton("Iniciar modo Livre")
        self.botao_serial.setFixedSize(250, 40)
        self.botao_serial.setStyleSheet("QPushButton { background-color: #555; color: white; border-radius: 10px; font-weight: bold; }")
        
        # LINHA CORRETA (CONECTA a função para execução posterior):
        self.botao_serial.clicked.connect(lambda: (
            self.enviar_serial("!"),
            self.stacked.setCurrentIndex(1),
            self.jogo.guarda_modo("livre")
        ))
        
        # Layout horizontal para centralizar o botão 👈 NOVAS LINHAS
        h_layout_botao = QHBoxLayout()
        h_layout_botao.addStretch()
        h_layout_botao.addWidget(self.botao_serial)
        h_layout_botao.addStretch()
        # ------------------

        layout.addWidget(titulo)
        layout.addSpacing(30)
        layout.addWidget(modo_label)
        layout.addWidget(self.modo_combo)
        layout.addSpacing(20)
        layout.addWidget(musica_label)
        layout.addWidget(self.musica_combo)
        # O PONTO DE CORREÇÃO: Adicionar o layout do botão aqui
        layout.addSpacing(40) # Adiciona um espaçamento antes do botão
        layout.addLayout(h_layout_botao) # ADICIONA O BOTÃO AO LAYOUT PRINCIPAL
        layout.addStretch()

        tela.setLayout(layout)
        return tela

    # ======================================================
    #  TELA 2 — JOGO (BOTÕES DAS NOTAS)
    # ======================================================
    def criar_tela_jogo(self):
        tela = QWidget()
        layout = QVBoxLayout()

        self.title = QLabel("Rock In Mind")
        self.title.setFont(QFont("Arial", 36, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        notas_layout = QHBoxLayout()
        self.botoes_notas = {}

        for i, cor in enumerate(CORES_NOTAS):
            btn = QPushButton(" --- ")
            btn.setFixedSize(120, 120)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {cor}; border-radius: 20px; "
                "color: black; font-weight: bold; font-size: 16px; }}"
            )
            notas_layout.addWidget(btn)
            self.botoes_notas[str(i+1)] = (btn, cor)

        self.botao_voltar = QPushButton("VOLTAR")
        self.botao_voltar.setFixedSize(250, 40)
        self.botao_voltar.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border-radius: 10px; font-weight: bold; }"
        )
        self.botao_voltar.clicked.connect(lambda: (
            self.stacked.setCurrentIndex(0),
            self.jogo.guarda_modo("jogo")
        ))

        h_botao = QHBoxLayout()
        h_botao.addStretch()
        h_botao.addWidget(self.botao_voltar)
        h_botao.addStretch()

        layout.addSpacing(10)
        layout.addWidget(self.title)
        layout.addSpacing(30)
        layout.addLayout(notas_layout)
        layout.addStretch()
        layout.addLayout(h_botao)

        tela.setLayout(layout)
        return tela
    
    def criar_tela_acertou(self):
        tela = QWidget()
        tela.setStyleSheet("background-color: #002200; color: white;")

        layout = QVBoxLayout()

        titulo = QLabel("✔ ACERTOU! ✔")
        titulo.setFont(QFont("Arial", 30, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #00FF55;")

        caveira = QLabel("💀")
        caveira.setFont(QFont("Arial", 140))
        caveira.setAlignment(Qt.AlignCenter)

        botao = QPushButton("CONTINUAR")
        botao.setFixedSize(250, 45)
        botao.setStyleSheet("QPushButton { background-color: #00AA55; color: white; font-weight: bold; border-radius: 10px; }")
        botao.clicked.connect(lambda: self.stacked.setCurrentIndex(0))

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addSpacing(10)
        layout.addWidget(caveira)
        layout.addSpacing(30)
        layout.addWidget(botao, alignment=Qt.AlignCenter)
        layout.addStretch()

        tela.setLayout(layout)
        return tela
    
    def criar_tela_errou(self):
        tela = QWidget()
        tela.setStyleSheet("background-color: #220000; color: white;")

        layout = QVBoxLayout()

        titulo = QLabel("✘ ERROU! ✘")
        titulo.setFont(QFont("Arial", 30, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #FF3333;")

        caveira = QLabel("💀")
        caveira.setFont(QFont("Arial", 140))
        caveira.setAlignment(Qt.AlignCenter)

        botao = QPushButton("CONTINUAR")
        botao.setFixedSize(250, 45)
        botao.setStyleSheet("QPushButton { background-color: #AA0000; color: white; font-weight: bold; border-radius: 10px; }")
        botao.clicked.connect(lambda: self.stacked.setCurrentIndex(0))

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addSpacing(10)
        layout.addWidget(caveira)
        layout.addSpacing(30)
        layout.addWidget(botao, alignment=Qt.AlignCenter)
        layout.addStretch()

        tela.setLayout(layout)
        return tela
    
    def limpar(self, msg):
        return "".join(c for c in msg if c in string.printable)

    def receive_serial(self, msg):
        msg = msg.strip()
        msg = self.limpar(msg)
        self.fila_serial.put(msg)

        print("[RECEBIDO SERIAL]:", msg)

        if msg.endswith("H") and len(msg) > 1:
            print(msg)
            self.play_note(msg)      
            return
        
        if msg.endswith("H") and len(msg) == 1:
            print(msg)
            low = self.fila_serial.get()
            digito = self.fila_serial.get()
            mensagem = str(digito) + str(low)
            self.play_note(mensagem)      
            return
        
        if (msg.endswith("L")) and len(msg) == 4:
            print("vefh")
            high = msg[:2]
            low = msg[2:]
            self.play_note(high)
            correta = self.jogo.registrar_jogada(low)
            time.sleep(1)
            self.play_note(low)
            if correta == 2:
                self.enviar_serial("T")
                print("Enviou T")
                return
            if correta:
                self.enviar_serial("A")
            else: 
                self.enviar_serial("E")
                if self.jogo.get_modo():
                    self.stacked.setCurrentIndex(0)         
            return

        # ------- troca para tela do jogo -------
        if msg[0] == "#":
            print("[Serial] Iniciando jogo → indo para tela 2")
            self.stacked.setCurrentIndex(1)
            idx_musica = str(self.musica.indice_musica)
            self.enviar_serial(idx_musica)
            return    

        if msg.startswith("T") and len(msg) > 1:
            indice = msg[1:]
            self.tocar_sequencia(indice)
            return  

        if (msg.endswith("L")) and len(msg) > 1:
            correta = self.jogo.registrar_jogada(msg)
            self.play_note(msg)
            if correta == 2:
                self.stacked.setCurrentIndex(2)
                self.enviar_serial("T")
            if correta:
                self.enviar_serial("A")
            else: 
                self.enviar_serial("E")
                if self.jogo.get_modo():
                    self.stacked.setCurrentIndex(3)        
            return
        
        if msg.endswith("L") and len(msg) == 1:
            low = self.fila_serial.get()
            digito = self.fila_serial.get()
            mensagem = str(digito) + str(low)
            correta = self.jogo.registrar_jogada(mensagem)
            self.play_note(mensagem)
            if correta == 2:
                self.enviar_serial("T")
            if correta:
                self.enviar_serial("A")
            else: 
                self.enviar_serial("E")
                if self.jogo.get_modo():
                    self.stacked.setCurrentIndex(0)        
            return
            

    
    def tocar_sequencia(self, indice):
        indice = int(indice)
        idx_musica = self.musica.indice_musica
        sequencia = SEQUENCIAS.get(idx_musica)
        if not sequencia:
            print(f"[Sequência] {indice} não encontrada")
            return

        limite = indice + 1
        sequencia_cortada = sequencia[:limite]
        self.jogo.iniciar_rodada(sequencia_cortada)

        print(f"[Sequência] Tocando T{indice}")

        # lista de eventos que o QTimer vai executar sem travar a UI
        eventos = []

        for numero, duracao in sequencia_cortada:
            numero = int(numero)
            eventos.append((f"{numero}H", duracao))   # aperta
            eventos.append((f"{numero}L", 0.15))      # solta

        # função recursiva para tocar cada evento com singleShot
        def tocar_proximo(i):
            if i >= len(eventos):
                self.enviar_serial("F")
                return

            msg, dur = eventos[i]
            self.play_note(msg)

            # chama o próximo após o intervalo
            QTimer.singleShot(int(dur * 1000), lambda: tocar_proximo(i + 1))

        # inicia a sequência com pequeno atraso
        QTimer.singleShot(300, lambda: tocar_proximo(0))


    def play_note(self, msg):
        numero = msg[:-1]  # tudo menos o último caractere
        estado = msg[-1].upper()  # último caractere (H ou L)
        
        numero_musica = self.musica.indice_musica  
        nota = NUMERO_PARA_NOTA[numero_musica].get(numero)
        if nota:
            nota = nota.upper()
            if numero in self.botoes_notas:
                btn, cor_original = self.botoes_notas[numero]
                if estado == "H":
                    btn.setStyleSheet("background-color: white; color: black; border-radius: 20px; font-weight: bold;")
                    # toca a nota
                    onda, fs = SONS[nota]
                    sd.play(onda, fs)
                    # freq = NOTAS_FREQ.get(nota)
                    # if freq:
                    #     threading.Thread(target=guitarra_sintetica, args=(freq,), daemon=True).start()
                elif estado == "L":
                    btn.setStyleSheet(f"background-color: {cor_original}; color: black; border-radius: 20px; font-weight: bold;")
                    sd.stop()

    def mudar_cor_titulo(self):
        cor = self.cores_titulo[self.cor_index]
        self.title.setStyleSheet(f"color: {cor};")
        self.cor_index = (self.cor_index + 1) % len(self.cores_titulo)

    def closeEvent(self, event):
        self.serial_thread.stop()
        super().closeEvent(event)

    def enviar_serial(self, msg):
        """Envia mensagem pela serial, se estiver conectado"""
        # verifica se self.serial_thread e self.serial_thread.ser existem
        if getattr(self, "serial_thread", None) and getattr(self.serial_thread, "ser", None):
            if self.serial_thread.ser.is_open:
                try:
                    self.serial_thread.ser.write((msg + "\n").encode())
                    print("Mensagem serial enviada", msg)
                except Exception as e:
                    print("[Serial] Erro ao enviar:", e)

    def on_musica_change(self, texto):
        self.musica.guardar_indice_musica(texto)
        self.jogo.indice_musica = self.musica.indice_musica
        self.atualizar_botoes()
    
    def atualizar_botoes(self):
        idx = self.musica.indice_musica   # 1, 2 ou 3
        notas = NUMERO_PARA_NOTA[idx]     # pega o mapa daquela música

        # para cada botão 1..8, mude o texto
        for numero, (btn, cor) in self.botoes_notas.items():
            nome_nota = notas[numero]   # ex: "DO1", "RE2"...
            btn.setText(nome_nota)

    def resizeEvent(self, event):
        # chamado sempre que a janela é redimensionada
        largura = self.width()
        altura = self.height()

        # calcula tamanho base para os botões (8 botões lado a lado)
        # deixa um pequeno padding (20 px) entre eles
        btn_width = max(80, (largura - 200) // max(1, len(self.botoes_notas)))  # largura mínima 80
        btn_height = max(80, int(altura * 0.25))  # não exagere na altura

        # limita para não ficar gigante
        btn_size = min(btn_width, btn_height)

        # atualiza tamanho dos botões (se já foram criados)
        for numero, (btn, cor) in getattr(self, "botoes_notas", {}).items():
            btn.setFixedSize(btn_size, btn_size)
            # opcional: ajustar tamanho da fonte do texto do botão
            font = btn.font()
            font.setPointSize(max(10, btn_size // 6))
            btn.setFont(font)

        # ajusta fonte do título com base na altura da janela
        if hasattr(self, "title"):
            f = self.title.font()
            f.setPointSize(max(18, altura // 20))
            self.title.setFont(f)

        super().resizeEvent(event)
