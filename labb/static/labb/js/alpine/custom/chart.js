// chart.js — labb Alpine component for Chart.js with DaisyUI theming
//
// ⚠️  This file is hand-written and lives outside the auto-generated
//     alpine/components/ folder so it is never overwritten or cleared.
//     See CUSTOM_COMPONENTS in alpine_components.py — do not remove that entry.

document.addEventListener('alpine:init', function () {
    Alpine.data('lbChartComp', function () {
        // Non-reactive state stored in closure — NOT returned in the object so Alpine
        // never wraps them in its reactive Proxy. Chart.js instances must be kept outside
        // Alpine's Proxy because Chart.js has its own internal proxy/getter system that
        // causes "Maximum call stack size exceeded" when both proxies are nested.
        var _chart    = null;
        var _observer = null;
        var _rawData  = {};
        var _rawOpts  = {};
        var _type     = 'bar';
        var _legend   = 'top';

        return {
            modelValue: null,  // only reactive property — watched via $watch

            init: function () {
                var el = this.$el;
                _type   = el.dataset.lbChartType   || 'bar';
                _legend = el.dataset.lbChartLegend || 'top';
                try { _rawData = JSON.parse(el.dataset.lbChartData    || '{}'); } catch (e) { _rawData = {}; }
                try { _rawOpts = JSON.parse(el.dataset.lbChartOptions || '{}'); } catch (e) { _rawOpts = {}; }

                var self   = this;
                var canvas = this.$refs.canvas;

                _chart = self._buildChart();

                // Reactive model binding — fires when x-model value changes.
                // Deep-clone via JSON to strip Alpine's Proxy wrappers from val
                // before handing data to Chart.js.
                this.$watch('modelValue', function (val) {
                    if (!val || !_chart) return;
                    var snap;
                    try { snap = JSON.parse(JSON.stringify(val)); } catch (e) { return; }

                    if (snap.data !== undefined) {
                        // Store original (unresolved) values so theme rebuilds
                        // always start from semantic colour names, not baked oklch strings.
                        _rawData = JSON.parse(JSON.stringify(snap.data));
                        // Run DaisyUI plugin colour resolution on a working copy
                        // before assigning — beforeInit only fires on new Chart(),
                        // not on in-place updates, so we invoke it manually here.
                        var resolved = JSON.parse(JSON.stringify(snap.data));
                        var plugin = window.LabbDaisyUIPlugin;
                        if (plugin && plugin.beforeInit) {
                            plugin.beforeInit({ config: { type: _type, data: resolved } });
                        }
                        _chart.data.labels   = resolved.labels   || [];
                        _chart.data.datasets = resolved.datasets || [];
                    }
                    if (snap.legend !== undefined) {
                        _legend = snap.legend;
                        _chart.options.plugins.legend.position =
                            snap.legend === 'none' ? false : snap.legend;
                    }
                    if (snap.options !== undefined) {
                        _rawOpts = snap.options;
                        Object.assign(_chart.options, snap.options);
                    }
                    var cfg = window.lbChartConfig || {};
                    _chart.update(cfg.updateAnimation === false ? 'none' : undefined);
                });

                // Theme change — must destroy+recreate, NOT just chart.update().
                // lb-daisy-plugin.js sets dataset colors in Chart.js's beforeInit hook,
                // which only fires on new Chart() construction. A plain chart.update()
                // after a theme switch leaves old colors baked in.
                function rebuild() {
                    if (!_chart) return;
                    _chart.destroy();
                    canvas.removeAttribute('width');
                    canvas.removeAttribute('height');
                    _chart = self._buildChart();
                }

                _observer = new MutationObserver(rebuild);
                _observer.observe(document.documentElement, {
                    attributes: true,
                    attributeFilter: ['data-theme'],
                });

                // Rebuild if lb-chart-defaults re-applies after a cold-start CSS read.
                this._lbRefresh = rebuild;
                document.addEventListener('lb:chart-defaults-applied', this._lbRefresh);
            },

            _buildChart: function () {
                // No cartesian x/y scales for radial charts — radar uses an `r`
                // radial scale, and pie/doughnut/polarArea have their own scale
                // handling. Injecting { x, y } here makes Chart.js draw a
                // cartesian grid on top of the radial chart.
                var isRadial = ['pie', 'doughnut', 'polarArea', 'radar'].includes(_type);
                var data = JSON.parse(JSON.stringify(_rawData));
                var opts = JSON.parse(JSON.stringify(_rawOpts));
                return new window.Chart(this.$refs.canvas, {
                    type: _type,
                    data: data,
                    options: Object.assign(
                        {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: _legend === 'none' ? false : _legend,
                                },
                            },
                            scales: isRadial ? {} : { x: {}, y: {} },
                        },
                        opts
                    ),
                });
            },

            destroy: function () {
                if (_observer) _observer.disconnect();
                if (this._lbRefresh) {
                    document.removeEventListener('lb:chart-defaults-applied', this._lbRefresh);
                }
                if (_chart) _chart.destroy();
            },
        };
    });
});
