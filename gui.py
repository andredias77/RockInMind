from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from serial_thread import SerialThread
from config import NUMERO_PARA_NOTA, CORES_NOTAS, CORES_TITULO
from guitarra import NOTAS_FREQ, guitarra_sintetica
from config import SEQUENCIAS
import threading, time
import sounddevice as sd
from jogo import Jogo
import string
import time


class RockInMindGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.jogo = Jogo()

        self.setWindowTitle("Rock In Mind 🎵")
        self.setFixedSize(650, 650)
        self.setStyleSheet("background-color: black; color: white;")

        self.numero_para_nota = NUMERO_PARA_NOTA
        self.cores_titulo = CORES_TITULO
        self.cor_index = 0

        # ---------- STACKED WIDGET (2 telas) ----------
        self.stacked = QStackedWidget()
        self.tela_menu = self.criar_tela_menu()
        self.tela_jogo = self.criar_tela_jogo()

        self.stacked.addWidget(self.tela_menu)  # índice 0
        self.stacked.addWidget(self.tela_jogo)  # índice 1
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

        # --- NOVO BOTÃO ---
        self.botao_serial = QPushButton("Enviar Sinal '!' (Serial)")
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
        self.title.setFont(QFont("Arial", 28, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        notas_layout = QGridLayout()
        nomes_notas = list(NUMERO_PARA_NOTA.values())
        self.botoes_notas = {}

        for i, (nome, cor) in enumerate(zip(nomes_notas, CORES_NOTAS)):
            btn = QPushButton(nome)
            btn.setFixedSize(120, 120)
            btn.setStyleSheet(f"QPushButton {{ background-color: {cor}; border-radius: 20px; color: black; font-weight: bold; font-size: 16px; }}")
            self.botoes_notas[nome.upper()] = (btn, cor)
            notas_layout.addWidget(btn, i // 4, i % 4)

        # --- NOVO BOTÃO ---
        self.botao_serial = QPushButton("VOLTAR")
        self.botao_serial.setFixedSize(250, 40)
        self.botao_serial.setStyleSheet("QPushButton { background-color: #555; color: white; border-radius: 10px; font-weight: bold; }")
        
        # LINHA CORRETA (CONECTA a função para execução posterior):
        self.botao_serial.clicked.connect(lambda: (
            self.stacked.setCurrentIndex(0),
            self.jogo.guarda_modo("jogo")
        ))
        
        # Layout horizontal para centralizar o botão 👈 NOVAS LINHAS
        h_layout_botao = QHBoxLayout()
        h_layout_botao.addStretch()
        h_layout_botao.addWidget(self.botao_serial)
        # O PONTO DE CORREÇÃO: Adicionar o layout do botão aqui
        layout.addSpacing(40) # Adiciona um espaçamento antes do botão
        layout.addLayout(h_layout_botao) # ADICIONA O BOTÃO AO LAYOUT PRINCIPAL
        h_layout_botao.addStretch()
        # ------------------

        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addLayout(notas_layout)
        layout.addStretch()

        tela.setLayout(layout)
        return tela
    
    def limpar(self, msg):
        return "".join(c for c in msg if c in string.printable)

    def receive_serial(self, msg):
        msg = msg.strip()
        msg = self.limpar(msg)

        print("[RECEBIDO SERIAL]:", msg)

        if msg.endswith("H") and len(msg) > 1:
            self.play_note(msg)      
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
            msg2 = msg[1:]        # "TXX"
            indice = msg[2:]      # "XX"
            print("msg2 =", msg2)
            print("indice =", indice)
            self.tocar_sequencia(indice)
            return    

        if msg.startswith("T") and len(msg) > 1:
            indice = msg[1:]
            self.tocar_sequencia(indice)
            return  

        if (msg.endswith("L")) and len(msg) > 1:
            correta = self.jogo.registrar_jogada(msg)
            self.play_note(msg)
            if correta:
                self.enviar_serial("A")
            else: 
                self.enviar_serial("E")
                if self.jogo.get_modo():
                    self.stacked.setCurrentIndex(0)        
            return

    
    def tocar_sequencia(self, indice):
        time.sleep(0.5)
        indice = int(indice)
        sequencia = SEQUENCIAS.get(indice)
        if not sequencia:
            print(f"[Sequência] {indice} não encontrada")
            return
        
        limite = int(indice) + 1
        sequencia_cortada = sequencia[:limite]
        self.jogo.iniciar_rodada(sequencia_cortada)

        print(f"[Sequência] Tocando T{indice}")

        for numero, duracao in sequencia_cortada:
            msg = f"{numero}H"   # ou o formato que seu play_note espera
            self.play_note(msg)
            time.sleep(duracao)
            msg = f"{numero}L"
            self.play_note(msg)
        time.sleep(0.1)
        self.enviar_serial("F")

    def play_note(self, msg):
        numero = msg[:-1]  # tudo menos o último caractere
        estado = msg[-1].upper()  # último caractere (H ou L)
        
        nota = self.numero_para_nota.get(numero)
        if nota:
            nota = nota.upper()
            if nota in self.botoes_notas:
                btn, cor_original = self.botoes_notas[nota]
                if estado == "H":
                    btn.setStyleSheet("background-color: white; color: black; border-radius: 20px; font-weight: bold;")
                    # toca a nota
                    freq = NOTAS_FREQ.get(nota)
                    if freq:
                        threading.Thread(target=guitarra_sintetica, args=(freq,), daemon=True).start()
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