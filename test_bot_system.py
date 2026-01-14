"""
Test rápido del sistema de bots
Verifica que todos los componentes funcionen correctamente
"""

def test_market_data():
    """Probar obtención de datos de mercado"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Market Data Provider")
    print("="*60)
    
    try:
        from market_data import MarketDataProvider
        
        market = MarketDataProvider()
        
        # Obtener datos de BTCUSDT
        print("📊 Obteniendo datos de BTCUSDT en 15m...")
        df = market.get_klines('BTCUSDT', '15m', limit=100)
        
        print(f"✅ Datos obtenidos: {len(df)} velas")
        print(f"   Precio actual: ${df['close'].iloc[-1]:,.2f}")
        print(f"   Precio más alto: ${df['high'].max():,.2f}")
        print(f"   Precio más bajo: ${df['low'].min():,.2f}")
        
        # Calcular indicadores
        print("\n📈 Calculando indicadores...")
        ema20 = market.calculate_ema(df, 20)
        rsi = market.calculate_rsi(df, 14)
        
        print(f"   EMA(20): ${ema20.iloc[-1]:,.2f}")
        print(f"   RSI(14): {rsi.iloc[-1]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_strategy_evaluator():
    """Probar evaluador de estrategias"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Strategy Evaluator")
    print("="*60)
    
    try:
        from market_data import MarketDataProvider
        from strategy_evaluator import StrategyEvaluator
        
        market = MarketDataProvider()
        evaluator = StrategyEvaluator()
        
        # Obtener datos
        df = market.get_klines('BTCUSDT', '15m', limit=100)
        
        # Estrategia simple: Precio > EMA(50)
        strategy = {
            'entry_long': [
                {'type': 'value', 'name': 'Price', 'params': {}},
                {'type': 'comparison', 'name': 'GreaterThan', 'params': {}},
                {'type': 'indicator', 'name': 'EMA', 'params': {'period': '50'}}
            ]
        }
        
        print("📊 Evaluando estrategia: Precio > EMA(50)")
        result = evaluator.evaluate_strategy(df, strategy, 'entry_long')
        
        current_price = df['close'].iloc[-1]
        ema50 = market.calculate_ema(df, 50).iloc[-1]
        
        print(f"   Precio actual: ${current_price:,.2f}")
        print(f"   EMA(50): ${ema50:,.2f}")
        print(f"   Resultado: {'✅ SEÑAL LONG' if result else '❌ Sin señal'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_telegram():
    """Probar conexión con Telegram"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Telegram Sender")
    print("="*60)
    
    # Pedir credenciales de prueba
    print("\n⚠️  Necesitas un Bot Token y Chat ID para esta prueba")
    print("   Puedes omitirla presionando Enter sin escribir nada\n")
    
    bot_token = input("Bot Token (o Enter para omitir): ").strip()
    
    if not bot_token:
        print("⏭️  Test omitido")
        return True
    
    chat_id = input("Chat ID: ").strip()
    
    try:
        from telegram_sender import TelegramSender
        
        sender = TelegramSender(bot_token, chat_id)
        
        print("\n📡 Probando conexión...")
        if sender.test_connection():
            print("✅ Conexión exitosa!")
            
            # Enviar mensaje de prueba
            test_msg = "🧪 Test exitoso del sistema de bots de señales"
            if sender.send_message(test_msg):
                print("✅ Mensaje enviado correctamente")
                return True
        
        print("❌ Error en la conexión")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database():
    """Probar tablas de base de datos"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Database Tables")
    print("="*60)
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('database/app.db')
        cursor = conn.cursor()
        
        # Verificar tabla signal_bots
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signal_bots'")
        if cursor.fetchone():
            print("✅ Tabla 'signal_bots' existe")
        else:
            print("❌ Tabla 'signal_bots' no existe")
            print("   Ejecuta: python update_database_bots.py")
            return False
        
        # Verificar tabla bot_signals
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bot_signals'")
        if cursor.fetchone():
            print("✅ Tabla 'bot_signals' existe")
        else:
            print("❌ Tabla 'bot_signals' no existe")
            return False
        
        # Contar bots existentes
        cursor.execute("SELECT COUNT(*) FROM signal_bots")
        bot_count = cursor.fetchone()[0]
        print(f"📊 Bots en base de datos: {bot_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("🤖 SISTEMA DE BOTS - TEST SUITE")
    print("="*60)
    
    results = {
        'Market Data': test_market_data(),
        'Strategy Evaluator': test_strategy_evaluator(),
        'Database': test_database(),
        'Telegram': test_telegram()
    }
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:.<40} {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "="*60)
    if passed == total:
        print(f"🎉 TODOS LOS TESTS PASARON ({passed}/{total})")
        print("\n✅ El sistema está listo para usarse!")
    else:
        print(f"⚠️  ALGUNOS TESTS FALLARON ({passed}/{total})")
        print("\n🔧 Revisa los errores arriba")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
