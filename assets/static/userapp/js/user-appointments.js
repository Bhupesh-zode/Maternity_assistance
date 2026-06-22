(function () {
  var form = document.getElementById('appointmentBookingForm');
  var dateInput = document.getElementById('preferredDate');
  var timeSelect = document.getElementById('preferredTime');
  if (!form || !dateInput || !timeSelect) {
    return;
  }

  var minDate = dateInput.getAttribute('min');
  var bookedSlotsUrl = form.getAttribute('data-booked-slots-url');
  var slotLabels = {};

  Array.from(timeSelect.options).forEach(function (option) {
    if (!option.value) {
      return;
    }
    slotLabels[option.value] = option.getAttribute('data-label') || option.textContent;
  });

  function setOptionState(option, state) {
    var baseLabel = slotLabels[option.value] || option.textContent;
    option.classList.remove('appointment-slot-booked', 'appointment-slot-past');

    if (state === 'booked') {
      option.textContent = baseLabel + ' — Booked';
      option.disabled = true;
      option.hidden = false;
      option.classList.add('appointment-slot-booked');
      return;
    }

    option.textContent = baseLabel;
    if (state === 'past') {
      option.disabled = true;
      option.hidden = true;
      option.classList.add('appointment-slot-past');
      return;
    }

    option.disabled = false;
    option.hidden = false;
  }

  function isPastSlot(timeValue) {
    if (dateInput.value !== minDate) {
      return false;
    }
    var parts = timeValue.split(':');
    var now = new Date();
    var slot = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      parseInt(parts[0], 10),
      parseInt(parts[1], 10),
      0,
      0
    );
    return slot <= now;
  }

  function refreshTimeSlots(booked) {
    var bookedSet = new Set(booked || []);

    Array.from(timeSelect.options).forEach(function (option, index) {
      if (index === 0 || !option.value) {
        return;
      }
      if (bookedSet.has(option.value)) {
        setOptionState(option, 'booked');
      } else if (isPastSlot(option.value)) {
        setOptionState(option, 'past');
      } else {
        setOptionState(option, 'available');
      }
    });

    if (timeSelect.selectedOptions[0] && timeSelect.selectedOptions[0].disabled) {
      timeSelect.value = '';
    }
  }

  function loadBookedSlots() {
    if (!dateInput.value) {
      refreshTimeSlots([]);
      return;
    }

    if (!bookedSlotsUrl) {
      refreshTimeSlots([]);
      return;
    }

    fetch(bookedSlotsUrl + '?date=' + encodeURIComponent(dateInput.value), {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Failed to load booked slots');
        }
        return response.json();
      })
      .then(function (data) {
        refreshTimeSlots(data.booked || []);
      })
      .catch(function () {
        refreshTimeSlots([]);
      });
  }

  dateInput.addEventListener('change', loadBookedSlots);
  dateInput.addEventListener('input', loadBookedSlots);
  loadBookedSlots();
})();
