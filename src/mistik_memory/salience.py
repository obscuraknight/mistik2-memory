from __future__ import annotations

import datetime as _dt
import math


def _parse_time(value):
    if not value:
        return None
    try:
        parsed = _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.timezone.utc)
    return parsed.astimezone(_dt.timezone.utc)


def salience_score(*, importance=0.5, novelty=0.5, emotional_intensity=0.0,
                   access_count=0, occurred_at=None, now=None, half_life_days=90.0):
    """Deterministic, bounded salience score. Decay affects ranking, not retention."""
    for name, value in (("importance", importance), ("novelty", novelty),
                        ("emotional_intensity", emotional_intensity)):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    if type(access_count) is not int or access_count < 0:
        raise ValueError("access_count must be a nonnegative integer")
    if not isinstance(half_life_days, (int, float)) or half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    when = _parse_time(occurred_at)
    now_dt = _parse_time(now) if now else _dt.datetime.now(_dt.timezone.utc)
    if when is None:
        recency = 0.5
    else:
        age_days = max(0.0, (now_dt - when).total_seconds() / 86400.0)
        recency = math.exp(-math.log(2) * age_days / float(half_life_days))
    access = 1.0 - math.exp(-access_count / 5.0)
    score = (0.36 * float(importance) + 0.20 * float(novelty) +
             0.14 * float(emotional_intensity) + 0.18 * recency + 0.12 * access)
    return max(0.0, min(1.0, score))
