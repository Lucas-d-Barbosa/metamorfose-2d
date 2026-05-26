"""
NPC alert state machine.

PATROL → SUSPICIOUS → ALERT → SEARCH → PATROL

Each NPC owns one AlertStateMachine instance.
The scene ticks it every frame with sensor data.
"""

from enum import Enum, auto


class AlertState(Enum):
    PATROL = auto()
    SUSPICIOUS = auto()
    ALERT = auto()
    SEARCH = auto()


# How quickly suspicion fills/drains (units per second)
_FILL_RATES = {
    "sound":   30.0,   # heard a noise in range
    "sight":  100.0,   # direct line of sight to player
}
_DRAIN_RATE = 20.0    # suspicion drains when no stimulus
_SUSPICIOUS_THRESHOLD = 40.0   # suspicion level that triggers SUSPICIOUS
_ALERT_THRESHOLD = 100.0       # suspicion level that triggers ALERT
_SEARCH_DURATION = 6.0         # seconds before returning to PATROL


class AlertStateMachine:
    def __init__(self) -> None:
        self.state = AlertState.PATROL
        self.suspicion: float = 0.0           # 0–100
        self.last_known_pos: tuple | None = None
        self._search_timer: float = 0.0

    # -------------------------------------------------------------------------

    def tick(self, dt: float, *,
             sees_player: bool,
             hears_player: bool,
             player_pos=None) -> AlertState:
        """
        Update state based on sensor readings.
        Returns the (possibly new) AlertState.
        """
        stimulus = 0.0
        if sees_player:
            stimulus = _FILL_RATES["sight"]
            self.last_known_pos = player_pos
        elif hears_player:
            stimulus = _FILL_RATES["sound"]
            if player_pos is not None:
                self.last_known_pos = player_pos

        if stimulus > 0:
            self.suspicion = min(100.0, self.suspicion + stimulus * dt)
        else:
            self.suspicion = max(0.0, self.suspicion - _DRAIN_RATE * dt)

        self._update_state(dt)
        return self.state

    def _update_state(self, dt: float) -> None:
        if self.state == AlertState.PATROL:
            if self.suspicion >= _ALERT_THRESHOLD:
                self._enter(AlertState.ALERT)
            elif self.suspicion >= _SUSPICIOUS_THRESHOLD:
                self._enter(AlertState.SUSPICIOUS)

        elif self.state == AlertState.SUSPICIOUS:
            if self.suspicion >= _ALERT_THRESHOLD:
                self._enter(AlertState.ALERT)
            elif self.suspicion <= 0:
                self._enter(AlertState.PATROL)

        elif self.state == AlertState.ALERT:
            if self.suspicion <= 0:
                self._enter(AlertState.SEARCH)

        elif self.state == AlertState.SEARCH:
            self._search_timer += dt
            if self._search_timer >= _SEARCH_DURATION:
                self.last_known_pos = None
                self._enter(AlertState.PATROL)

    def _enter(self, new_state: AlertState) -> None:
        self.state = new_state
        if new_state == AlertState.SEARCH:
            self._search_timer = 0.0

    # -------------------------------------------------------------------------

    @property
    def suspicion_ratio(self) -> float:
        return self.suspicion / 100.0

    @property
    def color(self) -> tuple[int, int, int]:
        return {
            AlertState.PATROL:     (50, 200, 50),
            AlertState.SUSPICIOUS: (230, 180, 0),
            AlertState.ALERT:      (220, 40, 40),
            AlertState.SEARCH:     (200, 100, 0),
        }[self.state]
