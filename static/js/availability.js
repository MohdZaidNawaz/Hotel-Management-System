import { openBooking } from './booking.js';
import { focusSearch } from './search-navigation.js';
import { state } from './state.js';
import {
  apiRequest, escapeHTML, formatDate, formatMoney, isoDate, setBusy, showToast,
} from './utils.js';

const availabilityForm = document.querySelector('#availability-form');
const checkInInput = document.querySelector('#check-in');
const checkOutInput = document.querySelector('#check-out');
const resultsSection = document.querySelector('#availability-results');
const resultsList = document.querySelector('#results-list');
const resultsTitle = document.querySelector('#results-title');

function initializeDates() {
  checkInInput.value = isoDate(1);
  checkOutInput.value = isoDate(4);
  checkInInput.min = isoDate(0);
  checkOutInput.min = isoDate(2);
}

function updateMinimumCheckout() {
  if (!checkInInput.value) return;
  const nextDay = new Date(`${checkInInput.value}T12:00:00`);
  nextDay.setDate(nextDay.getDate() + 1);
  const minimumCheckout = nextDay.toISOString().slice(0, 10);
  checkOutInput.min = minimumCheckout;
  if (!checkOutInput.value || checkOutInput.value <= checkInInput.value) {
    checkOutInput.value = minimumCheckout;
  }
}

function renderAvailability(search) {
  resultsTitle.textContent = `${search.nights} night${search.nights === 1 ? '' : 's'} · ${formatDate(search.check_in, { year: undefined })} — ${formatDate(search.check_out, { year: undefined })}`;
  if (!search.rooms.length) {
    resultsList.innerHTML = `
      <div class="empty-result">
        <h3>No rooms found for these dates.</h3>
        <p>Try a different date or reduce the number of guests. We would love to find another way to welcome you.</p>
        <button class="button button-dark" type="button" data-edit-search>Try other dates</button>
      </div>`;
    resultsList.querySelector('[data-edit-search]').addEventListener('click', focusSearch);
    return;
  }

  resultsList.innerHTML = search.rooms.map((room) => `
    <article class="result-card">
      <div class="result-image ${escapeHTML(room.image_variant)}" role="img" aria-label="${escapeHTML(room.name)}"></div>
      <div class="result-info">
        <h3>${escapeHTML(room.name)}</h3>
        <p>${escapeHTML(room.description)}</p>
        <ul class="amenity-list">${room.amenities.map((item) => `<li>${escapeHTML(item)}</li>`).join('')}</ul>
      </div>
      <div class="result-price">
        <span>${formatMoney(room.nightly_rate)} per night</span>
        <strong>${formatMoney(room.total)} total</strong>
        <button class="button button-coral" type="button" data-book-room="${escapeHTML(room.code)}">Reserve</button>
      </div>
    </article>`).join('');

  resultsList.querySelectorAll('[data-book-room]').forEach((button) => {
    button.addEventListener('click', () => openBooking(button.dataset.bookRoom));
  });
}

async function searchAvailability(event) {
  event.preventDefault();
  const button = availabilityForm.querySelector('button[type="submit"]');
  const query = new URLSearchParams(new FormData(availabilityForm));
  setBusy(button, true, 'Finding your stay…');
  try {
    state.activeSearch = await apiRequest(`/api/availability?${query}`);
    renderAvailability(state.activeSearch);
    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(button, false);
  }
}

export function initializeAvailability() {
  initializeDates();
  checkInInput.addEventListener('change', updateMinimumCheckout);
  availabilityForm.addEventListener('submit', searchAvailability);
  document.querySelector('#edit-search').addEventListener('click', focusSearch);
  document.querySelectorAll('.room-check').forEach((button) => {
    button.addEventListener('click', focusSearch);
  });
}
