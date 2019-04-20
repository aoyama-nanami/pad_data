from .common import Orb

def import_enum_members(enum, g):
    for name, value in enum.__members__.items():
        assert name not in g
        g[name] = value

def element_to_color(e):
    color_map = {
        Orb.NO_ORB: '',
        Orb.FIRE: '1;31',
        Orb.WATER: '1;36',
        Orb.WOOD: '1;32',
        Orb.LIGHT: '1;33',
        Orb.DARK: '1;35'
    }
    return f'\x1b[{color_map[e]}m'
