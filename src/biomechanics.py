
import numpy as np


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
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

    lm = landmarks[landmark_enum]
    return np.array([lm.x * frame_width, lm.y * frame_height], dtype=np.float64)
