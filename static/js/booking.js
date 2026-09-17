import { focusSearch } from './search-navigation.js';
import { state } from './state.js';
import {
  apiRequest, csrfToken, escapeHTML, formatDate, formatMoney, setBusy, showToast,
} from './utils.js';

const bookingModal = document.querySelector('#booking-modal');
const confirmationModal = document.querySelector('#confirmation-modal');
const reservationForm = document.querySelector('#reservation-form');
const bookingSummary = document.querySelector('.booking-summary');

export function openBooking(roomCode) {
  if (!state.activeSearch) return focusSearch();
  state.activeRoom = state.activeSearch.rooms.find((room) => room.code === roomCode);
  if (!state.activeRoom) return;

  document.querySelector('#booking-room-code').value = state.activeRoom.code;
  bookingSummary.dataset.roomVariant = state.activeRoom.image_variant;
  document.querySelector('#summary-room').textContent = state.activeRoom.name;
  document.querySelector('#summary-in').textContent = formatDate(state.activeSearch.check_in);
  document.querySelector('#summary-out').textContent = formatDate(state.activeSearch.check_out);
  document.querySelector('#summary-rate-label').textContent = `${formatMoney(state.activeRoom.nightly_rate)} × ${state.activeSearch.nights} night${state.activeSearch.nights === 1 ? '' : 's'}`;
  document.querySelector('#summary-subtotal').textContent = formatMoney(state.activeRoom.subtotal);
  document.querySelector('#summary-taxes').textContent = formatMoney(state.activeRoom.taxes);
  document.querySelector('#summary-total').textContent = formatMoney(state.activeRoom.total);
  document.querySelector('#reservation-error').textContent = '';
  bookingModal.showModal();
}

function showConfirmation(reservation) {
  document.querySelector('#confirmed-guest').textContent = reservation.guest_name.split(' ')[0];
  document.querySelector('#confirmation-code').textContent = reservation.confirmation_code;
  document.querySelector('#confirmed-details').innerHTML = `
    <div><span>Room</span><strong>${escapeHTML(reservation.room_name)}</strong></div>
    <div><span>Guests</span><strong>${reservation.guests}</strong></div>
    <div><span>Check in</span><strong>${formatDate(reservation.check_in)}</strong></div>
    <div><span>Total</span><strong>${formatMoney(reservation.total)}</strong></div>`;
  confirmationModal.showModal();
}

async function createReservation(event) {
  event.preventDefault();
  if (!state.activeSearch || !state.activeRoom) return;
  const button = reservationForm.querySelector('button[type="submit"]');
  const errorNode = document.querySelector('#reservation-error');
  const formData = Object.fromEntries(new FormData(reservationForm));
  const payload = {
    ...formData,
    check_in: state.activeSearch.check_in,
    check_out: state.activeSearch.check_out,
    guests: state.activeSearch.guests,
  };
  setBusy(button, true, 'Confirming…');
  errorNode.textContent = '';
  try {
    const data = await apiRequest('/api/reservations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
      body: JSON.stringify(payload),
    });
    bookingModal.close();
    showConfirmation(data.reservation);
    reservationForm.reset();
  } catch (error) {
    errorNode.textContent = error.message;
  } finally {
    setBusy(button, false);
  }
}

async function copyConfirmationCode(event) {
  try {
    await navigator.clipboard.writeText(event.currentTarget.textContent);
    showToast('Confirmation code copied.');
  } catch (_error) {
    showToast('Select the code to copy it.');
  }
}

export function initializeBooking() {
  reservationForm.addEventListener('submit', createReservation);
  document.querySelector('#confirmation-code').addEventListener('click', copyConfirmationCode);
}
