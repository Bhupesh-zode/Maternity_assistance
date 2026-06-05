(function () {
  var STORAGE_KEY = 'ma-user-theme';
  var LEGACY_KEY = 'ma-dashboard-theme';

  function isDark() {
    try {
      var theme = localStorage.getItem(STORAGE_KEY);
      if (!theme) {
        theme = localStorage.getItem(LEGACY_KEY);
      }
      return theme === 'dark';
    } catch (e) {
      return false;
    }
  }

  function persistTheme(dark) {
    try {
      localStorage.setItem(STORAGE_KEY, dark ? 'dark' : 'light');
    } catch (e) {}
  }

  function applyTheme(dark, notify) {
    document.documentElement.classList.toggle('ma-theme-dark', dark);
    document.body.setAttribute('data-theme', dark ? 'dark' : 'light');

    var toggle = document.getElementById('portal-theme-toggle');
    if (toggle) {
      toggle.checked = dark;
    }

    if (notify) {
      document.dispatchEvent(new CustomEvent('portal-theme-change', {
        detail: { dark: dark },
      }));
      document.dispatchEvent(new CustomEvent('dashboard-theme-change', {
        detail: { dark: dark },
      }));
    }
  }

  function init() {
    applyTheme(isDark(), false);

    var toggle = document.getElementById('portal-theme-toggle');
    if (!toggle) {
      return;
    }

    toggle.addEventListener('change', function () {
      var dark = toggle.checked;
      persistTheme(dark);
      applyTheme(dark, true);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
