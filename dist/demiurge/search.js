/* A small search over the reference: the pages' text is in search.json, read once, and matched in the browser. */
(function () {
  var script = document.currentScript;
  var input = document.getElementById('q');
  var hits = document.getElementById('hits');
  if (!script || !input || !hits) return;
  var index = null, loading = null;

  function load() {
    if (index) return Promise.resolve(index);
    if (!loading) {
      loading = fetch(script.getAttribute('data-index')).then(function (r) { return r.json(); }).then(function (j) { index = j; return j; });
    }
    return loading;
  }

  function words(q) { return q.toLowerCase().split(/\s+/).filter(function (w) { return w.length > 1; }); }

  function snippet(text, ws) {
    var low = text.toLowerCase(), at = -1;
    for (var i = 0; i < ws.length && at < 0; i++) at = low.indexOf(ws[i]);
    if (at < 0) return text.slice(0, 110);
    var from = Math.max(0, at - 50);
    return (from ? '…' : '') + text.slice(from, from + 130) + '…';
  }

  function search(q) {
    var ws = words(q);
    hits.textContent = '';
    if (!ws.length) { hits.classList.remove('open'); return; }
    var scored = [];
    index.forEach(function (p) {
      var t = p.t.toLowerCase(), x = p.x.toLowerCase(), score = 0, all = true;
      ws.forEach(function (w) {
        var inTitle = t.indexOf(w) >= 0, count = x.split(w).length - 1;
        if (!inTitle && !count) all = false;
        score += (inTitle ? 12 : 0) + Math.min(count, 10);
      });
      if (all) scored.push([score, p]);
    });
    scored.sort(function (a, b) { return b[0] - a[0]; });
    if (!scored.length) {
      var none = document.createElement('p');
      none.className = 'none';
      none.textContent = 'Nothing found. Try fewer or different words.';
      hits.appendChild(none);
    }
    scored.slice(0, 8).forEach(function (s) {
      var a = document.createElement('a');
      a.href = script.getAttribute('data-base') + s[1].u;
      var b = document.createElement('strong'); b.textContent = s[1].t;
      var d = document.createElement('span'); d.textContent = snippet(s[1].x, ws);
      a.appendChild(b); a.appendChild(d);
      hits.appendChild(a);
    });
    hits.classList.add('open');
  }

  input.addEventListener('input', function () { load().then(function () { search(input.value); }); });
  input.addEventListener('focus', function () { load(); if (input.value) hits.classList.add('open'); });
  document.addEventListener('click', function (e) { if (!e.target.closest || !e.target.closest('.search')) hits.classList.remove('open'); });
  input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { hits.classList.remove('open'); input.blur(); } });
})();
