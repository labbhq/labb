"""Tests for the block renderer viewer (c-lbb.renderer.viewer)."""

from .test_base import ComponentTestBase


class TestBlockViewerLoading(ComponentTestBase):
    """The preview URL rides in data-lbb-src (loaded via location.replace so it
    never pushes browser history); `lazy` defers the load until the frame is
    scrolled into view."""

    def render_viewer(self, extra_attrs=""):
        return self.render_template_string(
            f"""
{{% load lb_tags %}}
<c-lbb.renderer.viewer
    id="hero"
    slug="hero"
    preview_url="/blocks/marketing/hero/preview/"
    {extra_attrs}
/>
"""
        )

    def test_url_rides_in_data_attr_not_src(self):
        html = self.render_viewer()
        assert 'data-lbb-src="/blocks/marketing/hero/preview/"' in html
        # No `src` at all: the frame starts on its stable empty document and
        # lb-renderer.js navigates it with location.replace() (no history entry,
        # and no about:blank navigation to race the replace). The real URL must
        # never land on `src` (a JS-set src pushes history).
        assert " src=" not in html
        assert "data-attr:src" not in html

    def test_eager_by_default(self):
        html = self.render_viewer()
        assert "data-lbb-lazy" not in html

    def test_lazy_flag_defers_load(self):
        html = self.render_viewer(extra_attrs="lazy")
        assert 'id="pframe-hero"' in html
        assert "data-lbb-lazy" in html
        assert 'data-lbb-src="/blocks/marketing/hero/preview/"' in html

    def test_open_link_still_points_at_preview_when_lazy(self):
        html = self.render_viewer(extra_attrs="lazy")
        assert 'href="/blocks/marketing/hero/preview/"' in html


class TestThumbnailResolution:
    """Thumbnails are captured per theme; older single-file blocks still work."""

    def _meta(self, tmp_path, files, declared=None):
        from labb.contrib.blocks.renderer import configure, views

        block = tmp_path / "auth" / "login" / "thumbnails"
        block.mkdir(parents=True)
        for name in files:
            (block / name).write_bytes(b"png")
        configure({}, tmp_path, "lb")
        meta = {"category": "auth", "slug": "login"}
        if declared:
            meta["thumbnail"] = declared
        return views, meta

    def test_dark_mode_gets_the_dark_capture(self, tmp_path):
        views, meta = self._meta(tmp_path, ["login.light.png", "login.dark.png"])
        assert views._thumbnail_path(meta, "dark").name == "login.dark.png"

    def test_light_is_the_default(self, tmp_path):
        views, meta = self._meta(tmp_path, ["login.light.png", "login.dark.png"])
        assert views._thumbnail_path(meta).name == "login.light.png"

    def test_missing_dark_falls_back_to_light(self, tmp_path):
        views, meta = self._meta(tmp_path, ["login.light.png"])
        assert views._thumbnail_path(meta, "dark").name == "login.light.png"

    def test_pre_split_single_file_still_serves(self, tmp_path):
        views, meta = self._meta(tmp_path, ["login.png"])
        assert views._thumbnail_path(meta, "dark").name == "login.png"

    def test_declared_thumbnail_is_used(self, tmp_path):
        views, meta = self._meta(
            tmp_path, ["custom.png"], declared="thumbnails/custom.png"
        )
        assert views._thumbnail_path(meta, "dark").name == "custom.png"

    def test_declared_path_still_prefers_its_themed_sibling(self, tmp_path):
        # Every block.yaml declares the base name; the themed captures sit beside
        # it, so a manifest written before the split must still resolve them.
        views, meta = self._meta(
            tmp_path,
            ["custom.light.png", "custom.dark.png"],
            declared="thumbnails/custom.png",
        )
        assert views._thumbnail_path(meta, "dark").name == "custom.dark.png"
        assert views._thumbnail_path(meta).name == "custom.light.png"

    def test_nothing_captured_returns_none(self, tmp_path):
        views, meta = self._meta(tmp_path, [])
        assert views._thumbnail_path(meta, "light") is None
