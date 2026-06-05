(function () {
  var fab = document.getElementById('alertsFab');
  var toggle = document.getElementById('alertsFabToggle');
  var panel = document.getElementById('alertsFabPanel');

  if (!fab || !toggle || !panel) {
    return;
  }

  function closePanel() {
    panel.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    fab.classList.remove('is-open');
  }

  function openPanel() {
    panel.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    fab.classList.add('is-open');
  }

  toggle.addEventListener('click', function (e) {
    e.stopPropagation();
    if (panel.hidden) {
      openPanel();
    } else {
      closePanel();
    }
  });

  document.addEventListener('click', function (e) {
    if (!fab.contains(e.target)) {
      closePanel();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closePanel();
    }
  });
})();
