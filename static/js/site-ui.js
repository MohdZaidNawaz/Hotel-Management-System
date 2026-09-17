import { showToast } from './utils.js';

function initializeModalControls() {
  document.querySelectorAll('[data-close-modal]').forEach((button) => {
    button.addEventListener('click', () => button.closest('dialog').close());
  });
  document.querySelectorAll('dialog').forEach((dialog) => {
    dialog.addEventListener('click', (event) => {
      const bounds = dialog.getBoundingClientRect();
      const isBackdrop = event.clientX < bounds.left
        || event.clientX > bounds.right
        || event.clientY < bounds.top
        || event.clientY > bounds.bottom;
      if (isBackdrop) dialog.close();
    });
  });
}

function initializeNewsletter() {
  document.querySelector('#newsletter-form').addEventListener('submit', (event) => {
    event.preventDefault();
    showToast('You’re on the list. A little sunshine is on its way.');
    event.currentTarget.reset();
  });
}

function initializeMenu() {
  const menuButton = document.querySelector('.menu-button');
  menuButton.addEventListener('click', () => {
    const open = document.querySelector('.site-header').classList.toggle('menu-open');
    menuButton.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('.desktop-nav a').forEach((link) => link.addEventListener('click', () => {
    document.querySelector('.site-header').classList.remove('menu-open');
    menuButton.setAttribute('aria-expanded', 'false');
  }));
}

function initializeRevealAnimations() {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));
}

export function initializeSiteUI() {
  initializeModalControls();
  initializeNewsletter();
  initializeMenu();
  initializeRevealAnimations();
}
