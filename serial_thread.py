import time
from PyQt5.QtCore import QThread, pyqtSignal
import serial

class SerialThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port="COM10", baud=115200, simulate_if_error=True):
        super().__init__()
        self.port = port
        self.baud = baud
        self.running = True
        self.simulate_if_error = simulate_if_error
        self.ser = None 

    def run(self):
        try:
            self.ser = serial.Serial(
                self.port,
                self.baud,
                timeout=0.1,
                parity=serial.PARITY_NONE,     # <-- SEM PARIDADE
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE
            )
            
            print(f"[Serial] Conectado em {self.port} (115200, 8N1)")
            while self.running:
                if self.ser.in_waiting > 0:
                    msg = self.ser.readline().decode(errors="ignore").strip()
                    if msg:
                        self.data_received.emit(msg)
                time.sleep(0.02)
        except Exception as e:
            print(f"[Serial] Erro: {e}")
            if self.simulate_if_error:
                print("[Serial] Entrando no modo SIMULAÇÃO...")
                notas = ["#T00", "T01", "T02", "T03", "T04", "T05"]
                while self.running:
                    for nota in notas:
                        self.data_received.emit(nota)
                        time.sleep(2.0)

    def stop(self):
        self.running = False
        self.quit()
