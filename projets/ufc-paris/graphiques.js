// Graphiques interactifs de l'étude paris sportifs × UFC : événements par an, calculatrice de marge,
// calibration des cotes, rendement par cote, et simulateur "Essayez de battre le bookmaker".
(() => {
  const RES = JSON.parse(document.getElementById('data-res').textContent);
  const FIGHTS = JSON.parse(document.getElementById('data-fights').textContent); // [cote rouge, cote bleu, rouge gagne, année]
  const NS = 'http://www.w3.org/2000/svg';
  const fr = (x, d = 1) => x.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const pct = (x, d = 0) => fr(x * 100, d) + ' %';
  const eur = (x) => (x > 0 ? '+' : x < 0 ? '−' : '') + fr(Math.abs(x), 0) + ' €';
  const el = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  };
  const tip = document.querySelector('.tip');
  const showTip = (html, e) => {
    tip.innerHTML = html; tip.classList.add('on');
    const r = tip.getBoundingClientRect();
    let x = e.clientX + 14, y = e.clientY + 14;
    if (x + r.width > innerWidth - 8) x = e.clientX - r.width - 14;
    if (y + r.height > innerHeight - 8) y = e.clientY - r.height - 14;
    tip.style.transform = `translate(${x}px, ${y}px)`;
  };
  const hideTip = () => tip.classList.remove('on');
  const hover = (node, html) => { node.addEventListener('pointermove', (e) => showTip(html, e)); node.addEventListener('pointerleave', hideTip); };

  // ---------- 1. Événements UFC par an ----------
  if (document.getElementById('events')) {
    const svg = document.getElementById('events');
    const data = Object.entries(RES.evenements_ufc_par_annee).filter(([y]) => +y >= 2001);
    const W = 640, H = 220, L = 30, T = 12, B = 28, max = Math.max(...data.map(([, v]) => v)) * 1.1;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const bw = (W - L) / data.length, Y = (v) => T + (H - T - B) * (1 - v / max);
    for (const t of [0, 20, 40]) {
      el('line', { class: t ? 'grid' : 'base', x1: L, x2: W, y1: Y(t), y2: Y(t) }, svg);
      el('text', { x: L - 6, y: Y(t) + 4, 'text-anchor': 'end' }, svg).textContent = t;
    }
    data.forEach(([y, v], i) => {
      const legal = +y >= 2020;
      const r = el('rect', { class: 'bar ' + (legal ? 'hl' : ''), x: L + i * bw + bw * .15, y: Y(v), width: bw * .7, height: Y(0) - Y(v), rx: 2 }, svg);
      hover(r, `<b>${y}</b><br>${v} événements UFC${+y === 2020 ? '<br>MMA légal en France' : ''}${+y >= 2022 ? '<br>dont 1 à Paris' : ''}`);
      if (+y % 5 === 0) el('text', { x: L + i * bw + bw / 2, y: H - 8, 'text-anchor': 'middle' }, svg).textContent = y;
    });
  }

  // ---------- 1 bis. Où va l'argent : barres empilées par année ----------
  if (document.getElementById('money')) {
    const svg = document.getElementById('money');
    const data = Object.entries(RES.marche_francais.par_annee);
    const W = 640, H = 280, L = 52, T = 14, B = 28, max = 12000;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const bw = (W - L) / data.length, Y = (v) => T + (H - T - B) * (1 - v / max);
    for (const t of [0, 3000, 6000, 9000, 12000]) {
      el('line', { class: t ? 'grid' : 'base', x1: L, x2: W, y1: Y(t), y2: Y(t) }, svg);
      el('text', { x: L - 8, y: Y(t) + 4, 'text-anchor': 'end' }, svg).textContent = t ? fr(t / 1000, 0) + ' Md€' : '0';
    }
    data.forEach(([y, v], i) => {
      const x = L + i * bw + bw * .15, w = bw * .7;
      const g = el('g', {}, svg);
      el('rect', { class: 'bar strong', x, y: Y(v.redistribue), width: w, height: Y(0) - Y(v.redistribue), rx: 2 }, g);
      el('rect', { class: 'bar hl', x, y: Y(v.mises), width: w, height: Y(v.redistribue) - Y(v.mises) - 1.5, rx: 2 }, g);
      el('rect', { x: L + i * bw, y: T, width: bw, height: H - T - B, fill: 'transparent' }, g);
      hover(g, `<b>${y}</b><br>Misé : ${fr(v.mises / 1000, 2)} Md€<br><i class="sw accent"></i>Revenu aux parieurs : ${fr(v.redistribue / 1000, 2)} Md€<br><i class="sw hot"></i>Gardé : ${fr(v.garde / 1000, 2)} Md€ (${pct(v.garde / v.mises, 1)})`);
      if (+y % 3 === 1 || +y === 2025) el('text', { x: x + w / 2, y: H - 8, 'text-anchor': 'middle' }, svg).textContent = y;
    });
  }

  // ---------- 2. Calculatrice de marge ----------
  {
    const a = document.getElementById('cA'), b = document.getElementById('cB'), out = document.getElementById('cOut');
    const bA = document.getElementById('bA'), bB = document.getElementById('bB'), bM = document.getElementById('bM');
    const upd = () => {
      const ca = Math.max(1.01, +a.value || 1.01), cb = Math.max(1.01, +b.value || 1.01);
      const pa = 1 / ca, pb = 1 / cb, tot = pa + pb, marge = tot - 1;
      const scale = 100 / Math.max(tot, 1);
      bA.style.width = pa * scale + '%'; bB.style.width = pb * scale + '%';
      bM.style.width = Math.max(0, marge) * scale + '%';
      bA.textContent = pct(pa, 1); bB.textContent = pct(pb, 1);
      out.innerHTML = marge > 0
        ? `Total : <b>${pct(tot, 1)}</b>. Les <b>${pct(marge, 1)}</b> en trop, c'est la marge du bookmaker. Sur 100 € misés par les parieurs (répartis comme le prévoient les cotes), il en garde environ <b>${fr(100 * marge / tot, 1)} €</b>, quel que soit le vainqueur.`
        : `Total : <b>${pct(tot, 1)}</b>. Sous 100 %, le bookmaker perdrait de l'argent à coup sûr : aucun ne propose ces cotes.`;
    };
    a.addEventListener('input', upd); b.addEventListener('input', upd); upd();
  }

  // ---------- 3. Calibration ----------
  if (document.getElementById('calib')) {
    const svg = document.getElementById('calib');
    const W = 640, H = 400, L = 48, R = 16, T = 12, B = 40;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const X = (v) => L + (W - L - R) * v, Y = (v) => T + (H - T - B) * (1 - v);
    for (const t of [0, .2, .4, .6, .8, 1]) {
      el('line', { class: 'grid', x1: L, x2: W - R, y1: Y(t), y2: Y(t) }, svg);
      el('text', { x: L - 8, y: Y(t) + 4, 'text-anchor': 'end' }, svg).textContent = t * 100 + ' %';
      el('text', { x: X(t), y: H - 18, 'text-anchor': 'middle' }, svg).textContent = t * 100 + ' %';
    }
    el('text', { x: (L + W - R) / 2, y: H - 2, 'text-anchor': 'middle' }, svg).textContent = 'probabilité annoncée par la cote';
    el('line', { class: 'ref', x1: X(0), y1: Y(0), x2: X(1), y2: Y(1) }, svg);
    el('text', { x: X(.82), y: Y(.86) - 6, 'text-anchor': 'end' }, svg).textContent = 'cote parfaite';
    const pts = RES.calibration.filter((p) => p.n >= 100);
    el('path', { class: 'line hot', d: pts.map((p, i) => `${i ? 'L' : 'M'}${X(p.annoncee)},${Y(p.observee)}`).join('') }, svg);
    pts.forEach((p) => {
      const c = el('circle', { class: 'dot hot', cx: X(p.annoncee), cy: Y(p.observee), r: 4 + Math.sqrt(p.n) / 9 }, svg);
      hover(c, `Annoncé : <b>${pct(p.annoncee)}</b><br>Réel : <b>${pct(p.observee)}</b><br>${p.n.toLocaleString('fr-FR')} combattants`);
    });
  }

  // ---------- 4. Rendement par tranche de cote ----------
  if (document.getElementById('roi')) {
    const svg = document.getElementById('roi');
    const data = Object.entries(RES.rendement_par_cote), ic = RES.rendement_par_cote_ic95;
    const W = 640, H = 260, L = 48, T = 14, B = 34, lo = -.5, hi = .1;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const Y = (v) => T + (H - T - B) * (hi - v) / (hi - lo), bw = (W - L) / data.length;
    for (const t of [.1, 0, -.1, -.2, -.3, -.4, -.5]) {
      el('line', { class: t === 0 ? 'base' : 'grid', x1: L, x2: W, y1: Y(t), y2: Y(t) }, svg);
      el('text', { x: L - 8, y: Y(t) + 4, 'text-anchor': 'end' }, svg).textContent = (t > 0 ? '+' : '') + fr(t * 100, 0) + ' %';
    }
    data.forEach(([k, v], i) => {
      const x = L + i * bw + bw * .2, w = bw * .6, r = v.rendement;
      const bar = el('rect', { class: 'bar ' + (r < -.1 ? 'hl' : r > 0 ? 'strong' : ''), x, y: Math.min(Y(r), Y(0)), width: w, height: Math.max(1.5, Math.abs(Y(r) - Y(0))), rx: 3 }, svg);
      const e = ic[k] || 0;
      el('line', { class: 'tick', x1: x + w / 2, x2: x + w / 2, y1: Y(r + e), y2: Y(r - e), 'stroke-width': 1.4 }, svg);
      el('text', { class: 'val', x: x + w / 2, y: (r < 0 ? Y(r - e) + 16 : Y(r + e) - 6), 'text-anchor': 'middle' }, svg).textContent = (r > 0 ? '+' : '') + fr(r * 100, 0) + ' %';
      el('text', { x: x + w / 2, y: H - 10, 'text-anchor': 'middle' }, svg).textContent = k;
      hover(bar, `<b>Cote ${k}</b><br>Rendement : ${(r > 0 ? '+' : '') + pct(r, 1)} (± ${pct(e, 1)})<br>Victoires : ${pct(v.victoires)}<br>${v.n.toLocaleString('fr-FR')} paris`);
    });
  }

  // ---------- 5. Simulateur ----------
  {
    const strat = document.getElementById('sStrat'), nIn = document.getElementById('sN'), nOut = document.getElementById('sNv');
    const go = document.getElementById('sGo'), hist = document.getElementById('hist'), path = document.getElementById('path');
    const MISE = 10, PARIEURS = 1000;
    // Pour chaque stratégie : la liste des paris possibles [cote, gagné].
    const pool = { hasard: [], favori: [], outsider: [], gros: [], coup: [] };
    for (const [cr, cb, rg] of FIGHTS) {
      const sides = [[cr, rg === 1], [cb, rg === 0]];
      pool.hasard.push(...sides);
      if (cr !== cb) {
        const [fav, out] = cr < cb ? sides : [sides[1], sides[0]];
        pool.favori.push(fav); pool.outsider.push(out);
      }
      for (const s of sides) { if (s[0] < 1.3) pool.gros.push(s); if (s[0] > 3) pool.coup.push(s); }
    }
    const run = () => {
      const p = pool[strat.value], n = +nIn.value, bilans = new Float64Array(PARIEURS);
      let exemple = null;
      for (let j = 0; j < PARIEURS; j++) {
        let cagnotte = 0; const trace = j === 0 ? [0] : null;
        for (let i = 0; i < n; i++) {
          const [cote, gagne] = p[(Math.random() * p.length) | 0];
          cagnotte += gagne ? MISE * (cote - 1) : -MISE;
          if (trace) trace.push(cagnotte);
        }
        bilans[j] = cagnotte; if (trace) exemple = trace;
      }
      const tri = Array.from(bilans).sort((a, b) => a - b);
      document.getElementById('rWin').textContent = pct(tri.filter((b) => b > 0).length / PARIEURS);
      document.getElementById('rMed').textContent = eur(tri[PARIEURS >> 1]);
      document.getElementById('rBest').textContent = eur(tri.at(-1));
      drawHist(tri); drawPath(exemple, n);
      document.getElementById('sNote').textContent = {
        gros: "Le seul angle mort des cotes : les très gros favoris rapportent un peu (+1,6 % en moyenne sur 15 ans), mais c'est dans la marge d'erreur, et une seule surprise efface cinq victoires. Peu de parieurs le font : ça ne fait pas rêver.",
        coup: "Le gros coup : c'est le pari qui fait rêver, et celui qui perd le plus (−30 % en moyenne au-dessus d'une cote de 5).",
      }[strat.value] || '';
    };
    const drawHist = (tri) => {
      hist.innerHTML = '';
      const W = 640, H = 200, T = 10, B = 26, bins = 30;
      hist.setAttribute('viewBox', `0 0 ${W} ${H}`);
      const lo = tri[0], hi = Math.max(tri.at(-1), 1), step = (hi - lo) / bins || 1;
      const counts = new Array(bins).fill(0);
      for (const b of tri) counts[Math.min(bins - 1, Math.floor((b - lo) / step))]++;
      const max = Math.max(...counts), X = (v) => W * (v - lo) / (hi - lo), bw = W / bins;
      counts.forEach((c, i) => {
        const x0 = lo + i * step, gain = x0 + step / 2 > 0;
        const r = el('rect', { class: 'bar ' + (gain ? 'strong' : 'hl'), x: i * bw + 1, y: T + (H - T - B) * (1 - c / max), width: bw - 2, height: (H - T - B) * c / max, rx: 2 }, hist);
        hover(r, `Bilan entre <b>${eur(x0)}</b> et <b>${eur(x0 + step)}</b><br>${c} parieurs sur 1 000`);
      });
      if (lo < 0 && hi > 0) {
        el('line', { class: 'ref', x1: X(0), x2: X(0), y1: 0, y2: H - B }, hist);
        el('text', { x: X(0), y: H - 6, 'text-anchor': 'middle' }, hist).textContent = '0 €';
      }
      el('text', { x: 0, y: H - 6 }, hist).textContent = eur(lo);
      el('text', { x: W, y: H - 6, 'text-anchor': 'end' }, hist).textContent = eur(hi);
    };
    const drawPath = (trace, n) => {
      path.innerHTML = '';
      const W = 640, H = 160, T = 12, B = 22, L = 56;
      path.setAttribute('viewBox', `0 0 ${W} ${H}`);
      const lo = Math.min(0, ...trace), hi = Math.max(0, ...trace), span = hi - lo || 1;
      const X = (i) => L + (W - L) * i / n, Y = (v) => T + (H - T - B) * (hi - v) / span;
      el('line', { class: 'base', x1: L, x2: W, y1: Y(0), y2: Y(0) }, path);
      el('text', { x: L - 8, y: Y(0) + 4, 'text-anchor': 'end' }, path).textContent = '0 €';
      el('text', { x: L - 8, y: Y(trace.at(-1)) + 4, 'text-anchor': 'end', class: 'val' }, path).textContent = eur(trace.at(-1));
      const line = el('path', { class: 'line ' + (trace.at(-1) >= 0 ? 'accent' : 'hot'), d: trace.map((v, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join('') }, path);
      el('text', { x: W, y: H - 4, 'text-anchor': 'end' }, path).textContent = `pari n° ${n}`;
      if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const len = line.getTotalLength();
        line.style.strokeDasharray = len; line.style.strokeDashoffset = len;
        line.getBoundingClientRect();
        line.style.transition = 'stroke-dashoffset 1.6s ease-out'; line.style.strokeDashoffset = 0;
      }
    };
    nIn.addEventListener('input', () => { nOut.textContent = nIn.value; });
    go.addEventListener('click', run);
    strat.addEventListener('change', run);
    nIn.addEventListener('change', run);
    run();
  }
})();
