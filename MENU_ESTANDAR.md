# Menú de Navegación Estándar

## Estructura del Menú para TODAS las páginas

```html
<!-- Menú Desplegable -->
<div class="nav-menu-wrapper">
    <button class="menu-toggle" onclick="toggleMenu()" title="Menú">☰</button>
    <div class="dropdown-menu" id="navMenu">
        <a href="/">🏠 Inicio</a>
        <a href="/backtest">🧱 Visual Strategy Builder</a>
        <a href="/trading-bot">🤖 Trading Bot</a>
        <div class="divider"></div>
        <a href="/user-panel">👤 Mi Cuenta</a>
        <a href="/subscriptions">💎 Suscripciones</a>
        <a href="/admin/panel" id="adminLink" style="display: none;">🔒 Panel Admin</a>
        <div class="divider"></div>
        <button onclick="toggleDarkMode()">🌙 Modo Oscuro</button>
        <button onclick="toggleLanguage()">🌐 Idioma</button>
        <div class="divider"></div>
        <button onclick="logout()">🚪 Cerrar Sesión</button>
    </div>
</div>
```

## Páginas a actualizar:
1. ✓ index.html
2. backtest.html
3. trading_bot.html
4. signal_bot.html
5. auto_bot.html
6. admin_panel.html
7. user_panel.html
8. subscriptions.html
