def import_enum_members(enum, g):
    for name, value in enum.__members__.items():
        assert name not in g
        g[name] = value
