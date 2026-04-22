/* ═══════════════════════════════════════════════
   Portfolio — main.js
   ═══════════════════════════════════════════════ */

'use strict';

/* ── Loader ── */
(function initLoader() {
  const loader = document.getElementById('loader');
  if (!loader) return;

  window.addEventListener('load', () => {
    setTimeout(() => {
      loader.classList.add('hidden');
      loader.addEventListener('transitionend', () => loader.remove(), { once: true });
    }, 600);
  });
})();

/* ── Navbar scroll behaviour ── */
(function initNavbar() {
  const nav = document.getElementById('mainNav');
  if (!nav) return;

  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

/* ── Active nav link highlight on scroll ── */
(function initActiveLink() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('#mainNav .nav-link');

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach((link) => {
            link.classList.toggle('active', link.getAttribute('href') === '#' + id);
          });
        }
      });
    },
    { rootMargin: '-40% 0px -55% 0px' }
  );

  sections.forEach((s) => observer.observe(s));
})();

/* ── Scroll Reveal ── */
(function initReveal() {
  const elements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');
  if (!elements.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -60px 0px' }
  );

  elements.forEach((el) => observer.observe(el));
})();

/* ── Skill progress bars — animate on scroll ── */
(function initSkillBars() {
  const bars = document.querySelectorAll('.skill-progress-fill, .skill-bar-fill');
  if (!bars.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const bar = entry.target;
          const targetWidth = bar.dataset.width || 0;
          setTimeout(function () {
            bar.style.width = targetWidth + '%';
          }, 120);
          observer.unobserve(bar);
        }
      });
    },
    { threshold: 0.2 }
  );

  bars.forEach((bar) => observer.observe(bar));
})();

/* ── Back to Top ── */
(function initBackToTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

/* ── Smooth scroll for anchor links ── */
(function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href').slice(1);
      if (!targetId) return;
      const target = document.getElementById(targetId);
      if (!target) return;
      e.preventDefault();

      const collapse = document.querySelector('.navbar-collapse.show');
      if (collapse) {
        const toggler = document.querySelector('.navbar-toggler');
        if (toggler) toggler.click();
      }
      target.scrollIntoView({ behavior: 'smooth' });
    });
  });
})();

/* ── Navbar hamburger animation ── */
(function initHamburger() {
  const toggler = document.querySelector('.navbar-toggler');
  const collapseEl = document.getElementById('navbarNav');
  if (!toggler || !collapseEl) return;

  const spans = toggler.querySelectorAll('.toggler-icon span');

  collapseEl.addEventListener('show.bs.collapse', () => {
    if (spans[0]) spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
    if (spans[1]) spans[1].style.opacity = '0';
    if (spans[2]) spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
  });

  collapseEl.addEventListener('hide.bs.collapse', () => {
    spans.forEach((s) => {
      s.style.transform = '';
      s.style.opacity = '';
    });
  });
})();
