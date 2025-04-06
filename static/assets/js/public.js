const year = new Date().getFullYear();
document.getElementById('footer-year').innerHTML = `&copy; ${year} Lineage 2 [NOME DO SERVIDOR]. Todos os direitos reservados.`;

function toggleMenu() {
  const menu = document.getElementById('customMenu');
  menu.classList.toggle('show');
  }

  function closeMenu() {
    const menu = document.getElementById('customMenu');
    menu.classList.remove('show');
  }