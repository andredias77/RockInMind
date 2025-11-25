import numpy as np
import sounddevice as sd

# frequências padrão (Hz)
NOTAS_FREQ = {
    "DO1": 32.70,
    "RE1": 36.71,
    "MI1": 41.20,
    "FA1": 43.65,   # corrigido
    "SOL1": 49.00,  # corrigido
    "LA1": 55.00,
    "SI1": 61.74,
    "DO2": 65.41,
    "RE2": 73.42,
    "MI2": 82.41,
    "FA2": 87.31,
    "SOL2": 98.00,
    "LA2": 110.00,
    "SI2": 123.47,
    "DO3": 130.81,
    "RE3": 146.83,
    "MI3": 164.81,
    "FA3": 174.61,
    "SOL3": 196.00,
    "LA3": 220.00,
    "SI3": 246.94,
    "SIb3": 233.08,
    "DO4": 261.63,
    "REb4": 277.18,
}

# toca som de guitarra em thread separada

def guitarra_sintetica(freqs, duracao=2, volume=0.5):
    fs = 44100
    t = np.linspace(0, duracao, int(fs * duracao), False)

    if not isinstance(freqs, (list, tuple)):
        freqs = [freqs]

    # mistura ondas serrilhadas e triangulares para um timbre mais agressivo
    onda = np.zeros_like(t)
    for f in freqs:
        seno = np.sin(2 * np.pi * f * t)
        serra = 2 * (t * f % 1) - 1
        tri = 2 * np.abs(serra) - 1
        onda += 0.6 * serra + 0.4 * tri + 0.2 * seno

    onda /= len(freqs)

    # Envelope ADSR
    ataque, decaimento, sustain, release = 0.005, 0.08, 0.6, 0.1
    env = np.ones_like(t)
    a_n = int(ataque * fs)
    d_n = int(decaimento * fs)
    r_n = int(release * fs)

    env[:a_n] = np.linspace(0, 1, a_n)
    env[a_n:a_n+d_n] = np.linspace(1, sustain, d_n)
    env[a_n+d_n:-r_n] = sustain
    env[-r_n:] = np.linspace(sustain, 0, r_n)
    onda *= env

    # --- Distorção mais "metal" ---
    ganho = 15
    onda = np.tanh(ganho * onda)

    # --- Filtro passa-baixas + passa-altas (simula caixa Marshall) ---
    # passa-altas leve (tira grave embolado)
    for i in range(1, len(onda)):
        onda[i] = 0.8 * (onda[i] - 0.9 * onda[i-1])
    # passa-baixas suave (remove chiado)
    alpha = 0.1
    for i in range(1, len(onda)):
        onda[i] = onda[i-1] + alpha * (onda[i] - onda[i-1])

    # --- Chorus leve (efeito estéreo) ---
    delay = int(0.003 * fs)
    mix = 0.3
    onda_stereo = np.zeros((len(onda), 2))
    onda_stereo[:, 0] = onda  # canal L
    onda_stereo[:, 1] = np.roll(onda, delay) * mix + onda * (1 - mix)  # canal R

    # --- Normaliza e toca ---
    onda_stereo = np.clip(onda_stereo * volume, -1, 1)
    sd.play(onda_stereo, fs)

import numpy as np

def gerar_onda(freq, duracao=1.5, volume=0.5):
    fs = 44100
    t = np.linspace(0, duracao, int(fs * duracao), False)

    # ondas
    seno = np.sin(2 * np.pi * freq * t)
    serra = 2 * (t * freq % 1) - 1
    tri = 2 * np.abs(serra) - 1

    onda = 0.6 * serra + 0.4 * tri + 0.2 * seno

    # ADSR
    ataque, decaimento, sustain, release = 0.005, 0.08, 0.6, 0.1
    env = np.ones_like(t)
    fs_a = int(ataque * fs)
    fs_d = int(decaimento * fs)
    fs_r = int(release * fs)

    env[:fs_a] = np.linspace(0, 1, fs_a)
    env[fs_a:fs_a+fs_d] = np.linspace(1, sustain, fs_d)
    env[fs_a+fs_d:-fs_r] = sustain
    env[-fs_r:] = np.linspace(sustain, 0, fs_r)
    onda *= env

    # distorção
    onda = np.tanh(15 * onda)

    # filtro passa-baixas
    alpha = 0.1
    for i in range(1, len(onda)):
        onda[i] = onda[i-1] + alpha * (onda[i] - onda[i-1])

    # chorus estéreo
    delay = int(0.003 * fs)
    mix = 0.3
    onda_stereo = np.zeros((len(onda), 2))
    onda_stereo[:, 0] = onda
    onda_stereo[:, 1] = np.roll(onda, delay) * mix + onda * (1 - mix)

    # normaliza
    onda_stereo = np.clip(onda_stereo * volume, -1, 1)

    return onda_stereo, fs

SONS = {}
for nota, freq in NOTAS_FREQ.items():
    onda, fs = gerar_onda(freq)
    SONS[nota] = (onda, fs)


