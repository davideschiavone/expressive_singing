/* ============================================================
   EXPRESSIVE SINGING — MAIN JS
   ============================================================ */

// ---- LANGUAGE SYSTEM ----
// currentLang is set immediately (also in <head> inline script to avoid flash)
let currentLang = localStorage.getItem('lang') || 'en';

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);

  // Update button label
  const btn = document.getElementById('langBtn');
  if (btn) btn.textContent = lang === 'en' ? 'FR' : 'EN';

  // Update all elements that carry data-en / data-fr translations
  document.querySelectorAll('[data-en]').forEach(el => {
    const text = lang === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-fr');
    if (text !== null) el.textContent = text;
  });

  // Update textarea placeholders specifically
  document.querySelectorAll('[data-placeholder-en]').forEach(el => {
    el.placeholder = lang === 'fr'
      ? el.getAttribute('data-placeholder-fr')
      : el.getAttribute('data-placeholder-en');
  });

  // Update <html lang="..."> attribute for accessibility
  document.documentElement.lang = lang;
}

function toggleLang() {
  applyLang(currentLang === 'en' ? 'fr' : 'en');
}

// ---- NAVIGATION SCROLL ----
function initNav() {
  const nav = document.getElementById('mainNav');
  if (!nav) return;

  const onScroll = () => {
    if (window.scrollY > 40) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

// ---- HAMBURGER MENU ----
function initHamburger() {
  const toggle = document.getElementById('navToggle');
  const links = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    const isOpen = links.classList.contains('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // Close on link click
  links.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => links.classList.remove('open'));
  });
}

// ---- SCROLL FADE-IN ----
function initFadeIn() {
  const items = document.querySelectorAll('.fade-in');
  if (!items.length) return;

  // Fallback: ensure everything becomes visible after 400ms regardless
  setTimeout(() => {
    items.forEach(el => el.classList.add('visible'));
  }, 400);

  if (!('IntersectionObserver' in window)) {
    items.forEach(el => el.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });

  items.forEach(el => observer.observe(el));
}

// ---- ACTIVE NAV LINK ----
function initActiveNav() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === path || (path === '' && href === 'index.html')) {
      link.style.borderBottomWidth = '1px';
      link.style.borderBottomStyle = 'solid';
      link.style.borderBottomColor = 'var(--gold)';
      link.style.paddingBottom = '3px';
      link.style.color = 'var(--gold)';
    }
  });
}

// ---- CONTACT FORM ----
function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    const original = btn.textContent;
    btn.textContent = currentLang === 'fr' ? 'Envoyé ✓' : 'Sent ✓';
    btn.style.background = 'var(--forest)';
    btn.disabled = true;
    setTimeout(() => {
      btn.textContent = original;
      btn.style.background = '';
      btn.disabled = false;
      form.reset();
    }, 3000);
  });
}

// ---- INIT ALL ----
document.addEventListener('DOMContentLoaded', () => {
  applyLang(currentLang);
  initNav();
  initHamburger();
  initFadeIn();
  initActiveNav();
  initContactForm();
});
