"""Turn a flat {filename: content} mapping into a nested file tree."""


def file_tree(raw_tabs: dict) -> list:
    """
    Convert a {fname: content} mapping into a nested tree of nodes.

    Each node: {"type": "file"|"dir", "name": str, "fname": str|None, "children": list}
    Files are sorted before dirs at each level.

    Usage::

        raw = {"views.py": "...", "templates/pages/index.html": "..."}
        tabs = [{"fname": k, "content": v} for k, v in raw.items()]
        tree = file_tree(raw)
        # pass tabs + tree to c-lbb.renderer.viewer
    """

    def _insert(node, parts, fname):
        head, *tail = parts
        if tail:
            if head not in node or isinstance(node[head], str):
                node[head] = {}
            _insert(node[head], tail, fname)
        else:
            node[head] = fname

    root = {}
    for fname in sorted(raw_tabs.keys()):
        _insert(root, fname.split("/"), fname)

    def _to_nodes(node):
        files = {k: v for k, v in node.items() if isinstance(v, str)}
        dirs = {k: v for k, v in node.items() if isinstance(v, dict)}
        items = []
        for name in sorted(files):
            items.append({"type": "file", "name": name, "fname": files[name]})
        for name in sorted(dirs):
            items.append(
                {
                    "type": "dir",
                    "name": name,
                    "fname": None,
                    "children": _to_nodes(dirs[name]),
                }
            )
        return items

    return _to_nodes(root)
