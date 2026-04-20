

(function () {
    'use strict';

    // DaisyUI CSS variable names — resolved via getComputedStyle at render time
    var LB_CSS_VARS = {
        primary:              '--color-primary',
        'primary-content':    '--color-primary-content',
        secondary:            '--color-secondary',
        'secondary-content':  '--color-secondary-content',
        accent:               '--color-accent',
        'accent-content':     '--color-accent-content',
        neutral:              '--color-neutral',
        'neutral-content':    '--color-neutral-content',
        info:                 '--color-info',
        'info-content':       '--color-info-content',
        success:              '--color-success',
        'success-content':    '--color-success-content',
        warning:              '--color-warning',
        'warning-content':    '--color-warning-content',
        error:                '--color-error',
        'error-content':      '--color-error-content',
        'base-100':           '--color-base-100',
        'base-200':           '--color-base-200',
        'base-300':           '--color-base-300',
        'base-content':       '--color-base-content',
    };

    // DaisyUI palette used to auto-colour datasets/slices without explicit colours.
    // Cycles: primary → secondary → accent → info → success → warning → error
    var LB_PALETTE = [
        '--color-primary',
        '--color-secondary',
        '--color-accent',
        '--color-info',
        '--color-success',
        '--color-warning',
        '--color-error',
    ];

    // Alpha applied to *-light colour variants (e.g. 'primary-light').
    // Override globally via `window.lbChartConfig.lightAlpha`.
    var LB_ALPHA_LIGHT_DEFAULT = 0.4;

    function lbAlpha() {
        var v = window.lbChartConfig && window.lbChartConfig.lightAlpha;
        return (typeof v === 'number') ? v : LB_ALPHA_LIGHT_DEFAULT;
    }

    function lbReadCSSVar(varName) {
        var val = getComputedStyle(document.documentElement)
            .getPropertyValue(varName).trim();
        if (!val) return '';
        // DaisyUI 5 may expose channel-only values (e.g. "49% 0.31 275").
        // Canvas needs a full CSS color string — wrap with oklch() if needed.
        if (/^(oklch|rgb|hsl|#|color|lab|lch)/i.test(val)) return val;
        return 'oklch(' + val + ')';
    }

    // Like lbReadCSSVar but applies an alpha component to the resolved colour.
    function lbReadCSSVarWithAlpha(varName, alpha) {
        var val = getComputedStyle(document.documentElement)
            .getPropertyValue(varName).trim();
        if (!val) return '';
        if (/^oklch\(/i.test(val)) {
            // Full oklch(...) — insert alpha before closing paren
            return val.replace(/\)$/, ' / ' + alpha + ')');
        }
        if (/^(rgb|hsl|#|color|lab|lch)/i.test(val)) {
            // Non-oklch full colour — use color-mix() for broad format support
            var pct = Math.round((1 - alpha) * 100);
            return 'color-mix(in oklch, ' + val + ', transparent ' + pct + '%)';
        }
        // DaisyUI 5 channel-only: "49% 0.31 275"
        return 'oklch(' + val + ' / ' + alpha + ')';
    }

    // Resolve a single colour value:
    //   'primary'       → live --color-primary CSS value
    //   'primary-light' → live --color-primary at 20% alpha
    //   '--color-x'     → live CSS value of that var
    //   'red-light'     → color-mix(in oklch, red, transparent 80%)
    //   anything else (hex, rgb, oklch string) → pass through unchanged
    function lbResolve(val) {
        if (!val) return null;
        if (typeof val !== 'string') return val;

        var isLight = val.length > 6 && val.slice(-6) === '-light';
        var base    = isLight ? val.slice(0, -6) : val;

        if (LB_CSS_VARS[base]) {
            if (isLight) return lbReadCSSVarWithAlpha(LB_CSS_VARS[base], lbAlpha());
            return lbReadCSSVar(LB_CSS_VARS[base]);
        }
        if (base.startsWith('--')) {
            if (isLight) return lbReadCSSVarWithAlpha(base, lbAlpha());
            return lbReadCSSVar(base);
        }
        // Raw colour (hex, rgb, oklch literal, CSS named colour, etc.)
        if (isLight) {
            var mixPct = Math.round((1 - lbAlpha()) * 100);
            return 'color-mix(in oklch, ' + base + ', transparent ' + mixPct + '%)';
        }
        return val;
    }

    function lbResolveColor(val) {
        if (Array.isArray(val)) {
            return val.map(function (c) { return lbResolve(c) || c; });
        }
        return lbResolve(val);
    }

    var POLAR_TYPES = ['pie', 'doughnut', 'polarArea'];

    // polarArea + radar use `*-light` fills so overlapping data stays readable;
    // pie, doughnut, bar, line, etc. stay solid.
    function lbDefaultBg(type, varName) {
        if (type === 'polarArea' || type === 'radar') return lbReadCSSVarWithAlpha(varName, lbAlpha());
        return lbReadCSSVar(varName);
    }

    var LabbDaisyUIPlugin = {
        id: 'labbDaisyUI',

        // beforeInit runs once per chart creation, before Chart.js's update cycle.
        // Safe to mutate chart.config.data here — the update/invalidation system
        // has not started yet, so no recursive _invalidate() calls occur.
        beforeInit: function (chart) {
            var type = chart.config.type;
            var isPolar = POLAR_TYPES.indexOf(type) !== -1;
            var datasets = chart.config.data && chart.config.data.datasets;
            var labels   = (chart.config.data && chart.config.data.labels) || [];

            if (!datasets) return;

            datasets.forEach(function (ds, i) {
                // ── backgroundColor ──────────────────────────────────────────
                if (ds.backgroundColor === undefined || ds.backgroundColor === null || ds.backgroundColor === '') {
                    if (isPolar) {
                        // Polar types need one colour per slice
                        ds.backgroundColor = labels.map(function (_, j) {
                            return lbDefaultBg(type, LB_PALETTE[j % LB_PALETTE.length]);
                        });
                        // If no labels yet, fall back to single palette colour
                        if (labels.length === 0) {
                            ds.backgroundColor = lbDefaultBg(type, LB_PALETTE[i % LB_PALETTE.length]);
                        }
                    } else {
                        ds.backgroundColor = lbDefaultBg(type, LB_PALETTE[i % LB_PALETTE.length]);
                    }
                } else {
                    ds.backgroundColor = lbResolveColor(ds.backgroundColor);
                }

                // ── borderColor ───────────────────────────────────────────────
                if (ds.borderColor === undefined || ds.borderColor === null || ds.borderColor === '') {
                    if (type === 'polarArea') {
                        // Solid per-slice border over the translucent fill.
                        ds.borderColor = labels.map(function (_, j) {
                            return lbReadCSSVar(LB_PALETTE[j % LB_PALETTE.length]);
                        });
                        if (labels.length === 0) {
                            ds.borderColor = lbReadCSSVar(LB_PALETTE[i % LB_PALETTE.length]);
                        }
                    } else if (!isPolar) {
                        ds.borderColor = lbReadCSSVar(LB_PALETTE[i % LB_PALETTE.length]);
                    }
                } else {
                    ds.borderColor = lbResolveColor(ds.borderColor);
                }

                // ── hover colors ──────────────────────────────────────────────
                // Set explicitly to prevent Chart.js from running getHoverColor()
                // which uses @kurkle/color — a library that can't parse oklch()
                // values and falls back to black.
                if (ds.hoverBackgroundColor === undefined || ds.hoverBackgroundColor === null || ds.hoverBackgroundColor === '') {
                    ds.hoverBackgroundColor = ds.backgroundColor;
                }
                if (ds.hoverBorderColor === undefined || ds.hoverBorderColor === null || ds.hoverBorderColor === '') {
                    ds.hoverBorderColor = ds.borderColor;
                }
            });
        },
    };

    // Self-register so every new Chart() call gets DaisyUI theming automatically.
    // chart-core.min.js loads before this file (alphabetical sort: c < l), so
    // Chart is always defined here.
    if (typeof Chart !== 'undefined' && Chart.register) {
        Chart.register(LabbDaisyUIPlugin);
    }

    // Expose for any external code that needs a reference to the plugin.
    window.LabbDaisyUIPlugin = LabbDaisyUIPlugin;
}());
