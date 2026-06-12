"""
exercise_analyzer.py — Máquina de estados e regras de negócio.

Implementa a lógica de análise de repetições de rosca direta baseada
em tensão mecânica:  a repetição só é validada quando o ciclo completo
de amplitude (extensão → contração → extensão) é executado.
"""

from __future__ import annotations


class ExerciseAnalyzer:
                                                       
    STATE_IDLE = "IDLE"
    STATE_ECCENTRIC = "ECCENTRIC"
    STATE_CONCENTRIC = "CONCENTRIC"

    def __init__(
        self,
        concentric_threshold: float = 40.0,
        eccentric_threshold: float = 160.0,
        cheat_threshold: float = 150.0,
        alert_hold_frames: int = 45,
    ) -> None:
                    
        self.concentric_threshold = concentric_threshold
        self.eccentric_threshold = eccentric_threshold
        self.cheat_threshold = cheat_threshold
        self.alert_hold_frames = alert_hold_frames

                        
        self.state: str = self.STATE_IDLE
        self.reps: int = 0
        self.phase_label: str = "—"
        self.amplitude_alert: bool = False

                                                                    
        self._max_angle_in_eccentric: float = 0.0
                                                          
        self._alert_countdown: int = 0

                                                                               

    def update(self, angle: float) -> dict:
        self._tick_alert()

        if self.state == self.STATE_IDLE:
            self._handle_idle(angle)
        elif self.state == self.STATE_ECCENTRIC:
            self._handle_eccentric(angle)
        elif self.state == self.STATE_CONCENTRIC:
            self._handle_concentric(angle)

        return {
            "state": self.state,
            "reps": self.reps,
            "phase_label": self.phase_label,
            "amplitude_alert": self.amplitude_alert,
            "angle": angle,
        }

    def reset(self) -> None:
        """Reseta completamente o estado do analisador."""
        self.__init__(
            concentric_threshold=self.concentric_threshold,
            eccentric_threshold=self.eccentric_threshold,
            cheat_threshold=self.cheat_threshold,
            alert_hold_frames=self.alert_hold_frames,
        )

                                                                               

    def _handle_idle(self, angle: float) -> None:
        """IDLE → ECCENTRIC quando o braço atinge extensão completa."""
        if angle >= self.eccentric_threshold:
            self.state = self.STATE_ECCENTRIC
            self.phase_label = "DESCENDO ↓"
            self._max_angle_in_eccentric = angle

    def _handle_eccentric(self, angle: float) -> None:
                                   
        if angle > self._max_angle_in_eccentric:
            self._max_angle_in_eccentric = angle

        if angle <= self.concentric_threshold:
                                                                       
            if self._max_angle_in_eccentric < self.cheat_threshold:
                self._fire_alert()

            self.state = self.STATE_CONCENTRIC
            self.phase_label = "SUBINDO ↑"

    def _handle_concentric(self, angle: float) -> None:
        if angle >= self.eccentric_threshold:
            self.reps += 1
            self.state = self.STATE_ECCENTRIC
            self.phase_label = "DESCENDO ↓"
            self._max_angle_in_eccentric = angle

                                                                              

    def _fire_alert(self) -> None:
        """Dispara o alerta de amplitude encurtada."""
        self.amplitude_alert = True
        self._alert_countdown = self.alert_hold_frames

    def _tick_alert(self) -> None:
        """Decrementa o contador do alerta e desativa quando expirado."""
        if self._alert_countdown > 0:
            self._alert_countdown -= 1
            if self._alert_countdown == 0:
                self.amplitude_alert = False
