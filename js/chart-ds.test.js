const assert = require('node:assert');
const { test, beforeEach, describe } = require('node:test');

const { loadScript, makeChartEl, FakeChart } = require('./harness');

let ctx;
let lbChart;

beforeEach(() => {
    FakeChart.reset();
    ctx = loadScript('chart-ds.js');
    lbChart = ctx.window.lbChart;
});

const DATA = { labels: ['a'], datasets: [{ label: 'x', data: [1] }] };

describe('options merging', () => {
    test('a custom plugins key does not drop the legend default', () => {
        const el = makeChartEl({
            lbChartLegend: 'bottom',
            lbChartData: JSON.stringify(DATA),
            lbChartOptions: JSON.stringify({ plugins: { tooltip: { enabled: false } } }),
        });

        lbChart.initFromEl(el);

        const built = FakeChart.built[0];
        assert.strictEqual(built.options.plugins.legend.position, 'bottom');
        assert.strictEqual(built.options.plugins.tooltip.enabled, false);
    });

    test('a custom scales key keeps the axes it does not mention', () => {
        const el = makeChartEl({
            lbChartData: JSON.stringify(DATA),
            lbChartOptions: JSON.stringify({ scales: { y: { beginAtZero: true } } }),
        });

        lbChart.initFromEl(el);

        const scales = FakeChart.built[0].options.scales;
        assert.strictEqual(scales.y.beginAtZero, true);
        assert.ok(scales.x, 'the x axis default survives');
    });

    test('caller options win over labb defaults', () => {
        const el = makeChartEl({
            lbChartData: JSON.stringify(DATA),
            lbChartOptions: JSON.stringify({ responsive: false }),
        });

        lbChart.initFromEl(el);

        assert.strictEqual(FakeChart.built[0].options.responsive, false);
    });

    test('arrays replace rather than merge', () => {
        const merge = lbChart._internals.deepMerge;
        // Structural compare: objects built inside the vm context have their own intrinsics.
        assert.strictEqual(JSON.stringify(merge({ a: [1, 2, 3] }, { a: [9] })), '{"a":[9]}');
    });

    test('legend="none" still disables the legend', () => {
        const el = makeChartEl({
            lbChartLegend: 'none',
            lbChartData: JSON.stringify(DATA),
        });

        lbChart.initFromEl(el);

        assert.strictEqual(FakeChart.built[0].options.plugins.legend.position, false);
    });
});

describe('reactive updates', () => {
    test('a legend update does not throw on a chart with custom plugins', () => {
        const el = makeChartEl({
            lbChartOptions: JSON.stringify({ plugins: { tooltip: { enabled: false } } }),
        });

        lbChart.handle(el, { data: DATA });
        lbChart.handle(el, { legend: 'left' });

        assert.strictEqual(FakeChart.built[0].options.plugins.legend.position, 'left');
    });

    test('an options update merges instead of replacing', () => {
        const el = makeChartEl({});

        lbChart.handle(el, { data: DATA });
        lbChart.handle(el, { options: { plugins: { tooltip: { enabled: false } } } });

        const chart = FakeChart.built[0];
        assert.strictEqual(chart.options.plugins.tooltip.enabled, false);
        assert.ok(chart.options.plugins.legend, 'legend survives an options update');
    });

    test('new data reaches the chart', () => {
        const el = makeChartEl({});

        lbChart.handle(el, { data: DATA });
        lbChart.handle(el, { data: { labels: ['b'], datasets: [{ data: [2] }] } });

        assert.strictEqual(JSON.stringify(FakeChart.built[0].data.labels), '["b"]');
    });
});

describe('teardown', () => {
    test('document listeners do not grow with the number of charts', () => {
        for (let i = 0; i < 5; i++) lbChart.initFromEl(makeChartEl({}));

        assert.strictEqual(ctx.listenerCount('lb:chart-defaults-applied'), 1);
        assert.strictEqual(ctx.observers.length, 1);
    });

    test('a detached chart is dropped and not rebuilt on a theme change', () => {
        const gone = makeChartEl({});
        const kept = makeChartEl({});
        lbChart.initFromEl(gone);
        lbChart.initFromEl(kept);

        gone.isConnected = false;
        ctx.themeChange();

        assert.strictEqual(lbChart._internals.live.length, 1);
        assert.strictEqual(lbChart._internals.live[0].el, kept);
        assert.ok(FakeChart.built[0].destroyed, 'the detached chart was destroyed');
    });

    test('a live chart is rebuilt on a theme change', () => {
        const el = makeChartEl({ lbChartData: JSON.stringify(DATA) });
        lbChart.initFromEl(el);

        ctx.themeChange();

        assert.strictEqual(FakeChart.built.length, 2);
        assert.ok(FakeChart.built[0].destroyed);
        assert.strictEqual(FakeChart.built[1].destroyed, false);
    });

    test('destroy() forgets the chart', () => {
        const el = makeChartEl({});
        lbChart.initFromEl(el);

        lbChart.destroy(el);

        assert.strictEqual(lbChart._internals.live.length, 0);
        assert.ok(FakeChart.built[0].destroyed);
    });

    test('initialising after churn sweeps the detached ones', () => {
        const gone = makeChartEl({});
        lbChart.initFromEl(gone);
        gone.isConnected = false;

        lbChart.initFromEl(makeChartEl({}));

        assert.strictEqual(lbChart._internals.live.length, 1);
    });
});

describe('robustness', () => {
    test('an element with no canvas does not throw', () => {
        const el = makeChartEl({});
        el.children = [];

        assert.doesNotThrow(() => lbChart.initFromEl(el));
    });

    test('malformed JSON in the data attribute does not throw', () => {
        const el = makeChartEl({ lbChartData: '{not json' });

        assert.doesNotThrow(() => lbChart.initFromEl(el));
    });
});
