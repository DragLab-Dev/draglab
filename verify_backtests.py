import sqlite3

conn = sqlite3.connect('database/draglab.db')
cursor = conn.cursor()

# Ver backtests
cursor.execute('SELECT COUNT(*) FROM backtest_results')
count = cursor.fetchone()[0]
print(f'📊 Total backtests en BD: {count}')

if count > 0:
    cursor.execute('''
        SELECT b.id, u.email, b.symbol, b.timeframe, b.num_trades, b.created_at
        FROM backtest_results b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.created_at DESC
        LIMIT 10
    ''')
    results = cursor.fetchall()
    print('\n🔍 Últimos backtests:')
    for r in results:
        print(f'  ID:{r[0]}, User:{r[1]}, {r[2]}/{r[3]}, Trades:{r[4]}, Fecha:{r[5]}')

conn.close()
