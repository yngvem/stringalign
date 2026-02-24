def _indent(string: str, n_spaces: int, skip: int = 0):
    fill = n_spaces * " "
    lines = string.splitlines()
    unindented = lines[:skip]
    indented = (f"{fill}{line}" for line in lines[skip:])
    return "\n".join((*unindented, *indented))
