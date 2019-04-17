from .common import Element

def import_enum_members(enum, g):
    for name, value in enum.__members__.items():
        assert name not in g
        g[name] = value

def element_to_color(e):
    color_map = {
        Element.NO_ELEMENT: '',
        Element.FIRE: '1;31',
        Element.WATER: '1;36',
        Element.WOOD: '1;32',
        Element.LIGHT: '1;33',
        Element.DARK: '1;35'
    }
    return f'\x1b[{color_map[e]}m'
