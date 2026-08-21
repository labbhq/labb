"""A group's nav label comes from `_meta.yaml`, not from title-casing the folder.

Pages have always named themselves through frontmatter `title`. Folders had no
equivalent, so the parser title-cased the directory name and mangled acronyms
("building_uis" became "Building Uis"). `_meta.yaml` is the directory's
frontmatter, and it deliberately adds no route.

Run with: manage.py test labbdocs
"""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from ..doc_parser import DocParser


def _parser(content_path, build_path):
    return DocParser(
        name="guide",
        content_path=content_path,
        build_path=build_path,
        template_dir="labbdocs/docs/guide/",
        url_prefix="/docs/guide",
        yaml_output_path=str(Path(build_path) / "guide.yaml"),
    )


def _titles(menu):
    """Top-level group labels from a built menu structure."""
    out = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            if node.get("children"):
                out.append(node.get("title"))

    walk(menu)
    return out


class GroupTitleTests(SimpleTestCase):
    def _build(self, meta_yaml):
        tmp = tempfile.mkdtemp()
        content = Path(tmp) / "content" / "guide"
        group = content / "2_building_uis"
        group.mkdir(parents=True)
        (group / "1_composition.md").write_text(
            "---\ntitle: Composition\n---\n\nBody.\n"
        )
        if meta_yaml is not None:
            (group / "_meta.yaml").write_text(meta_yaml)

        build = Path(tmp) / "build"
        build.mkdir()
        parser = _parser(str(content), str(build))
        # create_menu_structure returns {menu, pages, navigation, doc_name}
        return _titles(parser.create_menu_structure()["menu"])

    def test_meta_yaml_names_the_group(self):
        assert self._build("title: Building UIs\n") == ["Building UIs"]

    def test_without_meta_the_folder_name_is_used(self):
        # the old behaviour, kept as a fallback and visibly worse
        assert self._build(None) == ["Building Uis"]

    def test_a_meta_without_a_title_falls_back(self):
        assert self._build("description: no title here\n") == ["Building Uis"]

    def test_malformed_meta_does_not_break_the_build(self):
        assert self._build("title: [unclosed\n") == ["Building Uis"]


class RealGuideGroupTests(SimpleTestCase):
    def test_every_guide_group_declares_its_label(self):
        """Each group carries a _meta.yaml, so no label is a title-cased guess."""
        from ..doc_parser import CONTENT_BASE_PATH

        guide = Path(CONTENT_BASE_PATH) / "guide"
        groups = [
            d for d in guide.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        assert groups, "no guide groups found"
        missing = [d.name for d in groups if not (d / "_meta.yaml").is_file()]
        assert not missing, f"groups without _meta.yaml: {missing}"

    def test_a_group_meta_does_not_create_a_page(self):
        """_meta.yaml is metadata, not content: it must not become a route."""
        from ..doc_parser import CONTENT_BASE_PATH

        guide = Path(CONTENT_BASE_PATH) / "guide"
        assert not list(guide.rglob("_meta.md")), "_meta must not be markdown"
