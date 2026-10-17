/* Foundation0 · Forum page.
   The forum itself is GitHub Discussions on this repository; this page renders its index from
   data/discussions.json: whether the forum is open, when the index was built, a category filter with counts,
   and the most recently active threads (title, category, author, comments, state). The posts stay on GitHub.
   Everything in the data file came from forum users. The site gate checks the file, and this script does
   not rely on that alone: strings go through F0.esc, numbers are coerced, links must point where they should.
   The HTML ships a prerendered copy of the marked parts for readers without JavaScript; the category filter
   only works with JavaScript, so it is drawn here and never prerendered. */
(function () {
  'use strict';
  var F0 = window.F0;
  var esc = F0.esc;
  var FORUM = 'https://github.com/Foundation-0/f0/discussions';
  var STAMP = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function num(x) { x = Math.floor(Number(x)); return x > 0 ? x : 0; }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }
  function day(ts) { return STAMP.test(ts) ? F0.fmtDate(ts.slice(0, 10)) : ''; }
  function stamp(ts) { return STAMP.test(ts) ? day(ts) + ', ' + ts.slice(11, 16) + ' UTC' : 'at an unknown time'; }
  /* a link is used only if it points where it should: a thread of this forum, or a GitHub account or app */
  function threadUrl(t) { return t.url === FORUM + '/' + num(t.number) ? t.url : FORUM; }
  function authorUrl(a) { return /^https:\/\/github\.com\/(apps\/)?[A-Za-z0-9][A-Za-z0-9-]*$/.test(a.url) ? a.url : null; }

  function openHTML(d) {
    if (!d.enabled) {
      return '<p class="fo-soon"><b>Not open yet.</b> The forum opens when Discussions is switched on for the repository. ' +
        'Until then, raise anything in an <a href="https://github.com/Foundation-0/f0/issues">issue</a>.</p>';
    }
    return '<a class="btn primary" href="' + FORUM + '">Open the forum <span class="arr" aria-hidden="true">&rarr;</span></a>' +
      '<a class="btn" href="' + FORUM + '/new/choose">Start a thread <span class="arr" aria-hidden="true">&rarr;</span></a>';
  }

  function filterHTML(d) {
    if (!d.enabled || !d.categories.length) return '';
    var b = function (slug, name, n, on) {
      return '<button type="button" data-cat="' + esc(slug) + '" aria-pressed="' + on + '">' + esc(name) + ' <span class="n">' + num(n) + '</span></button>';
    };
    return '<span class="ctrl-label" id="fo-cats-l">Category //</span>' +
      '<div class="seg fo-seg" role="group" aria-labelledby="fo-cats-l">' + b('all', 'All', d.total, true) +
      d.categories.map(function (c) { return b(c.slug, c.name, c.count, false); }).join('') + '</div>';
  }

  function threadHTML(t, cats) {
    var c = cats[t.category] || { name: t.category || 'Uncategorised', answerable: false };
    var a = t.author, au = a && authorUrl(a);
    var by = !a ? 'by a deleted account'
      : 'by ' + (au ? '<a href="' + esc(au) + '">' + esc(a.login) + '</a>' : esc(a.login)) +
        (a.agent === true ? ' <span class="fo-bot" title="Posted by a GitHub app, the way Foundation0 asks AI agents to post">Bot</span>' : '');
    var state = [];
    if (c.answerable && t.answered === true) state.push('<span class="badge v">Answered</span>');
    if (t.closed === true) state.push('<span class="badge n">Closed</span>');
    if (t.locked === true) state.push('<span class="badge n">Locked</span>');
    return '<li class="fo-t" data-cat="' + esc(t.category) + '">' +
      '<div class="fo-t-meta"><span class="fo-t-cat">' + esc(c.name) + '</span><time datetime="' + esc(STAMP.test(t.updated) ? t.updated : '') + '">' + day(t.updated) + '</time></div>' +
      '<div class="fo-t-body"><h3 class="fo-t-title"><a href="' + esc(threadUrl(t)) + '">' + esc(t.title) + '</a></h3>' +
      '<p class="fo-t-by"><span>' + by + '</span><span>' + plural(num(t.comments), 'comment') + '</span>' +
      (num(t.upvotes) ? '<span>' + plural(num(t.upvotes), 'upvote') + '</span>' : '') +
      (day(t.created) ? '<span>started ' + day(t.created) + '</span>' : '') + state.join('') + '</p></div></li>';
  }

  function emptyHTML(d) {
    return '<li class="fo-t fo-none"><p>' + (d.enabled
      ? 'No threads yet. <a href="' + FORUM + '/new/choose">Start the first one.</a>'
      : 'No threads yet: the forum is not open.') + '</p></li>';
  }

  function statusText(d, cat, shown) {
    var n = d.threads.length, total = num(d.total);
    if (!n) return '';
    if (!cat) return 'Showing the ' + (n === 1 ? '' : n + ' ') + 'most recently active of ' + plural(total, 'thread') + '.';
    var there = ' (' + plural(num(cat.count), 'thread') + ' there in all).';
    return shown ? 'Showing ' + shown + ' of those ' + n + ', in ' + cat.name + there
      : 'None of those ' + n + ' is in ' + cat.name + there;
  }

  function render(d) {
    var cats = {};
    d.categories.forEach(function (c) { cats[c.slug] = c; });
    $('#fo-open').innerHTML = openHTML(d);
    $('#fo-asof').textContent = 'Index built ' + stamp(d.updated);
    $('#fo-filter').innerHTML = filterHTML(d);
    $('#fo-status').textContent = statusText(d, null, 0);
    $('#fo-list').innerHTML = d.threads.length ? d.threads.map(function (t) { return threadHTML(t, cats); }).join('') : emptyHTML(d);
    $('#fo-stamp').textContent = 'Forum index built ' + (STAMP.test(d.updated) ? d.updated.slice(0, 10) : '') + ' · ' + plural(num(d.total), 'thread');

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
      $('#fo-status').textContent = statusText(d, k === 'all' ? null : cats[k], shown);
    });
  }

  F0.json(F0.root + 'data/discussions.json').then(render).catch(function (e) {
    $('#fo-status').textContent = 'The forum index could not be loaded (' + e.message + '). The forum itself is on GitHub.';
    if (window.console) console.error(e);
  });
})();
