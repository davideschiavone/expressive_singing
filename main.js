/* ============================================================
   EXPRESSIVE SINGING — MAIN JS
   ============================================================ */

// ---- LANGUAGE SYSTEM ----
const TRANSLATIONS = {
  en: {
    'nav.association': 'Association',
    'nav.company': 'Company',
    'nav.classes': 'Classes',
    'nav.events': 'Events',
    'nav.retreats': 'Retreats',
    'nav.blog': 'Blog',
    'nav.contact': 'Contact',
  },
  fr: {
    'nav.association': 'Association',
    'nav.company': 'Compagnie',
    'nav.classes': 'Cours',
    'nav.events': 'Événements',
    'nav.retreats': 'Retraites',
    'nav.blog': 'Blog',
    'nav.contact': 'Contact',
  }
};

let currentLang = localStorage.getItem('lang') || 'en';

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  const btn = document.getElementById('langBtn');
  if (btn) btn.textContent = lang === 'en' ? 'FR' : 'EN';

  // Update all [data-en] / [data-fr] elements
  document.querySelectorAll('[data-en]').forEach(el => {
    el.textContent = lang === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-fr');
  });

  // Update HTML lang attribute
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

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

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
