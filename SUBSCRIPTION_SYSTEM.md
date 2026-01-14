# 💳 Sistema de Suscripciones - DragLab

Sistema completo de gestión de planes, límites de uso y pagos para DragLab.

## 📋 Planes Disponibles

### 🆓 Free Trial
**Duración:** 14 días  
**Precio:** GRATIS  
**Límites:**
- ✓ 10 Backtests incluidos
- ✓ 1 Signal Bot activo
- ✓ 3 Indicadores técnicos
- ✓ 2 Estrategias guardadas
- ✓ 5 Operaciones/día
- ✓ Constructor visual básico
- ✓ Señales por Telegram
- ✓ Soporte por email

**Ideal para:** Usuarios que quieren probar la plataforma antes de comprar.

---

### 💼 Pro Monthly
**Duración:** 30 días  
**Precio:** $29.99 USD/mes  
**Límites:**
- ✓ 100 Backtests/mes
- ✓ 5 Signal Bots simultáneos
- ✓ 2 Auto Trading Bots
- ✓ Indicadores ilimitados
- ✓ 10 Estrategias guardadas
- ✓ 50 Operaciones/día
- ✓ Constructor visual avanzado
- ✓ Gestión de riesgo automática
- ✓ Stop-Loss y Take-Profit
- ✓ Historial completo de señales
- ✓ Análisis de rendimiento
- ✓ Soporte prioritario 24/7

**Ideal para:** Traders activos que necesitan herramientas profesionales.

---

### 👑 Pro Annual
**Duración:** 365 días  
**Precio:** $299.99 USD/año (≈$0.82/día)  
**Descuento:** 17% OFF vs plan mensual  
**Ahorro:** $60/año

**Límites:**
- ✓ Backtests ILIMITADOS
- ✓ Signal Bots ILIMITADOS
- ✓ Auto Trading Bots ILIMITADOS
- ✓ Indicadores ILIMITADOS
- ✓ Estrategias ILIMITADAS
- ✓ Operaciones ILIMITADAS
- ✓ Constructor visual premium
- ✓ API REST avanzada
- ✓ Webhooks personalizados
- ✓ Gestión de múltiples exchanges
- ✓ Backtesting con datos históricos premium
- ✓ Machine Learning signals (próximamente)
- ✓ Soporte VIP 24/7
- ✓ Acceso anticipado a nuevas features

**Ideal para:** Traders profesionales y equipos que necesitan capacidad máxima.

---

## 🚀 Instalación

### 1. Inicializar Base de Datos

```bash
python init_subscriptions.py
```

Este script creará automáticamente todas las tablas necesarias:
- `subscriptions` - Gestión de planes de usuario
- `payments` - Historial de pagos
- `backtest_results` - Registro de backtests
- `strategies` - Estrategias guardadas
- `signal_bots` - Bots de señales
- `auto_bots` - Bots de trading automático

### 2. Integrar en app.py

Agregar al archivo `app.py`:

```python
from subscription_routes import subscription_bp

# Registrar blueprint
app.register_blueprint(subscription_bp)
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` con:

```env
# PayPal
PAYPAL_CLIENT_ID=tu_client_id_aqui
PAYPAL_CLIENT_SECRET=tu_client_secret_aqui
PAYPAL_MODE=sandbox  # o 'live' para producción

# Stripe (opcional)
STRIPE_PUBLIC_KEY=tu_public_key_aqui
STRIPE_SECRET_KEY=tu_secret_key_aqui
```

---

## 🔌 API Endpoints

### GET `/api/subscriptions/plans`
Obtener todos los planes disponibles.

**Response:**
```json
{
  "success": true,
  "plans": [...]
}
```

### GET `/api/subscriptions/current`
Obtener suscripción actual del usuario.

**Response:**
```json
{
  "success": true,
  "subscription": {
    "plan_name": "pro_monthly",
    "display_name": "💼 Pro Monthly",
    "start_date": "2026-01-13T10:00:00",
    "end_date": "2026-02-13T10:00:00",
    "days_remaining": 30,
    "status": "active"
  }
}
```

### GET `/api/subscriptions/usage`
Obtener uso actual y límites.

**Response:**
```json
{
  "success": true,
  "usage": {
    "backtests": 15,
    "signal_bots": 2,
    "auto_bots": 1,
    "strategies": 5
  },
  "limits": {
    "backtests": 100,
    "signal_bots": 5,
    "auto_bots": 2,
    "strategies": 10
  }
}
```

### POST `/api/subscriptions/subscribe`
Activar una suscripción.

**Request:**
```json
{
  "plan_name": "pro_monthly",
  "payment_id": "PAYPAL-12345",
  "payment_method": "paypal"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Suscripción activada correctamente",
  "subscription": {...}
}
```

### GET `/api/subscriptions/check-limit/<limit_type>`
Verificar si se alcanzó un límite.

**Tipos válidos:**
- `backtests`
- `signal_bots`
- `auto_bots`
- `strategies`

**Response:**
```json
{
  "success": true,
  "allowed": true,
  "limit": 100,
  "current": 15,
  "remaining": 85
}
```

### POST `/api/subscriptions/cancel`
Cancelar suscripción actual.

---

## 💳 Integración de Pagos

### PayPal

1. Crear cuenta en [PayPal Developer](https://developer.paypal.com/)
2. Crear App en el Dashboard
3. Obtener Client ID y Secret
4. Configurar en `.env`
5. En `subscriptions.html`, reemplazar:

```html
<script src="https://www.paypal.com/sdk/js?client-id=TU_CLIENT_ID&currency=USD"></script>
```

### Stripe (Alternativa)

```bash
pip install stripe
```

Agregar en `subscription_routes.py`:

```python
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
```

---

## 🔒 Control de Límites

### En el Código

Verificar límites antes de ejecutar acciones:

```python
from flask import session, jsonify
import requests

def create_backtest():
    # Verificar límite
    response = requests.get(
        'http://localhost:5000/api/subscriptions/check-limit/backtests',
        cookies={'session': session.sid}
    )
    
    data = response.json()
    
    if not data['allowed']:
        return jsonify({
            'success': False,
            'error': 'Has alcanzado el límite de backtests para tu plan. Actualiza tu suscripción.',
            'upgrade_url': '/subscriptions'
        }), 403
    
    # Continuar con la creación...
```

### En el Frontend

```javascript
async function checkLimit(limitType) {
    const response = await fetch(`/api/subscriptions/check-limit/${limitType}`);
    const data = await response.json();
    
    if (!data.allowed) {
        alert(`⚠️ Has alcanzado el límite de ${limitType}.\n\nActualiza tu plan para continuar.`);
        window.location.href = '/subscriptions';
        return false;
    }
    
    return true;
}

// Uso
async function createBot() {
    if (await checkLimit('signal_bots')) {
        // Continuar con la creación
    }
}
```

---

## 📊 Monitoreo y Métricas

### Consultas Útiles

```sql
-- Usuarios por plan
SELECT plan_name, COUNT(*) as users
FROM subscriptions
WHERE status = 'active'
GROUP BY plan_name;

-- Ingresos mensuales
SELECT 
    strftime('%Y-%m', created_at) as month,
    SUM(amount) as revenue
FROM payments
WHERE status = 'completed'
GROUP BY month
ORDER BY month DESC;

-- Uso promedio por plan
SELECT 
    s.plan_name,
    AVG(br.count) as avg_backtests
FROM subscriptions s
LEFT JOIN (
    SELECT user_id, COUNT(*) as count
    FROM backtest_results
    GROUP BY user_id
) br ON s.user_id = br.user_id
WHERE s.status = 'active'
GROUP BY s.plan_name;
```

---

## 🧪 Testing

### Probar Free Trial

```bash
curl -X POST http://localhost:5000/api/subscriptions/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "free_trial"
  }'
```

### Simular Pago PayPal (Sandbox)

1. Crear cuenta de prueba en PayPal Sandbox
2. Usar credenciales de prueba en el frontend
3. Realizar pago de prueba
4. Verificar activación de suscripción

---

## 🔄 Renovación Automática

Para implementar renovación automática:

1. Configurar webhooks de PayPal
2. Escuchar evento `BILLING.SUBSCRIPTION.RENEWED`
3. Actualizar end_date en la BD

```python
@subscription_bp.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    # Verificar firma
    # Procesar evento
    # Actualizar suscripción
    pass
```

---

## 📈 Mejoras Futuras

- [ ] Cupones de descuento
- [ ] Programa de referidos
- [ ] Suscripción por equipos
- [ ] Facturación automática
- [ ] Exportar facturas PDF
- [ ] Webhooks para eventos
- [ ] Dashboard de analytics
- [ ] A/B testing de precios

---

## ⚠️ Notas Importantes

1. **Seguridad:** Nunca exponer API keys en el código
2. **Testing:** Usar modo sandbox antes de producción
3. **Logs:** Registrar todos los pagos y errores
4. **Backup:** Hacer backup de la BD regularmente
5. **Compliance:** Cumplir con leyes de protección de datos

---

## 🆘 Soporte

Para preguntas o problemas:
- Email: support@draglab.com
- Discord: [DragLab Community]
- Docs: [docs.draglab.com]

---

## 📝 Changelog

### v1.0.0 (2026-01-13)
- ✅ Sistema de 3 planes implementado
- ✅ Integración con PayPal lista
- ✅ Control de límites funcional
- ✅ Dashboard de uso completo
- ✅ API REST documentada

---

**Desarrollado con ❤️ por el equipo DragLab**
