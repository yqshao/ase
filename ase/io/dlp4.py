""" Read/Write DL_POLY_4 CONFIG files """
from ase.atoms import Atoms
from ase.data import chemical_symbols
from numpy import zeros
from ase.calculators.singlepoint import SinglePointCalculator
__all__ = ['read_dlp4', 'write_dlp4']


def read_dlp4(f):
    """Read a DL_POLY_4 config/revcon file.

    Typically used indirectly through read('filename', atoms, format='dlp4').

    Can be unforgiven with custom chemical element names.
    Please complain to alin@elena.space for bugs."""
    line = f.readline()
    line = f.readline().split()
    levcfg = int(line[0])
    imcon = int(line[1])
    pbc = False
    if imcon > 0:
        pbc = True
    cell = zeros((3, 3))
    if pbc:
        for j in range(3):
            line = f.readline().split()
            for i in range(3):
                try:
                    cell[j, i] = float(line[i])
                except ValueError:
                    raise RuntimeError("error reading cell")
    symbols = []
    positions = []
    velocities = []
    forces = []
    line = f.readline()
    while line:
        symbol = line.split()[0]
        if symbol in chemical_symbols:
            symbols.append(symbol)
        else:
            ns = symbol[0]
            if ns in chemical_symbols:
                symbols.append(ns)
            else:
                ns = symbol[0:2]
                if ns in chemical_symbols:
                    symbols.append(ns)
                else:
                    symbols.append('X')
        x, y, z = f.readline().split()[:3]
        positions.append([float(x), float(y), float(z)])
        if levcfg > 0:
            vx, vy, vz = f.readline().split()[:3]
            velocities.append([float(vx), float(vy), float(vz)])
        if levcfg > 1:
            fx, fy, fz = f.readline().split()[:3]
            forces.append([float(fx), float(fy), float(fz)])
        line = f.readline()

    ats = Atoms(positions=positions,
                symbols=symbols,
                cell=cell,
                pbc=pbc)

    # XXX Fix this once atom labels are a thing.
    if not ats.has('names'):
        ats.new_array('names', symbols, str)
        ats.set_array('names', symbols, str)
    f.readline()
    if levcfg > 0:
        ats.set_velocities(velocities)
    if levcfg > 1:
        ats.set_calculator(SinglePointCalculator(ats, forces=forces))
    return ats

def write_dlp4(f, atoms, levcfg = 0, title = 'CONFIG generated by ASE'):
    """Write a DL_POLY_4 config file.

    Typically used indirectly through write('filename', atoms, format='dlp4').

    Can be unforgiven with custom chemical element names.
    Please complain to alin@elena.space in case of bugs"""

    f.write('{0:72s}\n'.format(title))
    natoms = atoms.get_number_of_atoms()
    imcon = 0
    if all(atoms.pbc):
        imcon = 3
    f.write('{0:10d}{1:10d}{2:10d}\n'.format(levcfg, imcon, natoms))
    if imcon > 0:
        cell = atoms.get_cell()
        for j in range(3):
            f.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(
                cell[j, 0], cell[j, 1], cell[j, 2]))
    vels = []
    forces = []
    if levcfg > 0:
        vels = atoms.get_velocities()
    if levcfg > 1:
        forces = atoms.get_forces()
    for a in atoms:
        f.write("{0:8s}{1:10d}\n{2:20.10f}{3:20.10f}{4:20.10f}\n".format(
            a.symbol, a.index+1, a.x, a.y, a.z))
        if levcfg > 0:
            if vels is None:
                f.write("{0:20.10f}{1:20.10f}{2:20.10f}\n".format(
                    0.0, 0.0, 0.0))
            else:
                f.write("{0:20.10f}{1:20.10f}{2:20.10f}\n".format(
                    vels[a.index, 0], vels[a.index, 1], vels[a.index, 2]))
        if levcfg > 1:
            if forces is None:
                f.write("{0:20.10f}{1:20.10f}{2:20.10f}\n".format(
                    0.0, 0.0, 0.0))
            else:
                f.write("{0:20.10f}{1:20.10f}{2:20.10f}\n".format(
                    forces[a.index, 0], forces[a.index, 1], forces[a.index, 2]))