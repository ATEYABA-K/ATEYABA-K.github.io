const demo = document.querySelector('.decision-demo');
const options = demo.querySelector('.decision-options');
options.hidden = false;
options.addEventListener('click', (event) => {
  const button = event.target.closest('[data-choice]');
  if (!button) return;
  for (const choice of options.querySelectorAll('[data-choice]')) {
    choice.setAttribute('aria-pressed', String(choice === button));
  }
  for (const panel of demo.querySelectorAll('[data-panel]')) {
    panel.hidden = panel.dataset.panel !== button.dataset.choice;
  }
});
