"""
main.py — Entry point e loop principal de captura/análise.

Orquestra: captura de vídeo (webcam ou arquivo) → MediaPipe PoseLandmarker
(Task API) → cálculo biomecânico → análise de exercício → renderização do HUD.

Uso:
    py main.py                      # webcam, braço direito
    py main.py --source video.mp4   # arquivo de vídeo
    py main.py --arm left           # braço esquerdo
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import cv2
import mediapipe as mp
import numpy as np

from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    PoseLandmarker,
    PoseLandmarkerOptions,
    PoseLandmark,
    RunningMode,
)

from biomechanics import calculate_angle, extract_landmark_coords
from exercise_analyzer import ExerciseAnalyzer
from hud_renderer import draw_hud


# ── Landmark indices por braço ──────────────────────────────────────────────
ARM_LANDMARKS = {
    "right": {
        "shoulder": PoseLandmark.RIGHT_SHOULDER,
        "elbow": PoseLandmark.RIGHT_ELBOW,
        "wrist": PoseLandmark.RIGHT_WRIST,
    },
    "left": {
        "shoulder": PoseLandmark.LEFT_SHOULDER,
        "elbow": PoseLandmark.LEFT_ELBOW,
        "wrist": PoseLandmark.LEFT_WRIST,
    },
}

# ── Configurações de captura ────────────────────────────────────────────────
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720

# ── Caminho do modelo ───────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pose_landmarker_lite.task")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analise biomecânica de rosca direta (biceps) via MediaPipe Pose.",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Fonte de video: '0' para webcam ou caminho para arquivo .mp4 (default: 0).",
    )
    parser.add_argument(
        "--arm",
        type=str,
        choices=["left", "right"],
        default="right",
        help="Braco a ser analisado (default: right).",
    )
    return parser.parse_args()


def create_capture(source: str) -> cv2.VideoCapture:
    """Cria e configura o VideoCapture para webcam ou arquivo."""
    try:
        src = int(source)
    except ValueError:
        src = source

    cap = cv2.VideoCapture(src)

    if not cap.isOpened():
        print(f"[ERRO] Nao foi possivel abrir a fonte de video: {source}")
        sys.exit(1)

    if isinstance(src, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

    return cap


def main() -> None:
    args = parse_args()

    # ── Validar modelo ──────────────────────────────────────────────────────
    if not os.path.isfile(MODEL_PATH):
        print(f"[ERRO] Modelo nao encontrado: {MODEL_PATH}")
        print("[INFO] Baixe de: https://storage.googleapis.com/mediapipe-models/"
              "pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task")
        sys.exit(1)

    # ── Inicialização ───────────────────────────────────────────────────────
    cap = create_capture(args.source)
    analyzer = ExerciseAnalyzer()
    landmarks_cfg = ARM_LANDMARKS[args.arm]

    # Configurar PoseLandmarker (Task API — VIDEO mode para arquivos, IMAGE para frames)
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    landmarker = PoseLandmarker.create_from_options(options)

    # ── Variáveis de controle ───────────────────────────────────────────────
    frame_count = 0
    prev_time = time.perf_counter()
    fps = 0.0
    timestamp_ms = 0

    window_name = f"Rosca Direta - Braco {'Direito' if args.arm == 'right' else 'Esquerdo'}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print(f"[INFO] Fonte: {'Webcam' if args.source == '0' else args.source}")
    print(f"[INFO] Braco: {'Direito' if args.arm == 'right' else 'Esquerdo'}")
    print(f"[INFO] Pressione 'q' para sair, 'r' para resetar contagem.")

    # ── Loop principal ──────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            if args.source != "0":
                print("[INFO] Fim do video.")
                break
            continue

        frame_count += 1
        timestamp_ms += 33  # ~30fps incremento monotônico

        # Flip horizontal para webcam (efeito espelho)
        if args.source == "0":
            frame = cv2.flip(frame, 1)

        h, w = frame.shape[:2]

        # ── MediaPipe PoseLandmarker ────────────────────────────────────────
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = landmarker.detect_for_video(mp_image, timestamp_ms)

        if results.pose_landmarks and len(results.pose_landmarks) > 0:
            lm = results.pose_landmarks[0]  # primeira pessoa detectada

            # Extrair coordenadas em pixels
            shoulder = extract_landmark_coords(lm, landmarks_cfg["shoulder"], w, h)
            elbow = extract_landmark_coords(lm, landmarks_cfg["elbow"], w, h)
            wrist = extract_landmark_coords(lm, landmarks_cfg["wrist"], w, h)

            # Cálculo biomecânico
            angle = calculate_angle(shoulder, elbow, wrist)

            # Análise de exercício (máquina de estados)
            analysis = analyzer.update(angle)

            # Renderização do HUD
            draw_hud(frame, shoulder, elbow, wrist, analysis, fps, frame_count)
        else:
            cv2.putText(
                frame, "Posicione-se na frente da camera",
                (w // 2 - 250, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA,
            )

        # ── FPS ─────────────────────────────────────────────────────────────
        now = time.perf_counter()
        dt = now - prev_time
        prev_time = now
        fps = 1.0 / dt if dt > 0 else 0.0

        # ── Exibição ────────────────────────────────────────────────────────
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r"):
            analyzer.reset()
            print("[INFO] Contagem resetada.")

    # ── Cleanup ─────────────────────────────────────────────────────────────
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()

    print(f"\n[RESULTADO] Total de repeticoes validas: {analyzer.reps}")


if __name__ == "__main__":
    main()
