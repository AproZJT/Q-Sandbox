"""内存指标收集器（Milestone 4 Step 3）。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MetricsStore:
    counters: dict[str, int] = field(default_factory=dict)

    def inc(self, key: str, value: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + value

    def snapshot(self) -> dict[str, int]:
        return dict(self.counters)


metrics = MetricsStore()
