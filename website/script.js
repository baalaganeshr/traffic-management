(function(){
  const year = document.getElementById('year');
  if (year) {
    year.textContent = new Date().getFullYear();
  }

  const root = document.documentElement;
  let raf;
  window.addEventListener('mousemove', (event) => {
    if (raf) window.cancelAnimationFrame(raf);
    raf = window.requestAnimationFrame(() => {
      root.style.setProperty('--mx', event.clientX + 'px');
      root.style.setProperty('--my', event.clientY + 'px');
    });
  }, { passive: true });

  const nav = document.querySelector('[data-nav]');
  const toggle = nav ? nav.querySelector('.nav__toggle') : null;
  const links = nav ? nav.querySelector('.nav__links') : null;

  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      links.classList.toggle('nav__links--open', !expanded);
    });

    links.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', () => {
        toggle.setAttribute('aria-expanded', 'false');
        links.classList.remove('nav__links--open');
      });
    });
  }

  if (links) {
    const navAnchors = Array.from(links.querySelectorAll('a[href^="#"]'));
    const targets = navAnchors
      .map((anchor) => document.querySelector(anchor.getAttribute('href')))
      .filter(Boolean);

    if (targets.length) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          const id = entry.target.id;
          const active = navAnchors.find((anchor) => anchor.getAttribute('href') === '#' + id);
          if (!active) return;
          if (entry.isIntersecting) {
            navAnchors.forEach((anchor) => anchor.classList.remove('is-active'));
            active.classList.add('is-active');
          }
        });
      }, { rootMargin: '-40% 0px -40% 0px', threshold: 0.3 });

      targets.forEach((section) => observer.observe(section));
    }
  }
})();
