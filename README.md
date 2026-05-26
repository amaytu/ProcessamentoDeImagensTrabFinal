# Análise Biomecânica de Rosca Direta

Sistema de análise de postura e execução de rosca direta (bíceps) utilizando visão computacional e princípios de tensão mecânica.

## Stack

- **Python 3.10+**
- **OpenCV** — captura e renderização de vídeo
- **MediaPipe Pose** — estimativa de pose em tempo real
- **NumPy** — cálculos vetoriais

## Arquitetura

```
main.py               → Loop principal + CLI + orquestração
biomechanics.py        → Cálculo de ângulo articular (arctan2)
exercise_analyzer.py   → Máquina de estados + contagem de reps
hud_renderer.py        → HUD visual (esqueleto, ângulo, barra, alertas)
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Webcam (braço direito — padrão)
python main.py

# Arquivo de vídeo
python main.py --source video.mp4

# Braço esquerdo
python main.py --arm left

# Combinado
python main.py --source video.mp4 --arm left
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
