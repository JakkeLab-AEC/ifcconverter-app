import math

class SimpleVectorUtil:
    def __init__(self):
        pass

    def vector_rotate(self, vector: tuple[float, float], degree: float) -> tuple[float, float]:
        radian = degree * (math.pi/180)
        x = vector[0] * math.cos(radian) - vector[1] * math.sin(radian)
        y = vector[0] * math.sin(radian) + vector[1] * math.cos(radian)
        return x, y

    def vector_normalize(self, vector: tuple[float, float]) -> tuple[float, float]:
        size = math.sqrt(vector[0]**2 + vector[1]**2)
        return vector[0]/size, vector[1]/size

    def vector_add(self, v1: tuple[float, float], v2: tuple[float, float]) -> tuple[float, float]:
        return v1[0] + v2[0], v1[1] + v2[1]

    def vector_subtract(self, v1: tuple[float, float], v2: tuple[float, float]) -> tuple[float, float]:
        return v1[0] - v2[0], v1[1] - v2[1]

    def vector_multiply_scalar(self, vector: tuple[float, float], scalar: float) -> tuple[float, float]:
        return vector[0] * scalar, vector[1] * scalar

    def vector_size(self, vector: tuple[float, float]) -> float:
        return math.sqrt(vector[0]**2 + vector[1]**2)

