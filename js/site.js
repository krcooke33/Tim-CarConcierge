/* site.js — V1 interactions */

/* ─── Mobile nav toggle ───────────────────────────────────── */

(function () {
  var nav       = document.getElementById('site-nav');
  var hamburger = document.getElementById('nav-hamburger');
  var drawer    = document.getElementById('nav-drawer');

  if (!nav || !hamburger || !drawer) return;

  hamburger.addEventListener('click', function () {
    var isOpen = drawer.classList.toggle('is-open');
    nav.classList.toggle('nav-open', isOpen);
    hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  /* Close drawer when a link is tapped */
  drawer.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') {
      drawer.classList.remove('is-open');
      nav.classList.remove('nav-open');
      hamburger.setAttribute('aria-expanded', 'false');
    }
  });

  /* Close drawer on Escape */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
      drawer.classList.remove('is-open');
      nav.classList.remove('nav-open');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.focus();
    }
  });
})();
