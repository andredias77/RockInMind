# Estrutura do Projeto

Este projeto é composto por vários arquivos Python, cada um com uma responsabilidade específica dentro do sistema. Abaixo está a descrição de cada arquivo:

---

## 📁 config.py
Contém:
- A sequência das notas
- A nota e suas respectivas cores
- O tamanho (duração) de cada música

---

## 🎨 gui.py
Responsável por:
- Gerar a interface gráfica
- Orquestrar a lógica principal do sistema
- Integrar os módulos do jogo com a interface

---

## 🎸 guitarra.py
Contém:
- A tabela completa de frequências das notas musicais
- O código responsável por gerar o som da guitarra

---

## 🎮 jogo.py
Implementa:
- A lógica de acerto e erro das jogadas
- O modo de jogo normal
- O modo livre

---

## ▶️ main.py
Arquivo principal do projeto:
- Responsável por iniciar a interface gráfica
- Ponto de entrada da aplicação

---

## 📦 requirements.txt
Contém:
- A lista de dependências necessárias para rodar a interface e o projeto

---

## 🎵 seleciona_musica.py
Responsável por:
- Implementar a lógica de escolha da música a ser tocada

---

## 🔌 serial_thread.py
Responsável por:
- Realizar a comunicação serial com a FPGA
- Gerenciar a leitura e escrita de dados via porta serial

