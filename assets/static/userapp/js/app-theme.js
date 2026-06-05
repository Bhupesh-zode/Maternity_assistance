(function () {
  var STORAGE_KEY = 'ma-theme';
  var LEGACY_KEYS = ['ma-user-theme', 'ma-dashboard-theme'];

  function isDark() {
    try {
      var theme = localStorage.getItem(STORAGE_KEY);
      if (!theme) {
        for (var i = 0; i < LEGACY_KEYS.length; i++) {
          theme = localStorage.getItem(LEGACY_KEYS[i]);
          if (theme) {
            break;
          }
        }
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

  function getToggles() {
    return document.querySelectorAll('.ma-theme-toggle-input, #portal-theme-toggle, #theme-toggle-float');
  }

  function applyTheme(dark, notify) {
    document.documentElement.classList.toggle('ma-theme-dark', dark);
    document.body.setAttribute('data-theme', dark ? 'dark' : 'light');

    getToggles().forEach(function (toggle) {
      toggle.checked = dark;
    });

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

    getToggles().forEach(function (toggle) {
      toggle.addEventListener('change', function () {
        var dark = toggle.checked;
        persistTheme(dark);
        applyTheme(dark, true);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
