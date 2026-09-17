export const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export function isoDate(daysFromToday) {
  const value = new Date();
  value.setHours(12, 0, 0, 0);
  value.setDate(value.getDate() + daysFromToday);
  return value.toISOString().slice(0, 10);
}

export function formatDate(value, options = {}) {
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC', ...options,
  }).format(new Date(`${value}T00:00:00Z`));
}

export function formatMoney(value) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', maximumFractionDigits: 0,
  }).format(value);
}

export function escapeHTML(value) {
  const node = document.createElement('div');
  node.textContent = String(value);
  return node.innerHTML;
}

export function showToast(message) {
  const toast = document.querySelector('#toast');
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 3200);
}

export function setBusy(button, busy, busyLabel = 'Please wait…') {
  if (!button.dataset.originalLabel) button.dataset.originalLabel = button.innerHTML;
  button.disabled = busy;
  button.innerHTML = busy ? busyLabel : button.dataset.originalLabel;
}

export async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
  return data;
}
