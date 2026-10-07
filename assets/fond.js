// Fond interactif : un nuage de points qui dérive lentement, comme un scatter plot vivant.
// Sous la souris, une "loupe" allume les points, les relie et ajuste une droite de régression en direct.
// Un clic envoie une onde qui écarte les points. Respecte prefers-reduced-motion et le thème.
(() => {
  const canvas = document.getElementById('bg');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const LENS = 170;
  let W = 0, H = 0, dpr = 1, pts = [], mouse = null, ripples = [], colors = {}, raf = null, scrollY = 0;

  const readColors = () => {
    const s = getComputedStyle(document.documentElement);
    colors = { ink: s.getPropertyValue('--ink-soft').trim(), hot: s.getPropertyValue('--hot').trim(), grid: s.getPropertyValue('--border').trim() };
  };

  const resize = () => {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = innerWidth; H = innerHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.min(170, Math.round(W * H / 9000));
    // Les points suivent une légère tendance (y augmente avec x) : il y a toujours une droite à trouver.
    pts = Array.from({ length: n }, () => {
      const x = Math.random() * W;
      const y = H * (0.85 - 0.6 * x / W) + (Math.random() - .5) * H * 0.9;
      return { x, y: (y + H) % H, vx: (Math.random() - .5) * .18, vy: (Math.random() - .5) * .18, r: 1.2 + Math.random() * 1.4 };
    });
  };

  const grid = () => {
    ctx.strokeStyle = colors.grid; ctx.globalAlpha = .55; ctx.lineWidth = 1;
    const step = 96, off = -(scrollY * .15) % step;
    ctx.beginPath();
    for (let x = step; x < W; x += step) { ctx.moveTo(x + .5, 0); ctx.lineTo(x + .5, H); }
    for (let y = off; y < H; y += step) { ctx.moveTo(0, y + .5); ctx.lineTo(W, y + .5); }
    ctx.stroke(); ctx.globalAlpha = 1;
  };

  const frame = () => {
    ctx.clearRect(0, 0, W, H);
    grid();
    const near = [];
    for (const p of pts) {
      if (!reduce) {
        p.x += p.vx; p.y += p.vy;
        for (const r of ripples) {
          const dx = p.x - r.x, dy = p.y - r.y, d = Math.hypot(dx, dy) || 1;
          if (Math.abs(d - r.rad) < 30) { p.x += dx / d * 2.2 * r.life; p.y += dy / d * 2.2 * r.life; }
        }
        if (p.x < -10) p.x = W + 10; if (p.x > W + 10) p.x = -10;
        if (p.y < -10) p.y = H + 10; if (p.y > H + 10) p.y = -10;
      }
      const py = p.y - (scrollY * .25) % H, y = py < -10 ? py + H : py;
      let d = Infinity;
      if (mouse) d = Math.hypot(p.x - mouse.x, y - mouse.y);
      const lit = d < LENS;
      if (lit) near.push({ x: p.x, y, d });
      ctx.globalAlpha = lit ? .35 + .65 * (1 - d / LENS) : .32;
      ctx.fillStyle = lit ? colors.hot : colors.ink;
      ctx.beginPath(); ctx.arc(p.x, y, lit ? p.r + 1.2 : p.r, 0, Math.PI * 2); ctx.fill();
    }

    if (mouse && near.length) {
      // Relie chaque point allumé à ses deux voisins les plus proches.
      ctx.strokeStyle = colors.hot; ctx.lineWidth = 1;
      for (const a of near) {
        near.map((b) => [b, Math.hypot(a.x - b.x, a.y - b.y)]).filter(([, d]) => d > 0)
          .sort((u, v) => u[1] - v[1]).slice(0, 2).forEach(([b, d]) => {
            ctx.globalAlpha = .25 * (1 - a.d / LENS);
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          });
      }
      // Droite de régression (moindres carrés) sur les points de la loupe.
      if (near.length >= 4) {
        const n = near.length, mx = near.reduce((s, p) => s + p.x, 0) / n, my = near.reduce((s, p) => s + p.y, 0) / n;
        let sxy = 0, sxx = 0;
        for (const p of near) { sxy += (p.x - mx) * (p.y - my); sxx += (p.x - mx) ** 2; }
        const slope = sxx ? sxy / sxx : 0, ang = Math.atan(slope), L = LENS * .95;
        ctx.globalAlpha = .7; ctx.lineWidth = 1.6; ctx.setLineDash([6, 5]);
        ctx.beginPath(); ctx.moveTo(mx - Math.cos(ang) * L, my - Math.sin(ang) * L); ctx.lineTo(mx + Math.cos(ang) * L, my + Math.sin(ang) * L); ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = .75; ctx.fillStyle = colors.ink; ctx.font = '500 11px "JetBrains Mono", monospace';
        ctx.fillText(`n = ${n} · pente = ${(-slope).toFixed(2).replace(".", ",")}`, mouse.x + 16, mouse.y + LENS * .55);
      }
      ctx.globalAlpha = .22; ctx.strokeStyle = colors.ink; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(mouse.x, mouse.y, LENS, 0, Math.PI * 2); ctx.stroke();
    }

    ripples = ripples.filter((r) => (r.rad += 6, r.life -= .02) > 0);
    for (const r of ripples) {
      ctx.globalAlpha = r.life * .5; ctx.strokeStyle = colors.hot; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(r.x, r.y, r.rad, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.globalAlpha = 1;
    raf = reduce ? null : requestAnimationFrame(frame);
  };

  const redrawIfStatic = () => { if (reduce) frame(); };
  addEventListener('resize', () => { resize(); redrawIfStatic(); });
  addEventListener('scroll', () => { scrollY = window.scrollY; redrawIfStatic(); }, { passive: true });
  addEventListener('pointermove', (e) => { if (e.pointerType === 'mouse') { mouse = { x: e.clientX, y: e.clientY }; redrawIfStatic(); } });
  document.addEventListener('pointerleave', () => { mouse = null; redrawIfStatic(); });
  addEventListener('pointerdown', (e) => {
    if (reduce || e.target.closest('a, button, input, svg, .card')) return;
    ripples.push({ x: e.clientX, y: e.clientY, rad: 0, life: 1 });
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { cancelAnimationFrame(raf); raf = null; } else if (!reduce && !raf) raf = requestAnimationFrame(frame);
  });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { readColors(); redrawIfStatic(); });

  readColors(); resize(); frame();
})();
