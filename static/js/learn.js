(function () {
  const filters = Array.from(document.querySelectorAll('[data-learn-filter]'));
  const cards = Array.from(document.querySelectorAll('[data-learn-category]'));
  const empty = document.querySelector('[data-learn-empty]');
  if (!filters.length || !cards.length) return;

  const applyFilter = (filter) => {
    let visible = 0;
    cards.forEach((card) => {
      const show = filter === 'all' || card.dataset.learnCategory === filter;
      card.hidden = !show;
      if (show) {
        visible += 1;
        card.classList.remove('is-filtered-in');
        window.requestAnimationFrame(() => card.classList.add('is-filtered-in'));
      }
    });
    if (empty) empty.hidden = visible !== 0;
  };

  filters.forEach((button) => {
    button.addEventListener('click', () => {
      filters.forEach((item) => item.classList.toggle('is-active', item === button));
      applyFilter(button.dataset.learnFilter);
    });
  });
})();