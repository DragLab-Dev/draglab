-- ========================================
-- SISTEMA DE SUSCRIPCIONES - DRAGLAB
-- Tablas para gestión de planes y pagos
-- ========================================

-- Tabla de suscripciones de usuarios
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT DEFAULT 'active',  -- active, cancelled, expired
    payment_id TEXT,
    payment_method TEXT,  -- paypal, stripe, free
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de historial de pagos
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subscription_id INTEGER,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    payment_method TEXT NOT NULL,
    payment_id TEXT NOT NULL,  -- ID de PayPal, Stripe, etc.
    status TEXT DEFAULT 'pending',  -- pending, completed, failed, refunded
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
);

-- Tabla de resultados de backtest (para contar uso)
CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    strategy TEXT,
    total_trades INTEGER,
    win_rate REAL,
    total_profit REAL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de estrategias guardadas
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    strategy_data TEXT NOT NULL,  -- JSON con la estrategia
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de signal bots (referencia a bots existentes)
CREATE TABLE IF NOT EXISTS signal_bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    status TEXT DEFAULT 'paused',  -- active, paused, stopped
    bot_token TEXT,
    chat_id TEXT,
    strategy TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de auto trading bots
CREATE TABLE IF NOT EXISTS auto_bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    status TEXT DEFAULT 'paused',
    exchange TEXT,
    api_key TEXT,
    api_secret TEXT,
    strategy TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_backtest_user_date ON backtest_results(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_strategies_user ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_signal_bots_user ON signal_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_auto_bots_user ON auto_bots(user_id);

-- Trigger para actualizar updated_at en strategies
CREATE TRIGGER IF NOT EXISTS update_strategy_timestamp 
AFTER UPDATE ON strategies
BEGIN
    UPDATE strategies SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Trigger para cambiar status a expired cuando pasa la fecha
CREATE TRIGGER IF NOT EXISTS expire_subscriptions
AFTER UPDATE ON subscriptions
WHEN NEW.status = 'active' AND datetime(NEW.end_date) < datetime('now')
BEGIN
    UPDATE subscriptions SET status = 'expired' WHERE id = NEW.id;
END;
