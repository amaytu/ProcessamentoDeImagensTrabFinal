# Especificação de Requisitos e Organização do Projeto: Análise Biomecânica de Rosca Direta

Este documento consolida a especificação técnica, requisitos funcionais e não funcionais, arquitetura de software, stack tecnológica, e referências acadêmicas para o projeto de **Análise Biomecânica de Rosca Direta**. O projeto foi estruturado em conformidade com as diretrizes da disciplina de **Processamento de Imagens** da **FURB (Universidade Regional de Blumenau)**, ministrada pelo **Prof. Aurélio Hoppe**.

---

## 1. Contexto e Objetivo do Projeto

O objetivo deste projeto é desenvolver uma ferramenta de visão computacional em tempo real que auxilie na correta execução do exercício **Rosca Direta (biceps curl)**, monitorando a biomecânica do movimento do braço (esquerdo ou direito) do praticante.

Baseado nas diretrizes do trabalho final da disciplina (conforme roteiro acadêmico), o projeto se enquadra na categoria de **análise de movimentação corporal**. Ele utiliza um modelo consolidado de estimativa de pose (MediaPipe Pose/BlazePose) para derivar dados biomecânicos qualitativos (amplitude de movimento e fases de contração/alongamento) e quantitativos (contagem de repetições válidas), visando maximizar o estímulo de tensão mecânica e alertar sobre execuções com amplitude inadequada (comummente referidas como "roubo").

---

## 2. Requisitos do Sistema

### 2.1 Requisitos Funcionais (RF)

| ID | Requisito | Descrição | Status no Código |
| :--- | :--- | :--- | :--- |
| **RF001** | Seleção de Fonte de Vídeo | O sistema deve aceitar como entrada tanto uma transmissão de vídeo em tempo real (Webcam) quanto arquivos de vídeo pré-gravados (ex.: `.mp4`). | Implementado (`main.py` via `--source`) |
| **RF002** | Seleção de Membro Analisado | O usuário deve ser capaz de selecionar qual braço (esquerdo ou direito) deseja analisar durante a execução. | Implementado (`main.py` via `--arm`) |
| **RF003** | Estimativa de Pose Corporal | O sistema deve detectar de forma contínua a pose do usuário a partir dos frames de vídeo, localizando pontos de interesse (*landmarks*) do ombro, cotovelo e pulso. | Implementado (`main.py` via `PoseLandmarker`) |
| **RF004** | Cálculo Angular Biomecânico | O sistema deve calcular recursivamente o ângulo interno do cotovelo formado pelos segmentos de reta Ombro-Cotovelo e Pulso-Cotovelo. | Implementado (`biomechanics.py` via `calculate_angle`) |
| **RF005** | Máquina de Estados de Repetição | O sistema deve discernir as fases do exercício: **Idle** (início), **Excêntrica** (alongamento/descida) e **Concêntrica** (contração/subida) com base nos limiares de graus definidos. | Implementado (`exercise_analyzer.py`) |
| **RF006** | Contagem de Repetições | Uma repetição só será incrementada quando o usuário concluir um ciclo biomecânico completo: Extensão Completa ($\ge 160^\circ$) $\rightarrow$ Contração Completa ($\le 40^\circ$) $\rightarrow$ Extensão Completa ($\ge 160^\circ$). | Implementado (`exercise_analyzer.py`) |
| **RF007** | Detecção de Amplitude Insuficiente | O sistema deve identificar caso o usuário realize a fase de contração sem ter estendido previamente o braço de forma satisfatória ($< 150^\circ$), caracterizando "roubo" por amplitude reduzida. | Implementado (`exercise_analyzer.py`) |
| **RF008** | Interface Gráfica / HUD | Exibição em tempo real do frame processado contendo o esqueleto sobreposto, ângulo do cotovelo em tempo real, contador de repetições, fase atual, barra de progresso do movimento e banner piscante de alerta. | Implementado (`hud_renderer.py`) |
| **RF009** | Controle do Fluxo de Execução | O usuário deve ser capaz de resetar a contagem de repetições instantaneamente (tecla `r`) ou fechar a aplicação (tecla `q`). | Implementado (`main.py`) |

### 2.2 Requisitos Não Funcionais (RNF)

| ID | Requisito | Descrição | Critério de Aceitação / Abordagem |
| :--- | :--- | :--- | :--- |
| **RNF001** | Desempenho em Tempo Real | O processamento dos frames e a inferência de pose devem ocorrer a uma taxa fluida ($\ge 30\text{ FPS}$) em hardware de consumo geral (CPU). | Uso do MediaPipe Tasks API no modo `VIDEO`, otimizando a latência do pipeline em relação ao modo de imagem estática. |
| **RNF002** | Estabilidade Matemática | Os cálculos angulares das articulações não devem apresentar singularidades ou instabilidade numérica próximas a $0^\circ$ e $180^\circ$. | Uso da função `arctan2` sobre o produto vetorial e escalar 2D, em detrimento do `arccos(dot / (mag1 * mag2))` que possui derivadas tendendo a infinito nos extremos. |
| **RNF003** | Modularidade de Código | A lógica de cálculos vetoriais, máquina de estados e renderização visual devem ser desacopladas para facilitar testes e manutenção. | Divisão em módulos específicos: `biomechanics.py`, `exercise_analyzer.py`, `hud_renderer.py`, e script condutor `main.py`. |
| **RNF004** | Portabilidade e Suporte | O sistema deve rodar de forma nativa em plataformas populares (Windows, Linux, macOS) utilizando o ecossistema Python padrão. | Limitação de dependências a pacotes multiplataforma universais (`opencv-python`, `mediapipe`, `numpy`). |
| **RNF005** | Testabilidade | O sistema deve conter testes automatizados para verificar a consistência matemática do cálculo de ângulos e a corretude das transições da máquina de estados. | Implementação de baterias de testes unitários autoexecutáveis em `tests.py`. |

---

## 3. Ferramentas e Bibliotecas Utilizadas

A pilha de tecnologias foi escolhida com base na simplicidade de integração, eficiência computacional em tempo real e ampla aceitação na comunidade acadêmica e de desenvolvimento:

1. **Linguagem: Python (v3.10+)**
   - Escolhida pela rapidez no desenvolvimento, robustez das bibliotecas científicas e compatibilidade com MediaPipe.
2. **Biblioteca de Visão Computacional: OpenCV (opencv-python >= 4.8.0)**
   - Utilizada para manipulação de fluxos de vídeo, abertura de periféricos de captura (webcam), conversão de espaços de cores (BGR para RGB/cinza) e renderização primitiva do HUD (desenho de linhas, círculos e texto com suavização anti-aliasing).
3. **Framework de Machine Learning: MediaPipe (mediapipe >= 0.10.0)**
   - Utiliza a API `PoseLandmarker` da suite do Google. O MediaPipe fornece um modelo leve (BlazePose) capaz de predizer 33 landmarks corporais 3D a partir de um único frame, operando em tempo real diretamente em CPU, dispensando a necessidade de placas de vídeo dedicadas (GPUs) pesadas para a inferência local.
4. **Processamento Numérico: NumPy (numpy >= 1.24.0)**
   - Utilizado para vetorização dos pontos espaciais obtidos pelo MediaPipe, cálculo de produto escalar e vetorial 2D e conversão de radianos para graus de forma veloz.

---

## 4. Artigos Científicos e Referências Acadêmicas

Para fundamentar teoricamente a solução perante a banca acadêmica e guiar melhorias no algoritmo, os seguintes artigos e referências teóricas são utilizados como base:

### 4.1 Estimativa de Pose e Visão Computacional
*   **BlazePose: On-device Real-time Body Pose tracking**
    *   *Autores:* Valentin Bazarevsky, Ivan Grishchenko, Karthik Raveendran, Tyler Zhu, Fangfang Zhang, Matthias Grundmann (Google Research, 2020).
    *   *Relevância:* Este artigo descreve a arquitetura por trás do detector de pose do MediaPipe. Explica como o modelo alcança altíssima performance em dispositivos móveis e CPUs através de uma arquitetura leve baseada em encoder-decoder com predição de calor (heatmap) e regressão de coordenadas.
    *   *Link/Ref:* [arXiv:2006.10204](https://arxiv.org/abs/2006.10204)
*   **MediaPipe: A Framework for Building Perception Pipelines**
    *   *Autores:* Camillo Lugaresi et al. (Google Research, 2019).
    *   *Relevância:* Apresenta a arquitetura de grafos utilizada para criar pipelines de processamento de mídia (como fluxo de câmera $\rightarrow$ decodificação $\rightarrow$ inferência de IA $\rightarrow$ desenho de HUD).
    *   *Link/Ref:* [arXiv:1906.08172](https://arxiv.org/abs/1906.08172)

### 4.2 Biomecânica, Cinesiologia e Educação Física
*   **The Mechanisms of Muscle Hypertrophy and Their Application to Resistance Training**
    *   *Autor:* Brad J. Schoenfeld (2010).
    *   *Relevância:* Artigo de referência mundial que explica a importância da **tensão mecânica** e do **dano muscular** para o ganho de massa muscular (hipertrofia). Fundamenta cientificamente a escolha de monitorar a amplitude de movimento (ROM - Range of Motion) no exercício de rosca direta, justificando o porquê de alertar o usuário quando a amplitude é reduzida (impedindo o alongamento total sob carga).
    *   *Link/Ref:* *Journal of Strength and Conditioning Research*, 24(10), 2857-2872.
*   **Effect of range of motion on muscle hypertrophy and strength**
    *   *Autores:* Valenzuela, T., et al. (Estudos acumulados sobre ROM).
    *   *Relevância:* Discute como o treino com amplitude parcial na porção encurtada do movimento (iniciar a subida antes de esticar o braço totalmente) gera resultados inferiores comparado ao treino com amplitude total, validando a regra do software que desconsidera ou acusa "amplitude insuficiente" quando a descida é cortada antes de $150^\circ$.

---

## 5. Cronograma de Acompanhamento (Checkpoints FURB)

De acordo com o roteiro de elaboração do Trabalho Final definido pelo **Prof. Aurélio Hoppe**, os marcos do projeto são organizados no seguinte cronograma:

1.  **Definição do problema e base de imagens / escopo (15/05)**
    *   *Status:* **Concluído**. Escopo definido para análise biomecânica do exercício de rosca direta corporal e uso do MediaPipe.
2.  **Apresentação de resultados iniciais e evoluções (29/05)**
    *   *Status:* **Concluído**. Protótipo funcional com cálculo de ângulos 2D, máquina de estados e HUD renderizado com sucesso. Testes automatizados rodando.
3.  **Apresentação parcial do relatório + desenvolvimento (12/06)**
    *   *Status:* **Planejado**. Escrita do relatório científico acadêmico de 2 a 6 páginas. Refinamento de bugs visuais no HUD.
4.  **Entrega Final e Defesa do Trabalho (26/06/2026)**
    *   *Status:* **Planejado**. Entrega do código-fonte completo junto ao relatório definitivo em PDF. Apresentação e defesa individual/equipe perante o professor.
