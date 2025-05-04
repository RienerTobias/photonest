document.addEventListener('DOMContentLoaded', () => {
  const themeSelect = document.getElementById('theme-select');
  const html = document.documentElement;

  const themes = {
    light: 'light',
    dark: 'dark',
    system: 'Systemstandard'
  };

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    let themeToApply = theme;
    
    if (theme === 'system') {
      themeToApply = getSystemTheme();
      localStorage.removeItem('theme'); 
    } else {
      localStorage.setItem('theme', theme);
    }

    html.setAttribute('data-theme', themeToApply);
    themeSelect.value = theme;
  }

  function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'system';
  }

  const initialTheme = loadTheme();
  applyTheme(initialTheme);

  themeSelect.addEventListener('change', (e) => {
    applyTheme(e.target.value);
  });

  window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
    if (localStorage.getItem('theme') === null) {
      applyTheme('system');
    }
  });
});