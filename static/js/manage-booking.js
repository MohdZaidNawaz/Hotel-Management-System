import { state } from './state.js';
import {
  apiRequest, csrfToken, escapeHTML, formatDate, formatMoney, setBusy, showToast,
} from './utils.js';

const manageModal = document.querySelector('#manage-modal');
const lookupForm = document.querySelector('#lookup-form');

function renderManagedBooking(booking) {
  const container = document.querySelector('#managed-booking');
  const isCancelled = booking.status === 'cancelled';
  container.innerHTML = `
    <span class="booking-status ${isCancelled ? 'cancelled' : ''}">${escapeHTML(booking.status)}</span>
    <h3>${escapeHTML(booking.room_name)}</h3>
    <dl>
      <div><dt>Confirmation</dt><dd>${escapeHTML(booking.confirmation_code)}</dd></div>
      <div><dt>Guest</dt><dd>${escapeHTML(booking.guest_name)}</dd></div>
      <div><dt>Dates</dt><dd>${formatDate(booking.check_in, { year: undefined })} — ${formatDate(booking.check_out, { year: undefined })}</dd></div>
      <div><dt>Total</dt><dd>${formatMoney(booking.total)}</dd></div>
    </dl>
    ${isCancelled ? '' : '<button class="cancel-button" type="button" data-cancel-booking>Cancel this reservation</button>'}`;
  container.hidden = false;
  container.querySelector('[data-cancel-booking]')?.addEventListener('click', cancelBooking);
}

async function lookupReservation(event) {
  event.preventDefault();
  const button = lookupForm.querySelector('button[type="submit"]');
  const query = new URLSearchParams(new FormData(lookupForm));
  const errorNode = document.querySelector('#lookup-error');
  errorNode.textContent = '';
  setBusy(button, true, 'Looking it up…');
  try {
    const data = await apiRequest(`/api/reservations/lookup?${query}`);
    state.managedReservation = data.reservation;
    renderManagedBooking(state.managedReservation);
  } catch (error) {
    errorNode.textContent = error.message;
    document.querySelector('#managed-booking').hidden = true;
  } finally {
    setBusy(button, false);
  }
}

async function cancelBooking(event) {
  if (!state.managedReservation || !window.confirm('Cancel this reservation? This action cannot be undone.')) return;
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const data = await apiRequest(`/api/reservations/${encodeURIComponent(state.managedReservation.confirmation_code)}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
      body: JSON.stringify({ email: state.managedReservation.email }),
    });
    state.managedReservation.status = 'cancelled';
    renderManagedBooking(state.managedReservation);
    showToast(data.message);
  } catch (error) {
    showToast(error.message);
    button.disabled = false;
  }
}

export function initializeManageBooking() {
  document.querySelectorAll('[data-open-manage]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelector('#lookup-error').textContent = '';
      manageModal.showModal();
    });
  });
  lookupForm.addEventListener('submit', lookupReservation);
}
