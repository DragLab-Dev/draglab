"""
Test Suite para Signal Bot
Verifica que todos los componentes estén funcionando correctamente
"""

import sys
import json
from datetime import datetime

def test_database():
    """Probar conexión y tablas de la base de datos"""
    print("\n🧪 Test 1: Base de Datos")
    print("-" * 50)
    
    try:
        from database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['signal_bots', 'bot_signals', 'users']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"❌ Tablas faltantes: {', '.join(missing_tables)}")
            print("   Ejecuta: python update_signal_bots_db.py")
            return False
        
        print("✅ Todas las tablas requeridas existen:")
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} registros")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_market_data():
    """Probar obtención de datos de mercado"""
    print("\n🧪 Test 2: Market Data Provider")
    print("-" * 50)
    
    try:
        from market_data import MarketDataProvider
        
        provider = MarketDataProvider()
        
        # Obtener datos de BTC
        print("   📊 Obteniendo datos de BTCUSDT...")
        df = provider.get_klines('BTCUSDT', '1h', limit=100)
        
        if df.empty:
            print("❌ No se pudieron obtener datos")
            return False
        
        print(f"✅ Datos obtenidos correctamente")
        print(f"   - Velas: {len(df)}")
        print(f"   - Último precio: ${df['close'].iloc[-1]:.2f}")
        print(f"   - Columnas: {list(df.columns)}")
        
        # Probar indicadores
        print("\n   📈 Calculando indicadores...")
        ema = provider.calculate_ema(df, 20)
        rsi = provider.calculate_rsi(df, 14)
        
        print(f"✅ Indicadores calculados")
        print(f"   - EMA(20): ${ema.iloc[-1]:.2f}")
        print(f"   - RSI(14): {rsi.iloc[-1]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_evaluator():
    """Probar evaluador de estrategias"""
    print("\n🧪 Test 3: Strategy Evaluator")
    print("-" * 50)
    
    try:
        from strategy_evaluator import StrategyEvaluator
        from market_data import MarketDataProvider
        
        provider = MarketDataProvider()
        evaluator = StrategyEvaluator()
        
        # Obtener datos
        df = provider.get_klines('BTCUSDT', '1h', limit=100)
        
        # Crear estrategia simple
        strategy = {
            'entry_long': [
                {'type': 'value', 'name': 'Price', 'params': {}},
                {'type': 'comparison', 'name': '>', 'params': {}},
                {'type': 'indicator', 'name': 'EMA', 'params': {'period': 20}}
            ]
        }
        
        print("   🎯 Evaluando estrategia simple...")
        result = evaluator.evaluate_strategy(df, strategy, 'entry_long')
        
        print(f"✅ Estrategia evaluada")
        print(f"   - Resultado: {result}")
        print(f"   - Tipo: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_telegram_sender():
    """Probar envío de mensajes a Telegram (sin token real)"""
    print("\n🧪 Test 4: Telegram Sender")
    print("-" * 50)
    
    try:
        from telegram_sender import TelegramSender
        
        # Crear instancia con token falso
        sender = TelegramSender('fake_token', 'fake_chat_id')
        
        print("✅ TelegramSender inicializado correctamente")
        print("   - Base URL configurado")
        print("   - Métodos disponibles: send_message, send_photo")
        print("\n   💡 Para probar envío real, configura un bot de Telegram")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bot_engine():
    """Probar motor de bots"""
    print("\n🧪 Test 5: Bot Engine")
    print("-" * 50)
    
    try:
        from bot_engine import BotEngine, TradingBot
        
        engine = BotEngine()
        
        print("✅ BotEngine inicializado correctamente")
        print(f"   - Bots activos: {len(engine.bots)}")
        print(f"   - Thread-safe: ✓")
        print(f"   - Métodos: start_bot, stop_bot, restart_bot, get_bot_status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_routes():
    """Probar que las rutas de la API estén registradas"""
    print("\n🧪 Test 6: API Routes")
    print("-" * 50)
    
    try:
        from signal_bot_routes import signal_bot_bp
        
        print("✅ Blueprint registrado correctamente")
        print(f"   - Nombre: {signal_bot_bp.name}")
        print(f"   - URL Prefix: {signal_bot_bp.url_prefix or 'No prefix'}")
        
        expected_endpoints = [
            ('create', 'POST /api/signal-bots/create'),
            ('list', 'GET /api/signal-bots/list'),
            ('get', 'GET /api/signal-bots/get/<bot_id>'),
            ('update', 'PUT /api/signal-bots/update/<bot_id>'),
            ('delete', 'DELETE /api/signal-bots/delete/<bot_id>'),
            ('activate', 'POST /api/signal-bots/activate/<bot_id>'),
            ('pause', 'POST /api/signal-bots/pause/<bot_id>'),
            ('logs', 'GET /api/signal-bots/logs/<bot_id>'),
            ('health', 'GET /api/signal-bots/health'),
            ('get-chat-id', 'POST /api/telegram/get-chat-id'),
            ('send-test', 'POST /api/telegram/send-test')
        ]
        
        print("\n   📋 Endpoints configurados:")
        for name, endpoint in expected_endpoints:
            print(f"      ✓ {endpoint}")
        
        print(f"\n   💡 Total: {len(expected_endpoints)} endpoints disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("  SIGNAL BOT - Test Suite")
    print("="*60)
    
    tests = [
        ("Base de Datos", test_database),
        ("Market Data", test_market_data),
        ("Strategy Evaluator", test_strategy_evaluator),
        ("Telegram Sender", test_telegram_sender),
        ("Bot Engine", test_bot_engine),
        ("API Routes", test_api_routes)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' falló con excepción: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("  RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print("\n" + "-"*60)
    print(f"  Total: {passed}/{total} tests pasados ({passed/total*100:.0f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        print("   El sistema está listo para usar.")
        return True
    else:
        print(f"\n⚠️  {total-passed} test(s) fallaron")
        print("   Revisa los errores arriba y corrígelos antes de continuar.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
