from pad_data import common

def import_enum_members(enum, g):
    for name, value in enum.__members__.items():
        assert name not in g
        g[name] = value

def element_to_color(e):
    color_map = {
        common.Orb.NO_ORB: '',
        common.Orb.FIRE: '1;31',
        common.Orb.WATER: '1;36',
        common.Orb.WOOD: '1;32',
        common.Orb.LIGHT: '1;33',
        common.Orb.DARK: '1;35'
    }
    return f'\x1b[{color_map[e]}m'
