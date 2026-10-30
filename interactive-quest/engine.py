"""Raw game state. No graphics, input recording, or third-party dependencies."""
from dataclasses import dataclass, field
import time


@dataclass
class Rules:
    idle_seconds: float = 10.0
    auto_interval: float = 1.0
    enemy_health: int = 5
    damage: int = 1
    combat_xp: int = 1
    combat_gold: int = 1
    loot_sale_value: int = 1


@dataclass
class Game:
    rules: Rules = field(default_factory=Rules)
    mode: str = "auto"
    location: str = "battle"
    health: int = 5
    xp: int = 0
    gold: int = 0
    loot: int = 0
    kills: int = 0
    actions: int = 0
    stat_points: int = 0
    last_input: float | None = None
    last_auto: float | None = None
    active_quest: dict | None = None

    def __post_init__(self):
        self.health = self.rules.enemy_health

    def input_action(self, now=None):
        now = time.monotonic() if now is None else now
        self.mode = "active"
        self.last_input = now
        self.last_auto = now
        self.action()

    def enable_auto(self, now=None):
        self.mode = "auto"
        self.last_auto = time.monotonic() if now is None else now

    def tick(self, now=None):
        now = time.monotonic() if now is None else now
        if self.mode == "active":
            if self.last_input is None or now - self.last_input < self.rules.idle_seconds:
                return
            self.enable_auto(now)
        if self.last_auto is None:
            self.last_auto = now
        if now - self.last_auto >= self.rules.auto_interval:
            self.action()
            self.last_auto = now

    def action(self):
        self.actions += 1
        if self.location == "market":
            self.gold += self.loot * self.rules.loot_sale_value
            self.loot = 0
            self.location = "battle"
            return
        self.health -= self.rules.damage
        if self.health <= 0:
            self.kills += 1
            self.xp += self.rules.combat_xp
            self.gold += self.rules.combat_gold
            self.loot += 1
            if self.mode == "active" and self.active_quest is not None:
                self.active_quest["progress"] += 1
            self.health = self.rules.enemy_health
            self.location = "market"

    def start_quest(self, definition):
        """Content is supplied later, after quest design is approved."""
        if self.mode != "active":
            raise ValueError("Quests require active play")
        if self.active_quest is not None:
            raise ValueError("A quest is already active")
        self.active_quest = {**definition, "progress": 0}

    def spend_stat_points(self, amount):
        """Guard for future approved stats; no stats or leveling rules yet."""
        if self.mode != "active":
            raise ValueError("Stat points must be spent during active play")
        if amount <= 0 or amount > self.stat_points:
            raise ValueError("Not enough stat points")
        self.stat_points -= amount

    def status(self):
        return (f"{self.mode.upper()} | {self.location} | enemy HP {self.health} | "
                f"XP {self.xp} | gold {self.gold} | loot {self.loot} | "
                f"kills {self.kills} | actions {self.actions}")
