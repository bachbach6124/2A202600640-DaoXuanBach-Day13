from __future__ import annotations

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Day 13 / Observability</title>
  <style>
    :root {
      color-scheme: light;
      --paper: #f3f1eb;
      --ink: #181916;
      --muted: #686b63;
      --line: #d7d4cb;
      --accent: #d45b26;
      --danger: #b82f2f;
      --ok: #2f7450;
      --panel: #faf9f5;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .shell { min-height: 100vh; padding: 28px clamp(20px, 4vw, 64px) 48px; }
    header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--ink);
      animation: enter .45s ease-out both;
    }
    .eyebrow, .panel-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 750;
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    h1 { margin: 6px 0 0; font-size: clamp(30px, 5vw, 58px); line-height: .95; letter-spacing: -.055em; }
    .scope { display: flex; align-items: center; gap: 14px; color: var(--muted); font-size: 13px; }
    .live { display: inline-flex; align-items: center; gap: 7px; color: var(--ok); font-weight: 700; }
    .live::before {
      content: ""; width: 8px; height: 8px; border-radius: 50%; background: currentColor;
      box-shadow: 0 0 0 0 rgba(47,116,80,.35); animation: pulse 2s infinite;
    }
    .summary {
      display: grid;
      grid-template-columns: 1.3fr repeat(3, minmax(120px, .7fr));
      gap: 0;
      border-bottom: 1px solid var(--line);
      animation: enter .45s .08s ease-out both;
    }
    .summary > div { padding: 20px 20px 20px 0; }
    .summary > div + div { padding-left: 20px; border-left: 1px solid var(--line); }
    .summary strong { display: block; margin-top: 5px; font-size: 22px; letter-spacing: -.03em; }
    .alerts { color: var(--muted); }
    .alerts.firing { color: var(--danger); }
    main {
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      column-gap: 28px;
      border-bottom: 1px solid var(--ink);
    }
    .panel {
      grid-column: span 4;
      min-height: 300px;
      padding: 28px 0 24px;
      border-bottom: 1px solid var(--line);
      animation: enter .5s ease-out both;
    }
    .panel:nth-child(2), .panel:nth-child(5) { padding-left: 28px; padding-right: 28px; border-left: 1px solid var(--line); border-right: 1px solid var(--line); }
    .panel:nth-child(1) { animation-delay: .12s; }
    .panel:nth-child(2) { animation-delay: .16s; }
    .panel:nth-child(3) { animation-delay: .20s; }
    .panel:nth-child(4) { animation-delay: .24s; }
    .panel:nth-child(5) { animation-delay: .28s; }
    .panel:nth-child(6) { animation-delay: .32s; }
    .panel-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
    .panel h2 { margin: 7px 0 0; font-size: 21px; letter-spacing: -.03em; }
    .unit { color: var(--muted); font-size: 12px; }
    .value { margin: 30px 0 4px; font-size: clamp(38px, 5vw, 58px); font-weight: 760; line-height: 1; letter-spacing: -.06em; }
    .value small { color: var(--muted); font-size: 14px; letter-spacing: 0; }
    .subvalues { display: flex; gap: 18px; color: var(--muted); font-size: 12px; }
    .subvalues b { color: var(--ink); font-size: 14px; }
    canvas { width: 100%; height: 92px; margin-top: 22px; display: block; }
    .breakdown { margin-top: 25px; display: grid; gap: 10px; }
    .breakdown div { display: flex; justify-content: space-between; padding-bottom: 9px; border-bottom: 1px solid var(--line); font-size: 13px; }
    footer { display: flex; justify-content: space-between; padding-top: 16px; color: var(--muted); font-size: 12px; }
    @keyframes enter { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
    @keyframes pulse { 70% { box-shadow: 0 0 0 7px rgba(47,116,80,0); } 100% { box-shadow: 0 0 0 0 rgba(47,116,80,0); } }
    @media (max-width: 900px) {
      .summary { grid-template-columns: 1fr 1fr; }
      .summary > div { border-bottom: 1px solid var(--line); }
      .panel { grid-column: span 6; }
      .panel:nth-child(2), .panel:nth-child(5) { border-right: 0; }
      .panel:nth-child(3) { padding-left: 28px; border-left: 1px solid var(--line); }
    }
    @media (max-width: 620px) {
      header, footer { align-items: flex-start; flex-direction: column; }
      .summary { grid-template-columns: 1fr; }
      .summary > div + div { padding-left: 0; border-left: 0; }
      .panel { grid-column: span 12; min-height: 270px; }
      .panel:nth-child(n) { padding-left: 0; padding-right: 0; border-left: 0; border-right: 0; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div>
        <div class="eyebrow">Day 13 / Agent operations</div>
        <h1>Observability</h1>
      </div>
      <div class="scope"><span class="live">Live</span><span>Last 1 hour</span><span>Refresh 15s</span></div>
    </header>

    <section class="summary">
      <div><span class="panel-label">Service</span><strong>day13-observability-lab</strong></div>
      <div><span class="panel-label">Requests</span><strong id="traffic">0</strong></div>
      <div><span class="panel-label">Success</span><strong id="success">0</strong></div>
      <div><span class="panel-label">Alerts</span><strong id="alerts" class="alerts">0 firing</strong></div>
    </section>

    <main>
      <section class="panel">
        <div class="panel-head"><div><span class="panel-label">01 / Tail health</span><h2>Latency</h2></div><span class="unit">SLO 3,000 ms</span></div>
        <div class="value"><span id="p95">0</span> <small>ms P95</small></div>
        <div class="subvalues"><span>P50 <b id="p50">0</b></span><span>P99 <b id="p99">0</b></span></div>
        <canvas id="latency-chart"></canvas>
      </section>
      <section class="panel">
        <div class="panel-head"><div><span class="panel-label">02 / Demand</span><h2>Traffic</h2></div><span class="unit">requests / min</span></div>
        <div class="value"><span id="rpm">0</span> <small>rpm</small></div>
        <div class="subvalues"><span>Total <b id="traffic-total">0</b></span><span>Errors <b id="traffic-errors">0</b></span></div>
        <canvas id="traffic-chart"></canvas>
      </section>
      <section class="panel">
        <div class="panel-head"><div><span class="panel-label">03 / Reliability</span><h2>Error rate</h2></div><span class="unit">SLO &lt; 2%</span></div>
        <div class="value"><span id="error-rate">0</span><small>%</small></div>
        <div id="error-breakdown" class="breakdown"><div><span>No errors recorded</span><b>0</b></div></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div><span class="panel-label">04 / Budget</span><h2>Cost</h2></div><span class="unit">USD / day</span></div>
        <div class="value">$<span id="daily-cost">0</span></div>
        <div class="subvalues"><span>Average <b id="avg-cost">$0</b></span><span>SLO <b>$2.50</b></span></div>
        <canvas id="cost-chart"></canvas>
      </section>
      <section class="panel">
        <div class="panel-head"><div><span class="panel-label">05 / Usage</span><h2>Tokens</h2></div><span class="unit">input / output</span></div>
        <div class="value"><span id="tokens-out">0</span> <small>out</small></div>
        <div class="subvalues"><span>Input <b id="tokens-in">0</b></span><span>Total <b id="tokens-total">0</b></span></div>
        <canvas id="tokens-chart"></canvas>
      </section>
      <section class="panel">
        <div class="panel-head"><div><span class="panel-label">06 / Answer signal</span><h2>Quality proxy</h2></div><span class="unit">Target 0.75</span></div>
        <div class="value"><span id="quality">0</span><small> / 1.0</small></div>
        <div class="subvalues"><span>Heuristic based on retrieval and answer coverage</span></div>
        <canvas id="quality-chart"></canvas>
      </section>
    </main>
    <footer><span id="updated">Waiting for metrics...</span><span>Metrics -> Traces -> Logs</span></footer>
  </div>
  <script>
    const accent = "#d45b26", muted = "#b9b5aa", danger = "#b82f2f";
    const text = (id, value) => { document.getElementById(id).textContent = value; };
    const format = (value, digits = 2) => Number(value || 0).toFixed(digits);

    function draw(id, values, color = accent, threshold = null) {
      const canvas = document.getElementById(id);
      const ratio = window.devicePixelRatio || 1;
      canvas.width = canvas.clientWidth * ratio;
      canvas.height = canvas.clientHeight * ratio;
      const ctx = canvas.getContext("2d");
      ctx.scale(ratio, ratio);
      const width = canvas.clientWidth, height = canvas.clientHeight;
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = muted; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, height - .5); ctx.lineTo(width, height - .5); ctx.stroke();
      const data = values.length ? values : [0, 0];
      const max = Math.max(...data, threshold || 0, 1);
      if (threshold !== null) {
        const y = height - (threshold / max) * (height - 10);
        ctx.setLineDash([5, 5]); ctx.strokeStyle = danger;
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke(); ctx.setLineDash([]);
      }
      ctx.strokeStyle = color; ctx.lineWidth = 2.25; ctx.lineJoin = "round";
      ctx.beginPath();
      data.forEach((value, index) => {
        const x = data.length === 1 ? 0 : index * width / (data.length - 1);
        const y = height - (value / max) * (height - 10);
        index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      });
      ctx.stroke();
    }

    async function refresh() {
      const [metricsResponse, alertsResponse] = await Promise.all([
        fetch("/metrics"), fetch("/alerts?demo=true")
      ]);
      const m = await metricsResponse.json();
      const alerts = await alertsResponse.json();
      const series = m.time_series || [];
      text("traffic", m.traffic); text("success", m.success_count);
      text("p50", Math.round(m.latency_p50_ms)); text("p95", Math.round(m.latency_p95_ms)); text("p99", Math.round(m.latency_p99_ms));
      text("rpm", format(m.request_rate_per_min, 2)); text("traffic-total", m.traffic); text("traffic-errors", m.error_count);
      text("error-rate", format(m.error_rate_pct, 2));
      text("daily-cost", format(m.daily_cost_usd, 4)); text("avg-cost", "$" + format(m.avg_cost_usd, 5));
      text("tokens-in", m.tokens_in_total); text("tokens-out", m.tokens_out_total); text("tokens-total", m.tokens_in_total + m.tokens_out_total);
      text("quality", format(m.quality_avg, 2));
      const firing = alerts.filter(alert => alert.firing).length;
      const alertNode = document.getElementById("alerts");
      alertNode.textContent = firing + " firing";
      alertNode.classList.toggle("firing", firing > 0);
      const breakdown = Object.entries(m.error_breakdown || {});
      document.getElementById("error-breakdown").innerHTML = breakdown.length
        ? breakdown.map(([name, count]) => `<div><span>${name}</span><b>${count}</b></div>`).join("")
        : "<div><span>No errors recorded</span><b>0</b></div>";
      draw("latency-chart", series.map(item => item.latency_ms), accent, 3000);
      draw("traffic-chart", series.map((_, index) => index + 1));
      draw("cost-chart", series.map(item => item.cost_usd));
      draw("tokens-chart", series.map(item => item.tokens_in + item.tokens_out));
      draw("quality-chart", series.map(item => item.quality_score || 0), accent, .75);
      text("updated", "Updated " + new Date(m.generated_at).toLocaleTimeString());
    }
    refresh().catch(console.error);
    setInterval(() => refresh().catch(console.error), 15000);
  </script>
</body>
</html>
"""
