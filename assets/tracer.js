/* Word tracer: reveal sound laws one at a time.  Without JavaScript every step is visible. */
(function () {
  var root = document.querySelector('[data-tracer]');
  if (!root) return;
  document.documentElement.classList.add('js');

  var articles = [].slice.call(root.querySelectorAll('.trace'));
  var buttons = [].slice.call(root.querySelectorAll('[data-word]')).filter(function (b) { return b.tagName === 'BUTTON'; });
  var next = root.querySelector('[data-act="next"]');
  var all = root.querySelector('[data-act="all"]');
  var again = root.querySelector('[data-act="reset"]');
  var current = null, shown = 1;

  function steps() { return [].slice.call(current.querySelectorAll('.step')); }
  function chain() { return current.querySelector('.chain'); }

  function paint() {
    var s = steps();
    s.forEach(function (el, i) { el.hidden = i >= shown; });
    var done = shown >= s.length;
    next.disabled = done;
    all.disabled = done;
    chain().hidden = !done;
    var last = s[Math.min(shown, s.length) - 1];
    if (last && shown > 1) { last.classList.add('fresh'); setTimeout(function () { last.classList.remove('fresh'); }, 900); }
  }

  function choose(name) {
    current = articles.filter(function (a) { return a.getAttribute('data-word') === name; })[0];
    articles.forEach(function (a) { a.hidden = a !== current; });
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-word') === name ? 'true' : 'false'); });
    shown = 1;
    paint();
  }

  buttons.forEach(function (b) { b.addEventListener('click', function () { choose(b.getAttribute('data-word')); }); });
  next.addEventListener('click', function () { shown = Math.min(shown + 1, steps().length); paint(); });
  all.addEventListener('click', function () { shown = steps().length; paint(); });
  again.addEventListener('click', function () { shown = 1; paint(); });

  choose(buttons[0].getAttribute('data-word'));
})();
