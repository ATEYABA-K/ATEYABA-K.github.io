const filters = document.querySelector('.filters');
const cards = document.querySelectorAll('[data-category]');
filters.hidden = false;
filters.addEventListener('click', ({target}) => {
  const button = target.closest('button');
  if (!button) return;
  const selected = button.dataset.filter;
  for (const filter of filters.querySelectorAll('button')) {
    filter.setAttribute('aria-pressed', String(filter === button));
  }
  let visible = 0;
  for (const card of cards) {
    card.hidden = selected !== 'Tous' && card.dataset.category !== selected;
    visible += Number(!card.hidden);
  }
  document.querySelector('#project-count').textContent =
    visible + (visible === 1 ? ' projet affiché' : ' projets affichés');
});
