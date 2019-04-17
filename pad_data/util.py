def import_enum_members(E, g):
    for name, value in E.__members__.items():
        assert name not in g
        g[name] = value
