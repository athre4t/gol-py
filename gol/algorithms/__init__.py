from .sequential import GameOfLifePure
from .vectorized import GameOfLifeVect
from .parallel import GameOfLifeParallel
from .gpu import GameOfLifeGpu


def get_algorithm(mode: str):
    m = mode.lower()
    if m == 'sequential':
        return GameOfLifePure()
    if m == 'vectorized':
        return GameOfLifeVect()
    if m == 'parallel':
        return GameOfLifeParallel()
    if m == 'gpu':
        return GameOfLifeGpu()
    raise ValueError(f'Unknown algorithm mode: {mode}')
