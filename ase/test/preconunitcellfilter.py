import numpy as np

from ase.build import bulk
from ase.calculators.lj import LennardJones
from ase.optimize.precon import PreconLBFGS
from ase.constraints import UnitCellFilter

cu0 = bulk("Cu") * (2, 2, 2)
lj = LennardJones(sigma=cu0.get_distance(0,1))

cu = cu0.copy()
cu.set_cell(1.2*cu.get_cell())
cu.set_calculator(lj)

ucf = UnitCellFilter(cu, constant_volume=True)
opt = PreconLBFGS(ucf)
opt.run(fmax=1e-3)

assert abs(np.linalg.det(cu.cell)/np.linalg.det(cu0.cell) - 1.2**3) < 1e-3
