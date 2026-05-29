"""
biomechanics.py — Módulo de cálculo biomecânico puro.

Contém funções vetoriais para determinação de ângulos articulares
a partir de coordenadas 2D de landmarks. Sem dependência de
frameworks de visão computacional — apenas NumPy.
"""

import numpy as np


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Calcula o ângulo no vértice *b* formado pelos segmentos a→b e c→b.

    Utiliza ``arctan2`` sobre o produto vetorial (componente z do cross
    product 2D) e o produto escalar dos vetores BA e BC.  Essa abordagem
    é numericamente mais estável que ``arccos(dot / (|BA|·|BC|))`` nos
    extremos do intervalo (0° e 180°), onde o arco-cosseno sofre de
    perda de precisão por derivada tendendo a infinito.

    Parameters
    ----------
    a : np.ndarray, shape (2,) ou (3,)
        Coordenada do primeiro ponto (ex.: ombro).
    b : np.ndarray, shape (2,) ou (3,)
        Coordenada do vértice (ex.: cotovelo).
    c : np.ndarray, shape (2,) ou (3,)
        Coordenada do terceiro ponto (ex.: pulso).

    Returns
    -------
    float
        Ângulo em graus, no intervalo [0, 180].
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    c = np.asarray(c, dtype=np.float64)

    ba = a - b
    bc = c - b

                                                        
    cross = ba[0] * bc[1] - ba[1] * bc[0]
                                     
    dot = np.dot(ba[:2], bc[:2])

    angle_rad = np.abs(np.arctan2(cross, dot))
    return float(np.degrees(angle_rad))


def extract_landmark_coords(
    landmarks,
    landmark_enum,
    frame_width: int,
    frame_height: int,
) -> np.ndarray:
    """Converte um landmark do MediaPipe (coordenadas normalizadas) para pixels.

    Compatível com a MediaPipe Task API (PoseLandmarker), onde
    ``landmarks`` é uma lista de ``NormalizedLandmark`` e o índice
    é obtido via ``PoseLandmark.VALUE.value``.

    Parameters
    ----------
    landmarks : list[NormalizedLandmark]
        Lista de landmarks retornada por ``results.pose_landmarks[0]``.
    landmark_enum : PoseLandmark
        Enum do landmark (ex.: ``PoseLandmark.RIGHT_ELBOW``).
    frame_width : int
        Largura do frame em pixels.
    frame_height : int
        Altura do frame em pixels.

    Returns
    -------
    np.ndarray, shape (2,)
        Coordenadas ``[x, y]`` em pixels.
    """
    lm = landmarks[landmark_enum]
    return np.array([lm.x * frame_width, lm.y * frame_height], dtype=np.float64)
