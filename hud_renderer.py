"""
hud_renderer.py — Renderização do HUD e esqueleto sobre o frame.

Responsável por todo desenho visual: skeleton overlay nos braços,
exibição de ângulo, contador de repetições, fase atual, barra de
progresso com cor dinâmica e banner de alerta de amplitude encurtada.
"""

from __future__ import annotations
import cv2
import numpy as np

# Paleta de cores (BGR)
COLORS = {
    "joint": (0, 255, 255),
    "bone": (255, 200, 50),
    "text": (255, 255, 255),
    "text_shadow": (0, 0, 0),
    "bg_panel": (30, 30, 30),
    "bar_good": (0, 220, 100),
    "bar_warn": (0, 180, 255),
    "bar_bad": (0, 0, 255),
    "alert_bg": (0, 0, 180),
    "phase_up": (0, 255, 180),
    "phase_down": (255, 180, 0),
}

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_BOLD = cv2.FONT_HERSHEY_DUPLEX


def _text_shadow(frame, text, org, font=FONT, scale=0.7, color=COLORS["text"], thick=2, offset=2):
    cv2.putText(frame, text, (org[0]+offset, org[1]+offset), font, scale, COLORS["text_shadow"], thick+1, cv2.LINE_AA)
    cv2.putText(frame, text, org, font, scale, color, thick, cv2.LINE_AA)


def _rounded_rect(frame, pt1, pt2, color, alpha=0.7, radius=12):
    overlay = frame.copy()
    x1, y1 = pt1
    x2, y2 = pt2
    cv2.rectangle(overlay, (x1+radius, y1), (x2-radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1+radius), (x2, y2-radius), color, -1)
    cv2.ellipse(overlay, (x1+radius, y1+radius), (radius, radius), 180, 0, 90, color, -1)
    cv2.ellipse(overlay, (x2-radius, y1+radius), (radius, radius), 270, 0, 90, color, -1)
    cv2.ellipse(overlay, (x1+radius, y2-radius), (radius, radius), 90, 0, 90, color, -1)
    cv2.ellipse(overlay, (x2-radius, y2-radius), (radius, radius), 0, 0, 90, color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0, frame)


def draw_skeleton(frame, shoulder, elbow, wrist):
    pts = [tuple(shoulder.astype(int)), tuple(elbow.astype(int)), tuple(wrist.astype(int))]
    for i in range(len(pts)-1):
        cv2.line(frame, pts[i], pts[i+1], COLORS["text_shadow"], 6, cv2.LINE_AA)
        cv2.line(frame, pts[i], pts[i+1], COLORS["bone"], 3, cv2.LINE_AA)
    for pt in pts:
        cv2.circle(frame, pt, 10, COLORS["text_shadow"], -1, cv2.LINE_AA)
        cv2.circle(frame, pt, 7, COLORS["joint"], -1, cv2.LINE_AA)


def draw_angle_label(frame, elbow, angle):
    text = f"{int(angle)} graus"
    ex, ey = int(elbow[0]), int(elbow[1])
    tx, ty = ex + 20, ey - 15
    (tw, th), _ = cv2.getTextSize(text, FONT_BOLD, 0.65, 2)
    pad = 8
    _rounded_rect(frame, (tx-pad, ty-th-pad), (tx+tw+pad, ty+pad), COLORS["bg_panel"], 0.75, 8)
    _text_shadow(frame, text, (tx, ty), FONT_BOLD, 0.65, COLORS["joint"], 2)


def draw_info_panel(frame, reps, phase_label, fps):
    h, w = frame.shape[:2]
    _rounded_rect(frame, (10, 10), (270, 130), COLORS["bg_panel"], 0.80)
    _text_shadow(frame, "REPETICOES", (25, 40), FONT, 0.55, (180, 180, 180), 1)
    _text_shadow(frame, str(reps), (25, 95), FONT_BOLD, 2.0, COLORS["text"], 3)

    pc = COLORS["phase_up"] if "SUBINDO" in phase_label else COLORS["phase_down"]
    if phase_label == "\u2014":
        pc = (120, 120, 120)
    _text_shadow(frame, phase_label, (150, 95), FONT, 0.65, pc, 2)

    fps_text = f"FPS: {int(fps)}"
    (tw, _), _ = cv2.getTextSize(fps_text, FONT, 0.55, 1)
    fx = w - tw - 20
    _rounded_rect(frame, (fx-10, 10), (w-10, 45), COLORS["bg_panel"], 0.75, 8)
    _text_shadow(frame, fps_text, (fx, 35), FONT, 0.55, (180, 220, 255), 1)


def draw_progress_bar(frame, angle, amplitude_alert, bx=40, by=160, bh=300, bw=30):
    norm = np.clip((angle - 30.0) / 150.0, 0.0, 1.0)
    fill_h = int(norm * bh)
    fill_top = by + bh - fill_h

    if amplitude_alert:
        color = COLORS["bar_bad"]
    elif angle >= 150:
        color = COLORS["bar_good"]
    elif angle >= 100:
        color = COLORS["bar_warn"]
    else:
        color = COLORS["bar_bad"]

    _rounded_rect(frame, (bx, by), (bx+bw, by+bh), (60, 60, 60), 0.6, 10)
    if fill_h > 4:
        _rounded_rect(frame, (bx+3, fill_top+2), (bx+bw-3, by+bh-2), color, 0.85, 8)
    _text_shadow(frame, "180", (bx+bw+5, by+15), FONT, 0.4, (150, 150, 150), 1)
    _text_shadow(frame, "30", (bx+bw+5, by+bh), FONT, 0.4, (150, 150, 150), 1)


def draw_amplitude_alert(frame, frame_count):
    h, w = frame.shape[:2]
    pulse = 0.5 + 0.4 * np.sin(frame_count * 0.15)
    bw, bh = 500, 50
    bx = (w - bw) // 2
    by = 140
    _rounded_rect(frame, (bx, by), (bx+bw, by+bh), COLORS["alert_bg"], float(pulse), 12)
    text = "AMPLITUDE INSUFICIENTE!"
    (tw, th), _ = cv2.getTextSize(text, FONT_BOLD, 0.7, 2)
    tx = bx + (bw - tw) // 2
    ty = by + (bh + th) // 2
    cv2.putText(frame, text, (tx, ty), FONT_BOLD, 0.7, COLORS["text"], 2, cv2.LINE_AA)


def draw_hud(frame, shoulder, elbow, wrist, analysis, fps, frame_count):
    """Renderiza todo o HUD sobre o frame. Chamada principal do main.py."""
    draw_skeleton(frame, shoulder, elbow, wrist)
    draw_angle_label(frame, elbow, analysis["angle"])
    draw_info_panel(frame, analysis["reps"], analysis["phase_label"], fps)
    draw_progress_bar(frame, analysis["angle"], analysis["amplitude_alert"])
    if analysis["amplitude_alert"]:
        draw_amplitude_alert(frame, frame_count)
    return frame
