(() => {
  const frame = document.querySelector('.instrument');
  if (!frame) return;
  const data = JSON.parse(document.getElementById('instrument-data').textContent);
  const tabs = [...frame.querySelectorAll('[data-view]')];
  const axis = frame.querySelector('.plot-axis');
  const plot = frame.querySelector('.plot-bars');
  const legend = frame.querySelector('.data-legend');
  const source = frame.querySelector('.source');
  const heading = frame.querySelector('.instrument-title');
  const description = frame.querySelector('.instrument-readout p');
  const value = frame.querySelector('.instrument-readout strong');
  const link = frame.querySelector('.instrument-link');
  let active;
  const numeric = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 1 });

  function node(tag, className, label) {
    const item = document.createElement(tag);
    item.className = className;
    if (label !== undefined) item.textContent = label;
    return item;
  }

  function label(number) {
    return numeric.format(number) + (active.unit === '%' ? ' %' : '');
  }

  function choose(index) {
    const detail = active.items[index];
    value.textContent = detail.summary ?? detail.values.map((number, i) =>
      active.series[i].short + ' ' + label(number)
    ).join(' · ');
    description.textContent = detail.reading;
    for (const [i, button] of [...plot.querySelectorAll('button')].entries()) {
      button.setAttribute('aria-pressed', String(i === index));
    }
  }

  function render(key) {
    active = data[key];
    for (const tab of tabs) tab.setAttribute('aria-pressed', String(tab.dataset.view === key));
    source.textContent = active.source;
    heading.textContent = active.title;
    link.href = active.link;
    axis.replaceChildren(...[3, 2, 1, 0].map(i => node('span', '', label(active.max * i / 3))));
    plot.style.setProperty('--count', active.items.length);
    legend.replaceChildren(...active.series.map(series => {
      const tag = node('span', '', series.name);
      tag.style.setProperty('--swatch', series.color);
      return tag;
    }));
    plot.replaceChildren(...active.items.map((item, index) => {
      const button = node('button', 'plot-mark');
      button.type = 'button';
      const seriesText = item.values.map((number, i) => active.series[i].name + ' ' + label(number)).join(', ');
      button.setAttribute('aria-label', item.label + ' : ' + seriesText);
      button.title = seriesText;
      const columns = node('span', 'plot-columns');
      columns.setAttribute('aria-hidden', 'true');
      for (const [i, number] of item.values.entries()) {
        const bar = node('span', 'plot-bar');
        bar.style.setProperty('--height', number / active.max * 100 + '%');
        bar.style.setProperty('--swatch', active.series[i].color);
        columns.append(bar);
      }
      button.append(columns, node('span', 'plot-label', item.label));
      button.addEventListener('click', () => choose(index));
      return button;
    }));
    choose(active.selected);
  }

  for (const tab of tabs) tab.addEventListener('click', () => render(tab.dataset.view));
  render(tabs[0].dataset.view);
  frame.querySelector('.instrument-tabs').hidden = false;
  frame.querySelector('.plot-hint').hidden = false;

  const landing = document.querySelector('.landing');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  function highlight(event) {
    if (motion.matches) return;
    const bounds = landing.getBoundingClientRect();
    landing.style.setProperty('--px', event.clientX - bounds.left + 'px');
    landing.style.setProperty('--py', event.clientY - bounds.top + 'px');
  }
  landing.addEventListener('pointermove', event => {
    if (event.pointerType !== 'touch') highlight(event);
  }, {passive: true});
  landing.addEventListener('pointerdown', highlight, {passive: true});
})();
