/*
 * Mermaid needs `securityLevel: "loose"` for the `click` directives in
 * docs/architecture/the-loop.md to become real links.
 *
 * Material lazy-loads mermaid@11 itself and calls `mermaid.initialize` with
 * `startOnLoad: false` and no `securityLevel`, so mermaid's default -- `strict`
 * -- applies. Under `strict`, click handlers are disabled and HTML in node
 * labels is encoded rather than rendered, which turns an interactive diagram
 * into a static picture with visible markup in it.
 *
 * Material's loader is what defines `window.mermaid`, and it runs after this
 * file. So rather than racing it, this watches for the global to appear, wraps
 * `initialize` once, and folds the option in -- leaving every choice Material
 * makes (its theme variables in particular) untouched.
 *
 * The poll is deliberately bounded. If mermaid never loads -- offline, a
 * blocked CDN, a Material release that stops bundling it -- this gives up
 * quietly instead of spinning for the life of the page. The diagram still
 * renders; only the click-through is lost, and the page carries a plain link
 * index underneath for exactly that case.
 */
(function () {
  'use strict';

  var POLL_MS = 50;
  var GIVE_UP_MS = 10000;
  var waited = 0;

  var timer = setInterval(function () {
    waited += POLL_MS;

    if (typeof window.mermaid === 'undefined') {
      if (waited >= GIVE_UP_MS) {
        clearInterval(timer);
      }
      return;
    }

    clearInterval(timer);

    var original = window.mermaid.initialize;
    if (typeof original !== 'function' || original.__loopPatched) {
      return;
    }

    var patched = function (config) {
      var merged = Object.assign({}, config || {}, { securityLevel: 'loose' });
      return original.call(window.mermaid, merged);
    };
    patched.__loopPatched = true;
    window.mermaid.initialize = patched;
  }, POLL_MS);
})();
