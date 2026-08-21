// chart-ds.js — Datastar port of the labb Chart.js Alpine component.
//
// Two entry points:
//   lbChart.handle(el, signalData) — for reactive charts ($signal:fallback prop).
//     Called via data-effect="lbChart.handle(el, $chartData)".
//     Runs on mount (init) and again whenever $chartData changes (update).
//
//   lbChart.initFromEl(el) — for static charts (plain data="" prop).
//     Called via data-init="lbChart.initFromEl(el)".
//     Reads data-lb-chart-data/options from the element and initialises once.
//
// Chart.js instances are stored in a WeakMap, NOT in Datastar signals.
// Wrapping a Chart instance in a Datastar Proxy causes:
//   "Maximum call stack size exceeded"
// because Chart.js has its own internal getter chain that clashes with Proxy.
//
// Deep-clone via JSON.parse(JSON.stringify(...)) is required before passing
// any signal-derived data to Chart.js — same reason: strips Proxy wrappers.

(function () {
    var _instances = new WeakMap();
    // Live entries, so theme rebuilds can enumerate. WeakMap cannot be walked.
    var _live = [];

    function _clone(val) {
        try { return JSON.parse(JSON.stringify(val)); } catch (e) { return {}; }
    }

    function _isPlainObject(val) {
        return val !== null && typeof val === 'object' && !Array.isArray(val);
    }

    // Chart.js options nest (plugins.legend, scales.y), so a shallow merge would
    // drop a whole default subtree whenever the caller supplies its parent key.
    // Arrays replace: passing `datasets` means those datasets, not those appended.
    function _deepMerge(base, override) {
        var out = {};
        var key;
        for (key in base) {
            if (Object.prototype.hasOwnProperty.call(base, key)) out[key] = base[key];
        }
        for (key in override) {
            if (!Object.prototype.hasOwnProperty.call(override, key)) continue;
            if (_isPlainObject(out[key]) && _isPlainObject(override[key])) {
                out[key] = _deepMerge(out[key], override[key]);
            } else {
                out[key] = override[key];
            }
        }
        return out;
    }

    function _buildChart(el, rawData, rawOpts) {
        var canvas = el.querySelector('canvas');
        if (!canvas) return null;
        canvas.removeAttribute('width');
        canvas.removeAttribute('height');

        var type   = el.dataset.lbChartType   || 'bar';
        var legend = el.dataset.lbChartLegend || 'top';
        var data   = _clone(rawData);
        var opts   = _clone(rawOpts);

        var plugin = window.LabbDaisyUIPlugin;
        if (plugin && plugin.beforeInit) {
            plugin.beforeInit({ config: { type: type, data: data } });
        }

        var isRadial = ['pie', 'doughnut', 'polarArea', 'radar'].includes(type);

        var chart = new window.Chart(canvas, {
            type: type,
            data: data,
            options: _deepMerge(
                {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: legend === 'none' ? false : legend } },
                    scales: isRadial ? {} : { x: {}, y: {} },
                },
                opts
            ),
        });

        return chart;
    }

    function _forget(entry) {
        var i = _live.indexOf(entry);
        if (i !== -1) _live.splice(i, 1);
        _instances.delete(entry.el);
        if (entry.chart) entry.chart.destroy();
    }

    // Charts that left the DOM are dropped rather than rebuilt, so a morphed-away
    // chart stops holding its element, its Chart.js instance and its cloned data.
    function _sweep() {
        for (var i = _live.length - 1; i >= 0; i--) {
            if (!_live[i].el.isConnected) _forget(_live[i]);
        }
    }

    function _rebuildAll() {
        _sweep();
        for (var i = 0; i < _live.length; i++) {
            var entry = _live[i];
            if (entry.chart) entry.chart.destroy();
            entry.chart = _buildChart(entry.el, entry.rawData, entry.rawOpts);
        }
    }

    // One observer and one listener for the page, not one per chart. Per-chart
    // handlers on `document` kept every chart element alive for the page's life.
    var _watching = false;

    function _watch() {
        if (_watching) return;
        _watching = true;
        new MutationObserver(_rebuildAll).observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme'],
        });
        document.addEventListener('lb:chart-defaults-applied', _rebuildAll);
    }

    function _init(el, rawData, rawOpts) {
        _sweep();
        _watch();

        var entry = {
            el: el,
            chart: _buildChart(el, rawData, rawOpts),
            type: el.dataset.lbChartType || 'bar',
            rawData: _clone(rawData),
            rawOpts: _clone(rawOpts),
        };
        _instances.set(el, entry);
        _live.push(entry);
    }

    function _update(el, signalData) {
        var entry = _instances.get(el);
        if (!entry || !entry.chart) return;
        var chart  = entry.chart;
        var snap   = _clone(signalData);

        if (snap.data !== undefined) {
            entry.rawData = _clone(snap.data);
            var resolved  = _clone(snap.data);
            var plugin    = window.LabbDaisyUIPlugin;
            if (plugin && plugin.beforeInit) {
                plugin.beforeInit({ config: { type: entry.type, data: resolved } });
            }
            chart.data.labels   = resolved.labels   || [];
            chart.data.datasets = resolved.datasets || [];
        }
        if (snap.legend !== undefined) {
            // Custom `options` may have supplied a plugins object of its own.
            chart.options.plugins = chart.options.plugins || {};
            chart.options.plugins.legend = chart.options.plugins.legend || {};
            chart.options.plugins.legend.position = snap.legend === 'none' ? false : snap.legend;
        }
        if (snap.options !== undefined) {
            entry.rawOpts = _deepMerge(entry.rawOpts, snap.options);
            chart.options = _deepMerge(chart.options, snap.options);
        }

        var cfg = window.lbChartConfig || {};
        chart.update(cfg.updateAnimation === false ? 'none' : undefined);
    }

    window.lbChart = {
        // Reactive entry point — called by data-effect.
        handle: function (el, signalData) {
            var data = _clone(signalData);
            if (!_instances.has(el)) {
                var rawData = data.data !== undefined ? data.data : data;
                // Options come from the `options` prop (data-lb-chart-options),
                // same as the static path. Signal-provided options override it.
                var attrOpts = {};
                try { attrOpts = JSON.parse(el.dataset.lbChartOptions || '{}'); } catch (e) {}
                var rawOpts = _deepMerge(attrOpts, data.options !== undefined ? data.options : {});
                _init(el, rawData, rawOpts);
            } else {
                _update(el, data);
            }
        },

        // Static entry point — called by data-init.
        initFromEl: function (el) {
            var rawData = {};
            var rawOpts = {};
            try { rawData = JSON.parse(el.dataset.lbChartData    || '{}'); } catch (e) {}
            try { rawOpts = JSON.parse(el.dataset.lbChartOptions || '{}'); } catch (e) {}
            _init(el, rawData, rawOpts);
        },

        destroy: function (el) {
            var entry = _instances.get(el);
            if (entry) _forget(entry);
        },

        _internals: { live: _live, deepMerge: _deepMerge, sweep: _sweep, rebuildAll: _rebuildAll },
    };
})();
