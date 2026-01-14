import sqlite3

conn = sqlite3.connect('database/draglab.db')
cursor = conn.cursor()

# Ver suscripciones activas
print("=" * 60)
print("SUSCRIPCIONES ACTIVAS")
print("=" * 60)
cursor.execute("""
    SELECT s.id, s.user_id, u.email, s.plan_name, s.status, s.start_date, s.end_date
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    WHERE s.status = 'active'
""")
subs = cursor.fetchall()
for sub in subs:
    print(f"\nSuscripción ID: {sub[0]}")
    print(f"  User ID: {sub[1]}")
    print(f"  Email: {sub[2]}")
    print(f"  Plan: {sub[3]}")
    print(f"  Status: {sub[4]}")
    print(f"  Inicio: {sub[5]}")
    print(f"  Fin: {sub[6]}")

# Ver uso actual por usuario
print("\n" + "=" * 60)
print("USO DE RECURSOS POR USUARIO")
print("=" * 60)
cursor.execute("SELECT id, email FROM users")
users = cursor.fetchall()
for user_id, email in users:
    print(f"\n👤 {email} (ID: {user_id})")
    
    # Signal bots
    cursor.execute("SELECT COUNT(*) FROM signal_bots WHERE user_id=?", (user_id,))
    signal_count = cursor.fetchone()[0]
    print(f"   Signal Bots: {signal_count}")
    
    # Auto bots
    cursor.execute("SELECT COUNT(*) FROM auto_bots WHERE user_id=?", (user_id,))
    auto_count = cursor.fetchone()[0]
    print(f"   Auto Bots: {auto_count}")
    
    # Backtests (últimos 30 días)
    cursor.execute("""
        SELECT COUNT(*) FROM backtest_results 
        WHERE user_id=? AND created_at > datetime('now', '-30 days')
    """, (user_id,))
    backtest_count = cursor.fetchone()[0]
    print(f"   Backtests (30 días): {backtest_count}")
    
    # Strategies
    cursor.execute("SELECT COUNT(*) FROM strategies WHERE user_id=?", (user_id,))
    strategy_count = cursor.fetchone()[0]
    print(f"   Estrategias: {strategy_count}")

conn.close()
print("\n" + "=" * 60)
