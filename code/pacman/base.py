from dataclasses import dataclass

@dataclass
class vec2:
    x: int
    y: int

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

def clamp(lb, v, ub):
    return min(max(lb, v), ub)

def in_between(lb, v, ub) -> bool:
    return lb <= v < ub;
