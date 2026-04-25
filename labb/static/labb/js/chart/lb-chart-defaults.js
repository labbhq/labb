// lb-chart-defaults.js — DaisyUI-aligned Chart.js global defaults
//
// Reads window.lbChartConfig (set by <c-lb.chart />) for overrides.
// Re-applies on DaisyUI theme change via MutationObserver.

(function () {
    'use strict';

    function lbCSS(varName) {
        var val = getComputedStyle(document.documentElement)
            .getPropertyValue(varName).trim();
        if (!val) return '';
        // DaisyUI 5 may expose channel-only values (e.g. "27% 0.02 260").
        // Canvas needs a full CSS color string — wrap with oklch() if needed.
        if (/^(oklch|rgb|hsl|#|color|lab|lch)/i.test(val)) return val;
        return 'oklch(' + val + ')';
    }

    // Resolve a colour from a prop value:
    //   "base-content"         → lbCSS('--color-base-content')
    //   "--color-base-content" → lbCSS('--color-base-content')
    //   "#333" / "oklch(...)"  → pass through
    function lbColor(val, fallback) {
        if (!val) return lbCSS(fallback);
        if (val.startsWith('--')) return lbCSS(val);
        if (/^(oklch|rgb|hsl|#|color|lab|lch)/i.test(val)) return val;
        return lbCSS('--color-' + val);
    }

    // Captured once before we ever modify Chart.defaults.animation — lets us
    // restore Chart.js's own full animation config when re-enabling after disable.
    var _defaultAnimation = null;

    function lbApplyDefaults() {
        if (typeof Chart === 'undefined') return;

        // Lazily snapshot Chart.js's built-in animation config before first modification.
        if (_defaultAnimation === null) {
            _defaultAnimation = Chart.defaults.animation;
        }

        // Re-read on every call so theme-change re-applies and timing doesn't matter.
        var cfg = window.lbChartConfig || {};

        var showGrid        = cfg.grid            === true;
        var showAnim        = cfg.animation       !== false;
        var updateAnimation = cfg.updateAnimation !== false;
        var showTips        = cfg.tooltips        !== false;
        var showLegend      = cfg.legend          !== false;
        var fontSize        = parseInt(cfg.fontSize, 10) || 12;

        // Write resolved values back so chart.js Alpine component (and any external
        // code) can read a fully-populated config even if lbChartConfig was partial.
        window.lbChartConfig = {
            color:           cfg.color || 'base-content',
            grid:            showGrid,
            animation:       showAnim,
            updateAnimation: updateAnimation,
            fontSize:        fontSize,
            tooltips:        showTips,
            legend:          showLegend,
            lightAlpha:      (typeof cfg.lightAlpha === 'number') ? cfg.lightAlpha : 0.4,
        };

        var textColor = lbColor(cfg.color, '--color-base-content');

        // ── Typography ──────────────────────────────────────────────────────
        Chart.defaults.font.family = 'inherit';
        Chart.defaults.font.size   = fontSize;

        // ── Animation ────────────────────────────────────────────────────────
        Chart.defaults.animation = showAnim ? _defaultAnimation : false;

        // ── Axis labels + grid lines ─────────────────────────────────────────
        Chart.defaults.color       = textColor;
        Chart.defaults.borderColor = lbCSS('--color-base-300');

        // ── Scales ───────────────────────────────────────────────────────────
        Chart.defaults.scales.linear.grid   = { display: showGrid };
        Chart.defaults.scales.category.grid = { display: showGrid };

        // Radial scale (radar + polarArea): hide rings and spokes by default.
        // Mutate in place — replacing the whole grid/angleLines objects wipes
        // Chart.js internal radial defaults (e.g. grid.circular) and lets
        // cartesian scales bleed through.
        if (Chart.defaults.scales.radialLinear) {
            if (!Chart.defaults.scales.radialLinear.ticks)      Chart.defaults.scales.radialLinear.ticks = {};
            if (!Chart.defaults.scales.radialLinear.grid)       Chart.defaults.scales.radialLinear.grid = {};
            if (!Chart.defaults.scales.radialLinear.angleLines) Chart.defaults.scales.radialLinear.angleLines = {};
            Chart.defaults.scales.radialLinear.ticks.backdropColor = 'transparent';
            Chart.defaults.scales.radialLinear.grid.display        = showGrid;
            Chart.defaults.scales.radialLinear.angleLines.display  = showGrid;
        }

        // polarArea + radar opt back in to rings + spokes (they frame the shape).
        // polarArea also restores the arc border that global arc.borderWidth = 0 hid.
        ['polarArea', 'radar'].forEach(function (t) {
            if (!(Chart.overrides && Chart.overrides[t])) return;
            if (!Chart.overrides[t].scales)              Chart.overrides[t].scales = {};
            if (!Chart.overrides[t].scales.r)            Chart.overrides[t].scales.r = {};
            if (!Chart.overrides[t].scales.r.grid)       Chart.overrides[t].scales.r.grid = {};
            if (!Chart.overrides[t].scales.r.angleLines) Chart.overrides[t].scales.r.angleLines = {};
            Chart.overrides[t].scales.r.grid.display       = true;
            Chart.overrides[t].scales.r.angleLines.display = true;
        });
        if (Chart.overrides && Chart.overrides.polarArea) {
            if (!Chart.overrides.polarArea.elements)     Chart.overrides.polarArea.elements = {};
            if (!Chart.overrides.polarArea.elements.arc) Chart.overrides.polarArea.elements.arc = {};
            Chart.overrides.polarArea.elements.arc.borderWidth = 1;
        }

        // ── Tooltip ──────────────────────────────────────────────────────────
        if (Chart.defaults.plugins.tooltip) {
            Chart.defaults.plugins.tooltip.enabled         = showTips;
            Chart.defaults.plugins.tooltip.backgroundColor = lbCSS('--color-base-200');
            Chart.defaults.plugins.tooltip.titleColor      = lbCSS('--color-base-content');
            Chart.defaults.plugins.tooltip.bodyColor       = lbCSS('--color-base-content');
            Chart.defaults.plugins.tooltip.borderColor     = lbCSS('--color-base-300');
            Chart.defaults.plugins.tooltip.borderWidth     = 1;
            Chart.defaults.plugins.tooltip.cornerRadius    = 8;
            Chart.defaults.plugins.tooltip.padding         = 12;
        }

        // ── Legend ───────────────────────────────────────────────────────────
        if (Chart.defaults.plugins.legend) {
            Chart.defaults.plugins.legend.display          = showLegend;
            Chart.defaults.plugins.legend.labels.color     = textColor;
            Chart.defaults.plugins.legend.labels.boxHeight = 8;
        }

        // ── Arcs (pie / doughnut / polarArea) ────────────────────────────────
        if (Chart.defaults.elements.arc) {
            Chart.defaults.elements.arc.borderWidth = 0;
        }

        // ── Bars ─────────────────────────────────────────────────────────────
        if (Chart.defaults.elements.bar) {
            Chart.defaults.elements.bar.borderRadius = 4;
            Chart.defaults.elements.bar.borderWidth  = 0;
        }

        // ── Lines ─────────────────────────────────────────────────────────────
        if (Chart.defaults.elements.line) {
            Chart.defaults.elements.line.tension     = 0.35;
            Chart.defaults.elements.line.borderWidth = 2;
            Chart.defaults.elements.line.fill        = false;
        }

        // ── Points ────────────────────────────────────────────────────────────
        // Keep hit / hover area generous globally.
        if (Chart.defaults.elements.point) {
            Chart.defaults.elements.point.hoverRadius = 4;
            Chart.defaults.elements.point.hitRadius   = 12;
        }
        // Line: hide points, and show tooltip on nearest x without requiring
        // an exact hit on a point.
        if (Chart.overrides && Chart.overrides.line) {
            if (!Chart.overrides.line.elements) Chart.overrides.line.elements = {};
            if (!Chart.overrides.line.elements.point) Chart.overrides.line.elements.point = {};
            Chart.overrides.line.elements.point.radius = 0;

            Chart.overrides.line.interaction = { mode: 'index', intersect: false };
            if (!Chart.overrides.line.plugins) Chart.overrides.line.plugins = {};
            Chart.overrides.line.plugins.tooltip = Object.assign(
                Chart.overrides.line.plugins.tooltip || {},
                { mode: 'index', intersect: false }
            );
        }
    }

    // Initial getComputedStyle can return empty CSS custom-prop values before the
    // first style pass — retry at DOMContentLoaded/load, and notify live charts.
    function lbApplyAndNotify() {
        lbApplyDefaults();
        document.dispatchEvent(new CustomEvent('lb:chart-defaults-applied'));
    }

    lbApplyAndNotify();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', lbApplyAndNotify);
    }
    window.addEventListener('load', lbApplyAndNotify);

    new MutationObserver(lbApplyAndNotify).observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme'],
    });
}());
