# Análise Biomecânica de Rosca Direta

Sistema de análise de postura e execução de rosca direta (bíceps) utilizando visão computacional e princípios de tensão mecânica.

## Estrutura do Projeto

```
├── src/                         → Código-fonte do sistema
│   ├── main.py                  → Loop principal + CLI + orquestração
│   ├── biomechanics.py          → Cálculo de ângulo articular (arctan2)
│   ├── exercise_analyzer.py     → Máquina de estados + contagem de reps
│   ├── hud_renderer.py          → HUD visual (esqueleto, ângulo, barra, alertas)
│   ├── tests.py                 → Testes automatizados
│   ├── requirements.txt         → Dependências Python
│   └── pose_landmarker_lite.task → Modelo MediaPipe Pose (BlazePose Lite)
│
├── relatorio/                   → Relatório científico acadêmico
│   └── relatorio.md             → Relatório final (Markdown)
│
├── docs/                        → Documentação e roteiros
│   ├── especificacao_requisitos.md → Especificação de requisitos do projeto
│   └── Roteiro para a elaboração do Trabalho Final - sexta.pdf
│
└── README.md                   → Este arquivo
```

## Stack

- **Python 3.10+**
- **OpenCV** — captura e renderização de vídeo
- **MediaPipe Pose** — estimativa de pose em tempo real (BlazePose)
- **NumPy** — cálculos vetoriais

## Instalação

```bash
cd src
pip install -r requirements.txt
```

## Uso

```bash
# Webcam (braço direito — padrão)
python src/main.py

# Arquivo de vídeo
python src/main.py --source video.mp4

# Braço esquerdo
python src/main.py --arm left

# Combinado
python src/main.py --source video.mp4 --arm left
```

### Controles

| Tecla | Ação |
|-------|------|
| `q`   | Sair |
| `r`   | Resetar contagem de repetições |

## Lógica de Análise

### Ângulo Articular

Calculado via `arctan2` sobre o produto vetorial e escalar dos vetores ombro→cotovelo e pulso→cotovelo. Range: [0°, 180°].

### Fases e Contagem

- **Fase Excêntrica** (extensão): ângulo ≥ 160°
- **Fase Concêntrica** (contração): ângulo ≤ 40°
- **Repetição válida**: ciclo completo extensão → contração → extensão

### Alerta de Amplitude

Se a contração inicia sem extensão prévia ≥ 150°, um banner vermelho pulsante indica amplitude insuficiente ("roubo").

## Testes

```bash
python src/tests.py
```

## Relatório Acadêmico

O relatório científico do trabalho final está disponível em [`relatorio/relatorio.md`](relatorio/relatorio.md).

## Autores

- Gabriel [Sobrenome]
- [Membro 2]
- [Membro 3]

**Disciplina:** Processamento de Imagens — FURB — Prof. Aurélio Hoppe — 2026/1
