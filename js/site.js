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
/* Posts the form to Web3Forms (a free hosted relay) so every
   submission lands in Tim's inbox — even for visitors whose browser
   has no mail handler configured. On success we redirect to the
   thank-you page. If Web3Forms isn't configured yet, or the request
   fails (offline, blocked, etc.), we fall back to a mailto: handoff
   so nothing is silently lost. */

(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;

  var status     = document.getElementById('contact-form-status');
  var TO         = 'tim@theandgarage.com';
  var THANKS_URL = '/contact/thanks/';
  var ENDPOINT   = 'https://api.web3forms.com/submit';
  var KEY_PLACEHOLDER = 'YOUR-WEB3FORMS-ACCESS-KEY-HERE';

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

  function getAccessKey() {
    var input = form.querySelector('input[name="access_key"]');
    return trim(input && input.value);
  }

  function buildMailtoHref(name, email, budget, brief) {
    var subject = 'Inquiry from ' + name + ' — The & Garage';
    var bodyLines = [
      'Name:   ' + name,
      'Email:  ' + email,
      'Budget: ' + budget,
      '',
      "What I'm chasing:",
      brief,
      '',
      '— Sent from the contact form on theandgarage.com'
    ];
    return 'mailto:' + TO
      + '?subject=' + encodeURIComponent(subject)
      + '&body='    + encodeURIComponent(bodyLines.join('\n'));
  }

  function fallbackToMailto(name, email, budget, brief) {
    setStatus("Opening your email app as a backup… if nothing happens, email Tim directly at " + TO + ".", 'success');
    window.location.href = buildMailtoHref(name, email, budget, brief);
  }

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

    /* Honeypot: if a bot filled the hidden "website" field, pretend
       success without sending — quietly drop the spam. */
    var honeypot = form.querySelector('input[name="website"]');
    if (honeypot && trim(honeypot.value)) {
      window.location.href = THANKS_URL;
      return;
    }

    var accessKey = getAccessKey();

    /* If Web3Forms isn't configured yet (placeholder key), or fetch
       isn't available, skip straight to the mailto fallback. */
    if (!accessKey || accessKey === KEY_PLACEHOLDER || typeof window.fetch !== 'function') {
      fallbackToMailto(name, email, budget, brief);
      return;
    }

    setStatus('Sending your note to Tim…', '');

    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    var payload = new FormData();
    payload.append('access_key', accessKey);
    payload.append('subject', 'Inquiry from ' + name + ' — The & Garage');
    payload.append('from_name', 'The & Garage contact form');
    payload.append('name', name);
    payload.append('email', email);
    payload.append('budget', budget);
    payload.append('brief', brief);
    payload.append('message',
      'Name:   ' + name + '\n' +
      'Email:  ' + email + '\n' +
      'Budget: ' + budget + '\n\n' +
      "What I'm chasing:\n" + brief
    );

    fetch(ENDPOINT, {
      method: 'POST',
      body: payload,
      headers: { 'Accept': 'application/json' }
    }).then(function (res) {
      return res.json().then(function (data) {
        return { ok: res.ok && data && data.success, data: data };
      }).catch(function () {
        return { ok: res.ok, data: null };
      });
    }).then(function (result) {
      if (result.ok) {
        window.location.href = THANKS_URL;
      } else {
        if (submitBtn) submitBtn.disabled = false;
        fallbackToMailto(name, email, budget, brief);
      }
    }).catch(function () {
      if (submitBtn) submitBtn.disabled = false;
      fallbackToMailto(name, email, budget, brief);
    });
  });
})();
