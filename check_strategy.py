import sqlite3
import json

# Connect to tradingbot.db
conn = sqlite3.connect('database/tradingbot.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in tradingbot.db:")
for t in tables:
    print(f"  - {t[0]}")

# Check signal_bots table
try:
    result = cursor.execute('SELECT id, name, strategy FROM signal_bots WHERE id=9').fetchone()
    if result:
        print(f"\n✅ Bot ID: {result[0]}")
        print(f"✅ Name: {result[1]}")
        print("\n📋 Strategy JSON:")
        strategy = json.loads(result[2])
        print(json.dumps(strategy, indent=2))
    else:
        print("\n❌ Bot 9 not found")
except Exception as e:
    print(f"\n❌ Error: {e}")

conn.close()
