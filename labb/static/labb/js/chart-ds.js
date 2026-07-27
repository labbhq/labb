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

    function _clone(val) {
        try { return JSON.parse(JSON.stringify(val)); } catch (e) { return {}; }
    }

    function _buildChart(el, rawData, rawOpts) {
        var canvas = el.querySelector('canvas');
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
            options: Object.assign(
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

    function _init(el, rawData, rawOpts) {
        var chart = _buildChart(el, rawData, rawOpts);
        var type  = el.dataset.lbChartType || 'bar';

        function rebuild() {
            var entry = _instances.get(el);
            if (!entry) return;
            entry.chart.destroy();
            entry.chart = _buildChart(el, entry.rawData, entry.rawOpts);
        }

        var observer = new MutationObserver(rebuild);
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme'],
        });

        document.addEventListener('lb:chart-defaults-applied', rebuild);

        _instances.set(el, {
            chart: chart,
            type: type,
            rawData: _clone(rawData),
            rawOpts: _clone(rawOpts),
            observer: observer,
            rebuild: rebuild,
        });
    }

    function _update(el, signalData) {
        var entry = _instances.get(el);
        if (!entry) return;
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
            chart.options.plugins.legend.position = snap.legend === 'none' ? false : snap.legend;
        }
        if (snap.options !== undefined) {
            entry.rawOpts = _clone(snap.options);
            Object.assign(chart.options, snap.options);
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
                var rawOpts = Object.assign(attrOpts, data.options !== undefined ? data.options : {});
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
    };
})();
