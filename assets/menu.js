/* The language menu is a <details>: it closes when something else is clicked, or on Escape. */
(function () {
  var menu = document.querySelector('.langmenu');
  if (!menu) return;
  document.addEventListener('click', function (e) { if (!menu.contains(e.target)) menu.removeAttribute('open'); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.hasAttribute('open')) { menu.removeAttribute('open'); menu.querySelector('summary').focus(); }
  });
})();
