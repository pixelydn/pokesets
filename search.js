(function () {
  const input = document.querySelector('.search-bar');
  if (!input) return;
  const cards = document.querySelectorAll('.mon-card');
  input.addEventListener('input', function () {
    const q = this.value.toLowerCase();
    cards.forEach(function (card) {
      card.style.display = card.dataset.name.toLowerCase().includes(q) ? '' : 'none';
    });
  });
})();
