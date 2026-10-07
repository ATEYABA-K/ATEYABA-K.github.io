// Graphiques interactifs de l'étude NBA : terrain animé, rendement par zone,
// répartition des tirs et corrélation. Données injectées dans la page (resultats.json, terrain.json).
(() => {
  const RES = JSON.parse(document.getElementById('data-res').textContent);
  const COURT = JSON.parse(document.getElementById('data-court').textContent);
  const NS = 'http://www.w3.org/2000/svg';
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const fr = (x, d = 1) => x.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const pct = (x, d = 1) => fr(x * 100, d) + ' %';
  const label = (s) => `${s - 1}-${String(s).slice(2)}`;
  const SAISONS = Object.keys(RES.part_par_zone);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const el = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  };

  // ---------- infobulle partagée ----------
  const tip = document.querySelector('.tip');
  const showTip = (html, e) => {
    tip.innerHTML = html;
    tip.classList.add('on');
    const r = tip.getBoundingClientRect();
    let x = e.clientX + 14, y = e.clientY + 14;
    if (x + r.width > innerWidth - 8) x = e.clientX - r.width - 14;
    if (y + r.height > innerHeight - 8) y = e.clientY - r.height - 14;
    tip.style.transform = `translate(${x}px, ${y}px)`;
  };
  const hideTip = () => tip.classList.remove('on');

  // ---------- 1. Terrain ----------
  const court = document.querySelector('svg.court');
  const cells = el('g', {}, court);
  const lines = el('g', { class: 'court-lines' }, court);
  // Lignes du terrain NBA (pieds) : panier à 5,25 du fond, ligne à 3 pts à 22 (coin) et 23,75 (axe).
  el('line', { x1: -25, x2: 25, y1: 0, y2: 0 }, lines);
  el('rect', { x: -8, y: 0, width: 16, height: 19 }, lines);
  el('path', { d: 'M -6 19 A 6 6 0 0 0 6 19' }, lines);
  el('path', { d: 'M -4 5.25 A 4 4 0 0 0 4 5.25' }, lines);
  el('circle', { cx: 0, cy: 5.25, r: .75 }, lines);
  el('line', { x1: -3, x2: 3, y1: 4, y2: 4 }, lines);
  const yc = 5.25 + Math.sqrt(23.75 ** 2 - 22 ** 2);
  el('path', { d: `M -22 0 L -22 ${yc} A 23.75 23.75 0 0 0 22 ${yc} L 22 0` }, lines);

  const input = document.querySelector('.court-controls input');
  const seasonOut = document.querySelector('.court-season');
  const playBtn = document.querySelector('.court-controls .play');
  const legend = document.querySelector('.court-legend');
  const read = (k) => document.querySelector(`.court-read [data-k="${k}"]`);
  let mode = 'volume';

  // Couleur "rendement" : divergente autour de 1 point par tir (bleu = sous, gris = neutre, orange = au-dessus).
  const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const divColor = (pps) => {
    const lo = hex('#2f5aa8'), mid = hex('#b9bcc4'), hi = hex('#d9542b');
    const t = Math.max(-1, Math.min(1, (pps - 1) / 0.35));
    const c = t < 0 ? mix(mid, lo, -t) : mix(mid, hi, t);
    return `rgb(${c})`;
  };

  const drawLegend = () => {
    legend.innerHTML = mode === 'volume'
      ? '<span class="lg-ramp vol"></span><span>peu de tirs</span><span style="margin-left:auto">beaucoup de tirs</span>'
      : '<span class="lg-ramp roi"></span><span>0,65 pt / tir</span><span style="margin-left:auto">1,35 pt / tir</span>';
  };

  const draw = (s) => {
    const data = COURT.saisons[s];
    cells.innerHTML = '';
    const hot = css('--hot');
    for (const [cy, cx, part, pps] of data) {
      const x = cx * 2 - 25, y = cy * 2;
      const r = el('rect', { x: x + .1, y: y + .1, width: 1.8, height: 1.8, rx: .35 }, cells);
      if (mode === 'volume') {
        r.setAttribute('fill', hot);
        r.setAttribute('fill-opacity', Math.min(1, Math.sqrt(part / 40)).toFixed(3));
      } else {
        r.setAttribute('fill', divColor(pps));
        r.setAttribute('fill-opacity', Math.max(.25, Math.min(1, Math.sqrt(part / 12))).toFixed(3));
      }
      r.dataset.t = `<b>${label(+s)}</b><br>${fr(part / 10, 2)} % des tirs<br>${fr(pps, 2)} point par tir`;
    }
    const p = RES.part_par_zone[label(+s)];
    seasonOut.textContent = label(+s);
    read('mid').textContent = pct(p['Mi-distance']);
    read('trois').textContent = pct(p['3 pts dans le coin'] + p["3 pts dans l'axe"]);
    read('pps').textContent = fr(RES.rendement_global[label(+s)], 2);
  };

  cells.addEventListener('pointermove', (e) => { if (e.target.dataset.t) showTip(e.target.dataset.t, e); });
  cells.addEventListener('pointerleave', hideTip);
  input.addEventListener('input', () => { stop(); draw(input.value); });
  document.querySelectorAll('.seg button').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('.seg button').forEach((x) => x.classList.toggle('on', x === b));
    mode = b.dataset.mode; drawLegend(); draw(input.value);
  }));

  let timer = null;
  const stop = () => { clearInterval(timer); timer = null; playBtn.textContent = '▶ Lecture'; };
  playBtn.addEventListener('click', () => {
    if (timer) return stop();
    if (+input.value >= 2025) input.value = 2004;
    playBtn.textContent = '❚❚ Pause';
    draw(input.value);
    timer = setInterval(() => {
      if (+input.value >= 2025) return stop();
      input.value = +input.value + 1; draw(input.value);
    }, 650);
  });
  drawLegend(); draw(2004);
  // Lecture automatique la première fois que le terrain apparaît à l'écran.
  if (!reduce && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => {
      if (es[0].isIntersecting) { io.disconnect(); setTimeout(() => { if (!timer) playBtn.click(); }, 500); }
    }, { threshold: .6 });
    io.observe(court);
  }

  // ---------- 2. Rendement par zone (barres + repère 2003-04) ----------
  {
    const svg = document.getElementById('roi');
    const zones = ['Sous le panier', '3 pts dans le coin', "3 pts dans l'axe", 'Raquette', 'Mi-distance'];
    const last = RES.rendement_par_zone[SAISONS.at(-1)], first = RES.rendement_par_zone[SAISONS[0]];
    const W = 640, rowH = 58, max = 1.4, pw = W - 110;
    svg.setAttribute('viewBox', `0 0 ${W} ${zones.length * rowH + 26}`);
    zones.forEach((z, i) => {
      const y = i * rowH;
      const g = el('g', {}, svg);
      el('text', { class: 'lab', x: 0, y: y + 18 }, g).textContent = z;
      el('rect', { class: 'bar ' + (z === 'Mi-distance' ? 'hl' : z === '3 pts dans le coin' ? 'strong' : ''), x: 0, y: y + 28, width: pw * last[z] / max, height: 20, rx: 4 }, g);
      const fx = pw * first[z] / max;
      el('line', { class: 'tick', x1: fx, x2: fx, y1: y + 24, y2: y + 52 }, g);
      el('text', { class: 'val', x: pw * Math.max(last[z], first[z]) / max + 10, y: y + 43 }, g).textContent = fr(last[z], 2);
      el('rect', { x: 0, y, width: W, height: rowH, fill: 'transparent' }, g).addEventListener('pointermove', (e) =>
        showTip(`<b>${z}</b><br>2024-25 : ${fr(last[z], 2)} pt / tir<br>2003-04 : ${fr(first[z], 2)} pt / tir`, e));
      g.addEventListener('pointerleave', hideTip);
    });
    const x1 = pw * 1 / max;
    el('line', { class: 'ref', x1, x2: x1, y1: 0, y2: zones.length * rowH + 4 }, svg);
    el('text', { x: x1, y: zones.length * rowH + 22, 'text-anchor': 'middle' }, svg).textContent = '1 point par tir';
  }

  // ---------- 3. Répartition des tirs (lignes + réticule) ----------
  {
    const svg = document.getElementById('mix');
    const W = 640, H = 300, L = 36, R = 92, T = 12, B = 30;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const series = [
      { nom: 'Près du panier', cls: 'muted', v: (p) => p['Sous le panier'] + p['Raquette'] },
      { nom: '3 points', cls: 'accent', v: (p) => p['3 pts dans le coin'] + p["3 pts dans l'axe"] },
      { nom: 'Mi-distance', cls: 'hot', v: (p) => p['Mi-distance'] },
    ];
    const n = SAISONS.length, maxY = .55;
    const X = (i) => L + (W - L - R) * i / (n - 1), Y = (v) => T + (H - T - B) * (1 - v / maxY);
    for (const t of [0, .1, .2, .3, .4, .5]) {
      el('line', { class: 'grid', x1: L, x2: W - R, y1: Y(t), y2: Y(t) }, svg);
      el('text', { x: L - 8, y: Y(t) + 4, 'text-anchor': 'end' }, svg).textContent = t * 100 + ' %';
    }
    [0, 6, 12, 18, 21].forEach((i) => { el('text', { x: X(i), y: H - 8, 'text-anchor': 'middle' }, svg).textContent = SAISONS[i]; });
    const vals = series.map((s) => SAISONS.map((k) => s.v(RES.part_par_zone[k])));
    series.forEach((s, j) => {
      el('path', { class: 'line ' + s.cls, d: vals[j].map((v, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join('') }, svg);
      el('text', { class: 'end ' + s.cls, x: X(n - 1) + 8, y: Y(vals[j][n - 1]) + 4 }, svg).textContent = s.nom;
    });
    const cross = el('line', { class: 'cross', y1: T, y2: H - B, x1: -10, x2: -10 }, svg);
    const dots = series.map((s) => el('circle', { class: 'dot ' + s.cls, r: 4.5, cx: -10, cy: -10 }, svg));
    const hit = el('rect', { x: L, y: T, width: W - L - R, height: H - T - B, fill: 'transparent' }, svg);
    hit.addEventListener('pointermove', (e) => {
      const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
      const p = pt.matrixTransform(svg.getScreenCTM().inverse());
      const i = Math.max(0, Math.min(n - 1, Math.round((p.x - L) / (W - L - R) * (n - 1))));
      cross.setAttribute('x1', X(i)); cross.setAttribute('x2', X(i));
      dots.forEach((d, j) => { d.setAttribute('cx', X(i)); d.setAttribute('cy', Y(vals[j][i])); });
      showTip(`<b>${SAISONS[i]}</b>` + series.map((s, j) => `<br><i class="sw ${s.cls}"></i>${s.nom} : ${pct(vals[j][i])}`).join(''), e);
    });
    hit.addEventListener('pointerleave', () => { hideTip(); cross.setAttribute('x1', -10); cross.setAttribute('x2', -10); dots.forEach((d) => d.setAttribute('cx', -10)); });
  }

  // ---------- 4. Corrélation par saison (barres divergentes) ----------
  {
    const svg = document.getElementById('corr');
    const W = 640, H = 240, L = 36, T = 10, B = 30;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const vals = SAISONS.map((k) => RES.correlation_mi_distance_rendement[k]);
    const n = vals.length, bw = (W - L) / n, Y = (v) => T + (H - T - B) * (.3 - v) / .9;
    for (const t of [.3, 0, -.3, -.6]) {
      el('line', { class: t === 0 ? 'base' : 'grid', x1: L, x2: W, y1: Y(t), y2: Y(t) }, svg);
      el('text', { x: L - 8, y: Y(t) + 4, 'text-anchor': 'end' }, svg).textContent = fr(t, 1);
    }
    vals.forEach((v, i) => {
      const x = L + i * bw + bw * .18, w = bw * .64;
      const r = el('rect', { class: 'bar ' + (v > 0 ? 'hl' : 'strong'), x, y: Math.min(Y(v), Y(0)), width: w, height: Math.max(1, Math.abs(Y(v) - Y(0))), rx: 2 }, svg);
      r.addEventListener('pointermove', (e) => showTip(`<b>${SAISONS[i]}</b><br>corrélation : ${fr(v, 2)}<br>équipe avec le moins de mi-distance : ${RES.equipe_avec_le_moins_de_mi_distance[SAISONS[i]]}`, e));
      r.addEventListener('pointerleave', hideTip);
    });
    [0, 7, 14, 21].forEach((i) => { el('text', { x: L + i * bw + bw / 2, y: H - 8, 'text-anchor': 'middle' }, svg).textContent = SAISONS[i]; });
  }
})();
