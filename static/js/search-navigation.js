export function focusSearch() {
  document.querySelector('#reserve').scrollIntoView({ behavior: 'smooth', block: 'center' });
  window.setTimeout(() => document.querySelector('#check-in').focus(), 450);
}
