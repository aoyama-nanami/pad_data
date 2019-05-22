def post_process(effects):
    out = []
    for e in effects:
        if isinstance(e, list):
            out += e
        else:
            out.append(e)
    return out
