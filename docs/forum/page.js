/* Foundation0 · Forum page.
   The forum itself is GitHub Discussions on this repository; this page renders its index from
   data/discussions.json: whether it is open, when the snapshot was taken, a category filter with counts,
   and the most recently active threads (title, category, author, replies, state). The posts stay on GitHub.
   Everything in the data file came from forum users, so every string goes through F0.esc.
   The HTML ships a prerendered copy of each marked part for readers without JavaScript. */
(function () {
  'use strict';
  var F0 = window.F0;
  var esc = F0.esc;

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }
  function day(ts) { return F0.fmtDate(String(ts).slice(0, 10)); }
  function stamp(ts) { return day(ts) + ', ' + String(ts).slice(11, 16) + ' UTC'; }

  function openHTML(d) {
    if (!d.enabled) {
      return '<p class="fo-soon"><b>Not open yet.</b> The forum opens when Discussions is switched on for the repository. ' +
        'Until then, raise anything in an <a href="https://github.com/Foundation-0/f0/issues">issue</a>.</p>';
    }
    return '<a class="btn primary" href="' + esc(d.url) + '">Open the forum <span class="arr" aria-hidden="true">&rarr;</span></a>' +
      '<a class="btn" href="' + esc(d.url) + '/new/choose">Start a thread <span class="arr" aria-hidden="true">&rarr;</span></a>';
  }

  function filterHTML(d) {
    if (!d.enabled || !d.categories.length) return '';
    var b = function (slug, name, n, on) {
      return '<button type="button" data-cat="' + esc(slug) + '" aria-pressed="' + on + '">' + esc(name) + ' <span class="n">' + n + '</span></button>';
    };
    return '<span class="fo-ctrl-l" id="fo-cats-l">Category //</span>' +
      '<div class="seg fo-seg" role="group" aria-labelledby="fo-cats-l">' + b('all', 'All', d.total, true) +
      d.categories.map(function (c) { return b(c.slug, c.name, c.count, false); }).join('') + '</div>';
  }

  function threadHTML(t, cats) {
    var c = cats[t.category] || { name: t.category || 'Uncategorised', answerable: false };
    var by = t.author
      ? 'by <a href="' + esc(t.author.url) + '">' + esc(t.author.login) + '</a>' + (t.author.agent ? ' <span class="fo-agent" title="Written by a GitHub app: an AI agent or a bot">Agent</span>' : '')
      : 'by a deleted account';
    var state = [];
    if (c.answerable && t.answered) state.push('<span class="badge v">Answered</span>');
    if (t.closed) state.push('<span class="badge n">Closed</span>');
    if (t.locked) state.push('<span class="badge n">Locked</span>');
    return '<li class="fo-t" data-cat="' + esc(t.category) + '">' +
      '<div class="fo-t-meta"><span class="fo-t-cat">' + esc(c.name) + '</span><time datetime="' + esc(t.updated) + '">' + day(t.updated) + '</time></div>' +
      '<div class="fo-t-body"><h3 class="fo-t-title"><a href="' + esc(t.url) + '">' + esc(t.title) + '</a></h3>' +
      '<p class="fo-t-by"><span>' + by + '</span><span>' + plural(t.comments, 'comment') + '</span>' +
      (t.upvotes ? '<span>' + plural(t.upvotes, 'upvote') + '</span>' : '') +
      '<span>started ' + day(t.created) + '</span>' + state.join('') + '</p></div></li>';
  }

  function emptyHTML(d) {
    return '<li class="fo-t fo-none"><p>' + (d.enabled
      ? 'No threads yet. <a href="' + esc(d.url) + '/new/choose">Start the first one.</a>'
      : 'No threads yet: the forum is not open.') + '</p></li>';
  }

  function statusText(d, shown) {
    if (!d.threads.length) return '';
    return 'Showing ' + plural(shown, 'thread') + ', from the ' + d.threads.length + ' most recently active of ' + d.total + '.';
  }

  function render(d) {
    var cats = {};
    d.categories.forEach(function (c) { cats[c.slug] = c; });
    $('#fo-open').innerHTML = openHTML(d);
    $('#fo-asof').textContent = 'Index changed ' + stamp(d.updated);
    $('#fo-filter').innerHTML = filterHTML(d);
    $('#fo-status').textContent = statusText(d, d.threads.length);
    $('#fo-list').innerHTML = d.threads.length ? d.threads.map(function (t) { return threadHTML(t, cats); }).join('') : emptyHTML(d);
    $('#fo-stamp').textContent = 'Forum index changed ' + d.updated.slice(0, 10) + ' · ' + plural(d.total, 'thread');

    $('#fo-filter').addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-cat]');
      if (!btn) return;
      var k = btn.getAttribute('data-cat'), shown = 0;
      $$('#fo-filter button').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      $$('#fo-list .fo-t[data-cat]').forEach(function (li) {
        var on = k === 'all' || li.getAttribute('data-cat') === k;
        li.hidden = !on;
        if (on) shown++;
      });
      $('#fo-status').textContent = statusText(d, shown) + (shown ? '' : ' None in this category among them.');
    });
  }

  F0.json(F0.root + 'data/discussions.json').then(render).catch(function (e) {
    $('#fo-status').textContent = 'The forum index could not be loaded (' + e.message + '). The forum itself is on GitHub.';
    if (window.console) console.error(e);
  });
})();
