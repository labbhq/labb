from labb.tests.components.test_base import ComponentTestBase


class TestChartConfigProvider(ComponentTestBase):
    """c-lb.chart — page-level config provider, renders no canvas."""

    def test_chart_renders_no_canvas(self):
        """Config provider renders nothing — no canvas element."""
        html = self.render_component("chart")
        assert "<canvas" not in html

    def test_chart_renders_no_visible_elements(self):
        """Config provider produces no visible HTML elements."""
        html = self.render_component("chart")
        # Allow empty or whitespace-only output (script stack tags are removed)
        assert html.strip() == "" or "<div" not in html


class TestChartBarSubComponent(ComponentTestBase):
    """c-lb.chart.bar — bar chart sub-component."""

    def test_bar_renders_canvas(self):
        html = self.render_component("chart.bar")
        assert "<canvas" in html

    def test_bar_wrapper_class(self):
        html = self.render_component("chart.bar")
        assert "lb-chart" in html

    def test_bar_x_data_attribute(self):
        html = self.render_component("chart.bar")
        assert 'x-data="lbChartComp"' in html

    def test_bar_chart_type(self):
        html = self.render_component("chart.bar")
        assert 'data-lb-chart-type="bar"' in html

    def test_bar_default_height(self):
        html = self.render_component("chart.bar")
        assert "height: 300px" in html

    def test_bar_custom_height(self):
        html = self.render_component("chart.bar", height="450")
        assert "height: 450px" in html

    def test_bar_default_legend(self):
        html = self.render_component("chart.bar")
        assert 'data-lb-chart-legend="top"' in html

    def test_bar_legend_positions(self):
        for pos in ["top", "bottom", "left", "right", "none"]:
            html = self.render_component("chart.bar", legend=pos)
            assert f'data-lb-chart-legend="{pos}"' in html

    def test_bar_data_attribute_present(self):
        html = self.render_component("chart.bar")
        assert "data-lb-chart-data" in html

    def test_bar_options_attribute_present(self):
        html = self.render_component("chart.bar")
        assert "data-lb-chart-options" in html

    def test_bar_custom_class(self):
        html = self.render_component("chart.bar", **{"class": "shadow-lg"})
        assert "shadow-lg" in html
        assert "lb-chart" in html

    def test_bar_x_ref_canvas(self):
        html = self.render_component("chart.bar")
        assert 'x-ref="canvas"' in html


class TestChartLineSubComponent(ComponentTestBase):
    """c-lb.chart.line — line chart sub-component."""

    def test_line_renders_canvas(self):
        html = self.render_component("chart.line")
        assert "<canvas" in html

    def test_line_chart_type(self):
        html = self.render_component("chart.line")
        assert 'data-lb-chart-type="line"' in html

    def test_line_default_height(self):
        html = self.render_component("chart.line")
        assert "height: 300px" in html

    def test_line_x_data_attribute(self):
        html = self.render_component("chart.line")
        assert 'x-data="lbChartComp"' in html


class TestChartPieSubComponent(ComponentTestBase):
    """c-lb.chart.pie — pie chart sub-component."""

    def test_pie_renders_canvas(self):
        html = self.render_component("chart.pie")
        assert "<canvas" in html

    def test_pie_chart_type(self):
        html = self.render_component("chart.pie")
        assert 'data-lb-chart-type="pie"' in html

    def test_pie_x_data_attribute(self):
        html = self.render_component("chart.pie")
        assert 'x-data="lbChartComp"' in html


class TestChartDoughnutSubComponent(ComponentTestBase):
    """c-lb.chart.doughnut — doughnut chart sub-component."""

    def test_doughnut_renders_canvas(self):
        html = self.render_component("chart.doughnut")
        assert "<canvas" in html

    def test_doughnut_chart_type(self):
        html = self.render_component("chart.doughnut")
        assert 'data-lb-chart-type="doughnut"' in html

    def test_doughnut_x_data_attribute(self):
        html = self.render_component("chart.doughnut")
        assert 'x-data="lbChartComp"' in html


class TestChartRadarSubComponent(ComponentTestBase):
    """c-lb.chart.radar — radar chart sub-component."""

    def test_radar_renders_canvas(self):
        html = self.render_component("chart.radar")
        assert "<canvas" in html

    def test_radar_chart_type(self):
        html = self.render_component("chart.radar")
        assert 'data-lb-chart-type="radar"' in html

    def test_radar_x_data_attribute(self):
        html = self.render_component("chart.radar")
        assert 'x-data="lbChartComp"' in html


class TestChartPolarAreaSubComponent(ComponentTestBase):
    """c-lb.chart.polar-area — polar area chart sub-component."""

    def test_polar_area_renders_canvas(self):
        html = self.render_component("chart.polar-area")
        assert "<canvas" in html

    def test_polar_area_chart_type(self):
        html = self.render_component("chart.polar-area")
        assert 'data-lb-chart-type="polarArea"' in html

    def test_polar_area_x_data_attribute(self):
        html = self.render_component("chart.polar-area")
        assert 'x-data="lbChartComp"' in html


class TestChartScatterSubComponent(ComponentTestBase):
    """c-lb.chart.scatter — scatter chart sub-component."""

    def test_scatter_renders_canvas(self):
        html = self.render_component("chart.scatter")
        assert "<canvas" in html

    def test_scatter_chart_type(self):
        html = self.render_component("chart.scatter")
        assert 'data-lb-chart-type="scatter"' in html

    def test_scatter_x_data_attribute(self):
        html = self.render_component("chart.scatter")
        assert 'x-data="lbChartComp"' in html

    def test_scatter_default_height(self):
        html = self.render_component("chart.scatter")
        assert "height: 300px" in html

    def test_scatter_wrapper_class(self):
        html = self.render_component("chart.scatter")
        assert "lb-chart" in html


class TestChartBubbleSubComponent(ComponentTestBase):
    """c-lb.chart.bubble — bubble chart sub-component."""

    def test_bubble_renders_canvas(self):
        html = self.render_component("chart.bubble")
        assert "<canvas" in html

    def test_bubble_chart_type(self):
        html = self.render_component("chart.bubble")
        assert 'data-lb-chart-type="bubble"' in html

    def test_bubble_x_data_attribute(self):
        html = self.render_component("chart.bubble")
        assert 'x-data="lbChartComp"' in html

    def test_bubble_default_height(self):
        html = self.render_component("chart.bubble")
        assert "height: 300px" in html

    def test_bubble_wrapper_class(self):
        html = self.render_component("chart.bubble")
        assert "lb-chart" in html
