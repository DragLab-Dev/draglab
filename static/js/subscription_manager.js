/**
 * Subscription Manager - Sistema de Control de Límites
 * Maneja las restricciones de planes y límites de uso
 */

class SubscriptionManager {
    constructor() {
        this.currentPlan = null;
        this.usage = null;
        this.initialized = false;
    }

    /**
     * Inicializa el manager cargando plan y uso actual
     */
    async initialize() {
        try {
            await Promise.all([
                this.loadCurrentPlan(),
                this.loadUsage()
            ]);
            this.initialized = true;
            return true;
        } catch (error) {
            console.error('Error initializing SubscriptionManager:', error);
            return false;
        }
    }

    /**
     * Carga el plan actual del usuario
     */
    async loadCurrentPlan() {
        try {
            const response = await fetch('/api/subscriptions/current');
            const data = await response.json();
            
            if (data.success && data.subscription) {
                this.currentPlan = data.subscription;
            } else {
                // Sin plan activo - modo restringido
                this.currentPlan = {
                    plan_name: 'none',
                    status: 'inactive',
                    limits: {
                        backtests: 0,
                        signal_bots: 0,
                        auto_bots: 0,
                        operations_per_day: 0,
                        indicators: 0,
                        strategies: 0
                    }
                };
            }
            return this.currentPlan;
        } catch (error) {
            console.error('Error loading current plan:', error);
            throw error;
        }
    }

    /**
     * Carga el uso actual del usuario
     */
    async loadUsage() {
        try {
            const response = await fetch('/api/subscriptions/usage');
            const data = await response.json();
            
            if (data.success) {
                this.usage = data.usage;
            } else {
                this.usage = {
                    backtests: 0,
                    signal_bots: 0,
                    auto_bots: 0,
                    operations_today: 0,
                    strategies: 0
                };
            }
            return this.usage;
        } catch (error) {
            console.error('Error loading usage:', error);
            throw error;
        }
    }

    /**
     * Verifica si el usuario puede realizar una acción
     * @param {string} type - Tipo de acción: 'backtest', 'signal_bot', 'auto_bot', 'strategy'
     * @returns {Promise<{allowed: boolean, reason?: string}>}
     */
    async checkLimit(type) {
        try {
            console.log(`🔍 [DEBUG Frontend] Verificando límite de: ${type}`);
            const response = await fetch(`/api/subscriptions/check-limit/${type}`);
            const data = await response.json();
            
            console.log(`🔍 [DEBUG Frontend] Respuesta recibida:`, data);
            
            if (!data.allowed) {
                console.log(`❌ [DEBUG Frontend] Límite alcanzado:`, data);
                return {
                    allowed: false,
                    reason: data.reason || `Has alcanzado el límite de ${type}`,
                    limit: data.limit,
                    current: data.current
                };
            }
            
            console.log(`✅ [DEBUG Frontend] Acción permitida`);
            return { allowed: true };
        } catch (error) {
            console.error('❌ [DEBUG Frontend] Error checking limit:', error);
            // En caso de error, bloquear por seguridad
            return {
                allowed: false,
                reason: 'Error verificando límites. Por favor, recarga la página.'
            };
        }
    }

    /**
     * Muestra un modal de límite alcanzado con opción de upgrade
     * @param {string} type - Tipo de recurso limitado
     * @param {object} limitInfo - Información del límite
     */
    showLimitReachedModal(type, limitInfo) {
        const typeNames = {
            'backtest': 'Backtests',
            'signal_bot': 'Signal Bots',
            'auto_bot': 'Auto Trading Bots',
            'strategy': 'Estrategias'
        };

        const typeName = typeNames[type] || type;
        const limit = limitInfo.limit === -1 ? 'Ilimitado' : limitInfo.limit;
        
        const modal = document.createElement('div');
        modal.className = 'subscription-limit-modal';
        modal.innerHTML = `
            <div class="subscription-limit-content">
                <div class="limit-icon">⚠️</div>
                <h2>Límite Alcanzado</h2>
                <p class="limit-message">
                    Has alcanzado el límite de <strong>${typeName}</strong> de tu plan actual.
                </p>
                <div class="limit-stats">
                    <div class="limit-stat">
                        <span class="limit-label">Uso Actual:</span>
                        <span class="limit-value">${limitInfo.current}</span>
                    </div>
                    <div class="limit-stat">
                        <span class="limit-label">Límite del Plan:</span>
                        <span class="limit-value">${limit}</span>
                    </div>
                </div>
                <p class="upgrade-message">
                    Actualiza tu plan para obtener más ${typeName.toLowerCase()} y funcionalidades premium.
                </p>
                <div class="modal-buttons">
                    <button onclick="window.location.href='/subscriptions'" class="btn-upgrade">
                        ⬆️ Ver Planes
                    </button>
                    <button onclick="this.closest('.subscription-limit-modal').remove()" class="btn-cancel">
                        Cerrar
                    </button>
                </div>
            </div>
        `;

        // Estilos inline para el modal
        const style = document.createElement('style');
        style.textContent = `
            .subscription-limit-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 100000;
                animation: fadeIn 0.3s;
            }
            .subscription-limit-content {
                background: white;
                padding: 40px;
                border-radius: 20px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                animation: slideUp 0.3s;
            }
            .limit-icon {
                font-size: 64px;
                margin-bottom: 20px;
            }
            .subscription-limit-content h2 {
                color: #dc3545;
                margin-bottom: 15px;
                font-size: 28px;
            }
            .limit-message {
                font-size: 16px;
                color: #666;
                margin-bottom: 25px;
            }
            .limit-stats {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .limit-stat {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #dee2e6;
            }
            .limit-stat:last-child {
                border-bottom: none;
            }
            .limit-label {
                font-weight: 600;
                color: #495057;
            }
            .limit-value {
                font-weight: bold;
                color: #dc3545;
            }
            .upgrade-message {
                color: #667eea;
                font-weight: 600;
                margin: 20px 0;
            }
            .modal-buttons {
                display: flex;
                gap: 15px;
                margin-top: 25px;
            }
            .btn-upgrade {
                flex: 1;
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .btn-upgrade:hover {
                transform: translateY(-2px);
            }
            .btn-cancel {
                flex: 1;
                padding: 15px 30px;
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: opacity 0.2s;
            }
            .btn-cancel:hover {
                opacity: 0.8;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            body.dark-mode .subscription-limit-content {
                background: #1e1e2e;
                color: #fff;
            }
            body.dark-mode .limit-message {
                color: #ccc;
            }
            body.dark-mode .limit-stats {
                background: #2a2a3e;
            }
            body.dark-mode .limit-label {
                color: #aaa;
            }
        `;

        if (!document.querySelector('style[data-subscription-modal]')) {
            style.setAttribute('data-subscription-modal', 'true');
            document.head.appendChild(style);
        }

        document.body.appendChild(modal);

        // Cerrar al hacer click fuera del contenido
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    /**
     * Verifica y ejecuta una acción si está permitida
     * @param {string} type - Tipo de acción
     * @param {Function} callback - Función a ejecutar si está permitido
     */
    async executeIfAllowed(type, callback) {
        if (!this.initialized) {
            await this.initialize();
        }

        const check = await this.checkLimit(type);
        
        if (!check.allowed) {
            this.showLimitReachedModal(type, check);
            return false;
        }

        // Ejecutar la acción
        if (typeof callback === 'function') {
            await callback();
        }
        
        // Actualizar uso después de la acción
        await this.loadUsage();
        
        return true;
    }

    /**
     * Obtiene información del plan actual
     */
    getPlanInfo() {
        return this.currentPlan;
    }

    /**
     * Obtiene información del uso actual
     */
    getUsageInfo() {
        return this.usage;
    }

    /**
     * Verifica si el plan está activo
     */
    isPlanActive() {
        return this.currentPlan && this.currentPlan.status === 'active';
    }

    /**
     * Obtiene el nombre del plan actual
     */
    getPlanName() {
        if (!this.currentPlan || this.currentPlan.plan_name === 'none') {
            return 'Sin Plan';
        }
        
        const planNames = {
            'free_trial': 'Free Trial',
            'pro_monthly': 'Pro Monthly',
            'pro_annual': 'Pro Annual'
        };
        
        return planNames[this.currentPlan.plan_name] || this.currentPlan.plan_name;
    }
}

// Instancia global
window.subscriptionManager = new SubscriptionManager();

// Inicializar automáticamente cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.subscriptionManager.initialize();
    });
} else {
    window.subscriptionManager.initialize();
}
