/**
 * MoneyFlow — JavaScript Principal
 * Gerenciamento de tema, validação de exclusão (DELETAR), utilitários e Chart.js
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Alternador de Tema Claro/Escuro
  const themeToggleBtn = document.getElementById('themeToggle');
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    document.documentElement.style.colorScheme = theme;
    updateThemeIcon(theme);
  }

  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', newTheme);
      applyTheme(newTheme);
    });
  }


  function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill text-secondary';
    }
  }

  // 2. Validação da palavra "DELETAR" no formulário de exclusão permanente
  const deleteInput = document.getElementById('deleteConfirmationInput');
  const deleteSubmitBtn = document.getElementById('btnConfirmDelete');

  if (deleteInput && deleteSubmitBtn) {
    deleteSubmitBtn.disabled = true;
    deleteInput.addEventListener('input', (e) => {
      if (e.target.value.trim() === 'DELETAR') {
        deleteSubmitBtn.disabled = false;
        deleteSubmitBtn.classList.remove('btn-secondary');
        deleteSubmitBtn.classList.add('btn-danger');
      } else {
        deleteSubmitBtn.disabled = true;
        deleteSubmitBtn.classList.remove('btn-danger');
        deleteSubmitBtn.classList.add('btn-secondary');
      }
    });
  }

  // 3. Auto-submit em seletores de mês e ano no topo
  const periodForm = document.getElementById('periodSelectForm');
  if (periodForm) {
    const selects = periodForm.querySelectorAll('select');
    selects.forEach(select => {
      select.addEventListener('change', () => {
        periodForm.submit();
      });
    });
  }

  // 4. Auto-dismiss em alertas após 5 segundos
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});
