"""
Test del Market Data Service - Demostración de eficiencia
Compara el sistema antiguo vs el nuevo
"""

import time
from market_data_service import market_data_service


def test_market_data_service():
    """Test completo del servicio"""
    
    print("=" * 70)
    print("🧪 TEST: MARKET DATA SERVICE")
    print("=" * 70)
    print()
    
    # ESCENARIO: 5 usuarios con bots en los mismos pares
    bots = [
        ("bot_user1_btc", "BTCUSDT", "15m"),
        ("bot_user2_btc", "BTCUSDT", "15m"),
        ("bot_user3_btc", "BTCUSDT", "15m"),
        ("bot_user4_eth", "ETHUSDT", "1h"),
        ("bot_user5_eth", "ETHUSDT", "1h"),
        ("bot_user6_bnb", "BNBUSDT", "5m"),
    ]
    
    print("📊 ESCENARIO DE PRUEBA:")
    print(f"   • {len(bots)} bots activos")
    print(f"   • 3 bots en BTCUSDT/15m")
    print(f"   • 2 bots en ETHUSDT/1h")
    print(f"   • 1 bot en BNBUSDT/5m")
    print()
    
    # SISTEMA ANTIGUO (simulado)
    print("🔴 SISTEMA ANTIGUO:")
    print("   Cada bot hace su propia llamada a Binance")
    print(f"   Total llamadas: {len(bots)} requests cada 60 segundos")
    print(f"   = {len(bots) * 60} requests/hora")
    print()
    
    # SISTEMA NUEVO
    print("🟢 SISTEMA NUEVO (Market Data Service):")
    print("   Un worker por cada par único (símbolo + timeframe)")
    unique_pairs = len(set((symbol, tf) for _, symbol, tf in bots))
    print(f"   Total workers: {unique_pairs}")
    print(f"   Total llamadas: {unique_pairs} requests cada 60-120 segundos")
    print(f"   = ~{unique_pairs * 30} requests/hora")
    print()
    
    reduction = ((len(bots) - unique_pairs) / len(bots)) * 100
    print(f"💰 AHORRO: {reduction:.1f}% de reducción en llamadas a Binance!")
    print()
    
    # Suscribir todos los bots
    print("=" * 70)
    print("🚀 INICIANDO BOTS...")
    print("=" * 70)
    print()
    
    for bot_id, symbol, timeframe in bots:
        market_data_service.subscribe(bot_id, symbol, timeframe)
        time.sleep(0.5)  # Pequeña pausa para ver los logs
    
    print()
    print("⏳ Esperando 10 segundos para que se carguen los datos...")
    time.sleep(10)
    
    # Obtener estadísticas
    print()
    print("=" * 70)
    print("📊 ESTADÍSTICAS DEL SERVICIO")
    print("=" * 70)
    
    stats = market_data_service.get_stats()
    
    print(f"   Pares activos: {stats['active_pairs']}")
    print(f"   Workers activos: {stats['active_workers']}")
    print(f"   Total suscriptores: {stats['total_subscribers']}")
    print(f"   Datasets en cache: {stats['cached_datasets']}")
    print()
    
    print("   Detalle por par:")
    for pair_key, pair_data in stats['pairs'].items():
        print(f"      • {pair_key}: {pair_data['subscribers']} bots suscriptores")
    print()
    
    # Probar obtención de datos
    print("=" * 70)
    print("🔍 PROBANDO OBTENCIÓN DE DATOS")
    print("=" * 70)
    print()
    
    for symbol, timeframe in [("BTCUSDT", "15m"), ("ETHUSDT", "1h"), ("BNBUSDT", "5m")]:
        df = market_data_service.get_data(symbol, timeframe)
        if df is not None:
            last_price = df['close'].iloc[-1]
            print(f"✅ {symbol}/{timeframe}: {len(df)} velas, último precio: ${last_price:,.2f}")
        else:
            print(f"❌ {symbol}/{timeframe}: No hay datos disponibles")
    
    print()
    print("⏳ Esperando 15 segundos para ver actualizaciones...")
    time.sleep(15)
    
    # Desuscribir algunos bots
    print()
    print("=" * 70)
    print("🛑 DESUSCRIBIENDO BOTS...")
    print("=" * 70)
    print()
    
    # Desuscribir los 3 bots de BTC (el worker debería detenerse)
    for bot_id, symbol, timeframe in bots[:3]:
        market_data_service.unsubscribe(bot_id, symbol, timeframe)
        time.sleep(0.5)
    
    print()
    print("⏳ Esperando 5 segundos...")
    time.sleep(5)
    
    # Ver estadísticas finales
    print()
    print("=" * 70)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 70)
    
    final_stats = market_data_service.get_stats()
    
    print(f"   Pares activos: {final_stats['active_pairs']}")
    print(f"   Workers activos: {final_stats['active_workers']}")
    print(f"   Total suscriptores: {final_stats['total_subscribers']}")
    print()
    
    # Shutdown completo
    print("=" * 70)
    print("🛑 DETENIENDO SERVICIO")
    print("=" * 70)
    print()
    
    market_data_service.shutdown()
    
    print()
    print("=" * 70)
    print("✅ TEST COMPLETADO")
    print("=" * 70)
    print()
    
    print("📋 RESUMEN:")
    print(f"   • Sistema ANTIGUO: {len(bots)} llamadas/minuto")
    print(f"   • Sistema NUEVO: {unique_pairs} llamadas/2-5 minutos")
    print(f"   • Reducción: {reduction:.1f}%")
    print()
    print("💡 BENEFICIOS:")
    print("   ✅ Menos carga en Binance API")
    print("   ✅ Menor riesgo de rate limiting")
    print("   ✅ Menor consumo de ancho de banda")
    print("   ✅ Datos más consistentes entre bots")
    print("   ✅ Escalable a cientos de usuarios")
    print()


if __name__ == "__main__":
    test_market_data_service()
