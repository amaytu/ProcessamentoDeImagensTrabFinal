"""
tests.py — Testes unitários para biomechanics e exercise_analyzer.

Execução:
    python tests.py
"""

import numpy as np
from biomechanics import calculate_angle
from exercise_analyzer import ExerciseAnalyzer


def test_calculate_angle():
    """Valida calculate_angle com triângulos conhecidos."""
    print("=== Testes de calculate_angle ===\n")

                                        
    a = np.array([0, 1])
    b = np.array([0, 0])
    c = np.array([1, 0])
    angle = calculate_angle(a, b, c)
    assert abs(angle - 90.0) < 0.1, f"Esperado ~90°, obteve {angle:.2f}°"
    print(f"  [OK] Ângulo reto:       {angle:.2f}° (esperado: 90°)")

                              
    a = np.array([-1, 0])
    b = np.array([0, 0])
    c = np.array([1, 0])
    angle = calculate_angle(a, b, c)
    assert abs(angle - 180.0) < 0.1, f"Esperado ~180°, obteve {angle:.2f}°"
    print(f"  [OK] Ângulo raso:       {angle:.2f}° (esperado: 180°)")

                                              
    a = np.array([1, 0])
    b = np.array([0, 0])
    c = np.array([2, 0])
    angle = calculate_angle(a, b, c)
    assert abs(angle - 0.0) < 0.1, f"Esperado ~0°, obteve {angle:.2f}°"
    print(f"  [OK] Ângulo zero:       {angle:.2f}° (esperado: 0°)")

                    
    a = np.array([0, 1])
    b = np.array([0, 0])
    c = np.array([1, 1])
    angle = calculate_angle(a, b, c)
    assert abs(angle - 45.0) < 0.1, f"Esperado ~45°, obteve {angle:.2f}°"
    print(f"  [OK] Ângulo 45°:        {angle:.2f}° (esperado: 45°)")

                                
    a = np.array([1, 0])
    b = np.array([0, 0])
    c = np.array([0.5, np.sqrt(3)/2])
    angle = calculate_angle(a, b, c)
    assert abs(angle - 60.0) < 0.1, f"Esperado ~60°, obteve {angle:.2f}°"
    print(f"  [OK] Ângulo 60°:        {angle:.2f}° (esperado: 60°)")

          
    a = np.array([1, 0])
    b = np.array([0, 0])
    c = np.array([-0.5, np.sqrt(3)/2])
    angle = calculate_angle(a, b, c)
    assert abs(angle - 120.0) < 0.1, f"Esperado ~120°, obteve {angle:.2f}°"
    print(f"  [OK] Ângulo 120°:       {angle:.2f}° (esperado: 120°)")

    print("\n  Todos os testes de ângulo passaram!\n")


def test_state_machine():
    """Valida a máquina de estados com sequências simuladas de ângulos."""
    print("=== Testes da Máquina de Estados ===\n")

    analyzer = ExerciseAnalyzer(
        concentric_threshold=40.0,
        eccentric_threshold=160.0,
        cheat_threshold=150.0,
        alert_hold_frames=5,
    )

                    
    assert analyzer.state == "IDLE"
    assert analyzer.reps == 0
    print("  [OK] Estado inicial: IDLE, reps=0")

                                           
    result = analyzer.update(165.0)
    assert result["state"] == "ECCENTRIC"
    print(f"  [OK] 165 -> estado={result['state']}")

                                              
    result = analyzer.update(35.0)
    assert result["state"] == "CONCENTRIC"
    assert result["reps"] == 0                         
    print(f"  [OK] 35  -> estado={result['state']}, reps={result['reps']}")

                                                
    result = analyzer.update(170.0)
    assert result["state"] == "ECCENTRIC"
    assert result["reps"] == 1
    print(f"  [OK] 170 -> estado={result['state']}, reps={result['reps']} (rep contada!)")

                                
    analyzer.update(35.0)
    result = analyzer.update(165.0)
    assert result["reps"] == 2
    print(f"  [OK] Ciclo completo -> reps={result['reps']}")

                                                    
    analyzer.reset()
    analyzer.update(165.0)                            

                                                                               
    analyzer._max_angle_in_eccentric = 130.0

    result = analyzer.update(35.0)             
    assert result["amplitude_alert"] is True
    print(f"  [OK] Amplitude encurtada detectada (max_angle=130° < 150°)")

                                                 
    for i in range(4):
        result = analyzer.update(100.0)
        assert result["amplitude_alert"] is True
    result = analyzer.update(100.0)
    assert result["amplitude_alert"] is False
    print(f"  [OK] Alerta expirou após {analyzer.alert_hold_frames} frames")

    print("\n  Todos os testes da máquina de estados passaram!\n")


if __name__ == "__main__":
    test_calculate_angle()
    test_state_machine()
    print("=" * 50)
    print("TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 50)
