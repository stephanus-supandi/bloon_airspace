"""
BLOON DETERMINISTIC RNG
-----------------------
No global random. No numpy.random. No secrets.
Just a local Random instance seeded once.

"BLOON REPRODUCIBILITY LAW:
 If you seed it today, it flies the same tomorrow."
"""
import random


class BloonRNG:
    """Local, seedable, reproducible RNG. Nothing escapes."""

    def __init__(self, seed: int = 1337):
        self._seed = seed
        self._rng = random.Random(seed)

    @property
    def seed(self) -> int:
        return self._seed

    def reset(self) -> None:
        """Rewind RNG to initial seed. Time travel, basically."""
        self._rng = random.Random(self._seed)

    def reseed(self, seed: int) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq):
        return self._rng.choice(seq)

    def shuffle(self, seq) -> None:
        self._rng.shuffle(seq)

    def random(self) -> float:
        return self._rng.random()