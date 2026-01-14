/* MENÚ UNIVERSAL - JavaScript compartido por todas las páginas */

function toggleUniversalMenu() {
    const menu = document.getElementById('universalMenu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// Cerrar menú al hacer clic fuera
document.addEventListener('click', function(event) {
    const menu = document.querySelector('.universal-menu');
    const menuContent = document.getElementById('universalMenu');
    if (menu && menuContent && !menu.contains(event.target)) {
        menuContent.classList.remove('active');
    }
});

// Mostrar enlace de admin si el usuario es admin
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/auth/me')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.user && data.user.role === 'admin') {
                const adminLink = document.getElementById('adminMenuLink');
                if (adminLink) adminLink.style.display = 'block';
            }
        })
        .catch(err => console.error('Error verificando rol:', err));
});
