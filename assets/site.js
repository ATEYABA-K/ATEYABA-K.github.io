// Comportements communs à toutes les pages : thème clair/sombre, apparition au scroll,
// compteurs, filtres de projets, copie de l'e-mail, barre de lecture.
(() => {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* navigation privée */ } },
  };

  // ---------- Thème ----------
  const saved = store.get('theme');
  if (saved) root.dataset.theme = saved;
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  document.querySelectorAll('.theme-toggle').forEach((b) => {
    const sync = () => { b.setAttribute('aria-pressed', isDark()); b.title = isDark() ? 'Passer en clair' : 'Passer en sombre'; };
    sync();
    b.addEventListener('click', () => {
      root.dataset.theme = isDark() ? 'light' : 'dark';
      store.set('theme', root.dataset.theme);
      sync();
      window.dispatchEvent(new Event('themechange'));
    });
  });

  // ---------- Compteurs ----------
  const countUp = (el) => {
    const m = el.textContent.match(/^([^\d]*)(\d+(?:[,\s]\d+)*)(.*)$/s);
    if (!m || reduce) return;
    const [, pre, num, post] = m;
    const dec = num.includes(',') ? num.split(',')[1].length : 0;
    const target = parseFloat(num.replace(/\s/g, '').replace(',', '.'));
    const t0 = performance.now(), dur = 1000;
    const fmt = (v) => v.toLocaleString('fr-FR', { minimumFractionDigits: dec, maximumFractionDigits: dec });
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / dur), v = target * (1 - Math.pow(1 - k, 3));
      el.textContent = pre + fmt(v) + post;
      if (k < 1) requestAnimationFrame(tick); else el.textContent = pre + num + post;
    };
    requestAnimationFrame(tick);
  };

  // ---------- Apparition au scroll ----------
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        e.target.querySelectorAll('.big-num, .off-num, .stat-n').forEach(countUp);
        io.unobserve(e.target);
      });
    }, { threshold: 0.12 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('in'));
  }

  // ---------- Filtres de projets ----------
  const chips = document.querySelectorAll('.filters button');
  chips.forEach((chip) => chip.addEventListener('click', () => {
    const f = chip.dataset.f;
    chips.forEach((c) => c.setAttribute('aria-pressed', c === chip));
    document.querySelectorAll('[data-tags]').forEach((card) => {
      card.hidden = f !== 'tous' && !card.dataset.tags.split(' ').includes(f);
    });
  }));

  // ---------- Cartes « chiffres » : retourner au clic ----------
  document.querySelectorAll('.fact-inner').forEach((b) => b.addEventListener('click', () => {
    const on = b.classList.toggle('flipped');
    b.setAttribute('aria-pressed', on);
  }));

  // ---------- Copier l'e-mail ----------
  document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const txt = b.dataset.copy, label = b.textContent;
    try { await navigator.clipboard.writeText(txt); b.textContent = 'Copié ✓'; }
    catch { window.location.href = 'mailto:' + txt; }
    setTimeout(() => { b.textContent = label; }, 1800);
  }));

  // ---------- Barre de lecture (pages d'étude) ----------
  const bar = document.querySelector('.progress-read');
  if (bar) {
    const upd = () => {
      const h = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = `scaleX(${h > 0 ? Math.min(1, scrollY / h) : 0})`;
    };
    addEventListener('scroll', upd, { passive: true }); upd();
  }

  console.log('%cVous lisez le code source ? On va bien s\'entendre. → alvinkouadio1@icloud.com', 'font:600 14px Inter,sans-serif;color:#d9542b');
})();
