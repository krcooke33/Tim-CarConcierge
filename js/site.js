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

/* ─── FAQ accordion (Process page) ────────────────────────── */

(function () {
  var questions = document.querySelectorAll('.faq-q');
  if (!questions.length) return;

  questions.forEach(function (q) {
    q.addEventListener('click', function () {
      var isOpen = q.getAttribute('aria-expanded') === 'true';
      q.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
    });
  });
})();

/* ─── Contact form (Contact page) ─────────────────────────── */
/* Builds a mailto: with all field data so a real email lands in
   Tim's inbox. Works on every browser, mobile and desktop, with no
   third-party form service required. The <form> still has a plain
   action="mailto:..." as a no-JS fallback. */

(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;

  var status   = document.getElementById('contact-form-status');
  var TO       = 'tim@andgarage.com';

  function setStatus(msg, kind) {
    if (!status) return;
    status.textContent = msg || '';
    status.classList.remove('is-success', 'is-error');
    if (kind) status.classList.add('is-' + kind);
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function trim(v) { return (v == null ? '' : String(v)).trim(); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var fields = {
      name:   form.querySelector('#cf-name'),
      email:  form.querySelector('#cf-email'),
      budget: form.querySelector('#cf-budget'),
      brief:  form.querySelector('#cf-brief')
    };

    /* Reset error state */
    Object.keys(fields).forEach(function (k) {
      var el = fields[k];
      if (el && el.parentNode) el.parentNode.classList.remove('has-error');
    });

    var name   = trim(fields.name && fields.name.value);
    var email  = trim(fields.email && fields.email.value);
    var budget = trim(fields.budget && fields.budget.value);
    var brief  = trim(fields.brief && fields.brief.value);

    var firstInvalid = null;
    function flag(el) {
      if (el && el.parentNode) el.parentNode.classList.add('has-error');
      if (!firstInvalid) firstInvalid = el;
    }

    if (!name)               flag(fields.name);
    if (!email || !isValidEmail(email)) flag(fields.email);
    if (!budget)             flag(fields.budget);
    if (!brief)              flag(fields.brief);

    if (firstInvalid) {
      setStatus('Please fill in every field with a valid email so Tim can write back.', 'error');
      try { firstInvalid.focus(); } catch (err) {}
      return;
    }

    var subject = 'Inquiry from ' + name + ' — The & Garage';
    var bodyLines = [
      'Name:   ' + name,
      'Email:  ' + email,
      'Budget: ' + budget,
      '',
      "What I'm chasing:",
      brief,
      '',
      '— Sent from the contact form on andgarage.com'
    ];
    var href = 'mailto:' + TO
      + '?subject=' + encodeURIComponent(subject)
      + '&body='    + encodeURIComponent(bodyLines.join('\n'));

    setStatus("Opening your email app… if nothing happens, email Tim directly at " + TO + ".", 'success');

    /* Use location.href so the OS handler picks it up reliably across
       browsers (window.open can be blocked or open a blank tab). */
    window.location.href = href;
  });
})();
