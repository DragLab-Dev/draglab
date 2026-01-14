"""
Strategy Evaluator
Evalúa estrategias de trading basadas en bloques visuales
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from market_data import MarketDataProvider

class StrategyEvaluator:
    """Evaluador de estrategias de trading"""
    
    def __init__(self):
        self.market_data = MarketDataProvider()
        self.indicator_cache = {}
    
    def evaluate_strategy(self, df: pd.DataFrame, strategy: Dict[str, List[Dict]], zone: str) -> bool:
        """
        Evaluar una zona de estrategia (entry_long, exit_long, entry_short, exit_short)
        
        Args:
            df: DataFrame con datos de mercado
            strategy: Configuración de la estrategia
            zone: Zona a evaluar ('entry_long', 'exit_long', 'entry_short', 'exit_short')
        
        Returns:
            True si se cumple la condición, False en caso contrario
        """
        if zone not in strategy or not strategy[zone]:
            return False
        
        blocks = strategy[zone]
        
        # Evaluar la cadena de bloques
        try:
            result = self._evaluate_blocks(df, blocks)
            return bool(result)
        except Exception as e:
            print(f"Error evaluating strategy for zone {zone}: {e}")
            return False
    
    def _reorder_blocks_to_rpn(self, blocks: List[Dict]) -> List[Dict]:
        """
        Reordenar bloques de notación infija a postfija (RPN)
        Ejemplo: [Value, Operator, Value] → [Value, Value, Operator]
        """
        result = []
        i = 0
        
        while i < len(blocks):
            block = blocks[i]
            block_type = block.get('type', '')
            
            # Si es un operador de comparación y hay bloques antes y después
            if (block_type in ['operator', 'comparison']) and i > 0 and i < len(blocks) - 1:
                # Patrón: [Value, Operator, Value]
                # Ya tenemos el value anterior en result, agregar el siguiente value primero
                if i + 1 < len(blocks):
                    result.append(blocks[i + 1])  # Agregar el value de la derecha
                result.append(block)  # Luego agregar el operador
                i += 2  # Saltar el siguiente value porque ya lo agregamos
            else:
                result.append(block)
                i += 1
        
        return result
    
    def _evaluate_blocks(self, df: pd.DataFrame, blocks: List[Dict]) -> Any:
        """
        Evaluar una secuencia de bloques
        
        Los bloques se evalúan de forma secuencial:
        - Indicadores: retornan valores numéricos
        - Operadores de comparación: comparan dos valores
        - Operadores lógicos: combinan condiciones booleanas
        """
        if not blocks:
            print("⚠️ No blocks to evaluate")
            return False
        
        print(f"🔍 Evaluating {len(blocks)} blocks...")
        
        # Reordenar bloques para notación postfija (RPN)
        # Convertir [Value, Operator, Value] a [Value, Value, Operator]
        reordered_blocks = self._reorder_blocks_to_rpn(blocks)
        
        # Stack para evaluar expresiones
        values = []
        
        for i, block in enumerate(reordered_blocks):
            block_type = block.get('type', '')
            block_name = block.get('name', '')
            params = block.get('params', {})
            
            print(f"  Block {i+1}: type='{block_type}', name='{block_name}', params={params}")
            
            if block_type == 'indicator':
                # Calcular indicador
                value = self._calculate_indicator(df, block_name, params)
                print(f"    → Indicator value: {value}")
                values.append(value)
                
            elif block_type == 'value':
                # Valor constante (Price, Number, Percentage)
                value = self._get_constant_value(df, block_name, params)
                print(f"    → Constant value: {value}")
                values.append(value)
                
            elif block_type == 'comparison' or block_type == 'operator':
                # Operador de comparación (>, <, >=, <=, =, !=, Crosses)
                # Acepta tanto 'comparison' como 'operator' para compatibilidad
                if len(values) < 2:
                    print(f"    ⚠️ Not enough values in stack (need 2, have {len(values)})")
                    continue
                
                right = values.pop()
                left = values.pop()
                print(f"    → Comparing: {left} {block_name} {right}")
                result = self._compare_values(left, right, block_name)
                print(f"    → Result: {result}")
                values.append(result)
                
            elif block_type == 'logic':
                # Operador lógico (AND, OR, NOT, XOR, NAND, NOR)
                result = self._apply_logic_operator(values, block_name)
                print(f"    → Logic result: {result}")
                values.append(result)
        
        # Retornar el último valor evaluado
        final_result = values[-1] if values else False
        print(f"✅ Final result: {final_result} (values stack: {values})")
        return final_result
    
    def _calculate_indicator(self, df: pd.DataFrame, indicator_name: str, params: Dict) -> float:
        """Calcular un indicador técnico"""
        try:
            if indicator_name == 'EMA':
                period = int(params.get('period', 20))
                ema = self.market_data.calculate_ema(df, period)
                return float(ema.iloc[-1])
            
            elif indicator_name == 'SMA':
                period = int(params.get('period', 20))
                sma = self.market_data.calculate_sma(df, period)
                return float(sma.iloc[-1])
            
            elif indicator_name == 'RSI':
                period = int(params.get('period', 14))
                rsi = self.market_data.calculate_rsi(df, period)
                return float(rsi.iloc[-1])
            
            elif indicator_name == 'MACD':
                fast = int(params.get('fast', 12))
                slow = int(params.get('slow', 26))
                signal = int(params.get('signal', 9))
                macd_data = self.market_data.calculate_macd(df, fast, slow, signal)
                
                component = params.get('component', 'macd')  # macd, signal, histogram
                return float(macd_data[component].iloc[-1])
            
            elif indicator_name == 'BBands':
                period = int(params.get('period', 20))
                std_dev = float(params.get('std_dev', 2))
                bb_data = self.market_data.calculate_bollinger_bands(df, period, std_dev)
                
                band = params.get('band', 'middle')  # upper, middle, lower
                return float(bb_data[band].iloc[-1])
            
            elif indicator_name == 'ATR':
                period = int(params.get('period', 14))
                atr = self.market_data.calculate_atr(df, period)
                return float(atr.iloc[-1])
            
            elif indicator_name == 'Swing':
                lookback = int(params.get('lookback', 5))
                swing_type = params.get('type', 'high')  # high or low
                
                if swing_type == 'high':
                    swings = self.market_data.find_swing_high(df, lookback)
                else:
                    swings = self.market_data.find_swing_low(df, lookback)
                
                # Retornar el último swing válido
                valid_swings = swings.dropna()
                if len(valid_swings) > 0:
                    return float(valid_swings.iloc[-1])
                return 0.0
            
            else:
                print(f"Unknown indicator: {indicator_name}")
                return 0.0
                
        except Exception as e:
            print(f"Error calculating indicator {indicator_name}: {e}")
            return 0.0
    
    def _get_constant_value(self, df: pd.DataFrame, value_name: str, params: Dict) -> float:
        """Obtener un valor constante"""
        try:
            if value_name == 'Price':
                # Precio actual (close de la última vela)
                return float(df['close'].iloc[-1])
            
            elif value_name == 'Number':
                # Número fijo - buscar cualquier key que contenga "value"
                # Puede ser 'value', 'block_2_value', 'block_8_value', etc.
                for key, val in params.items():
                    if 'value' in key.lower():
                        # Eliminar separadores de miles (puntos o comas)
                        val_str = str(val).replace('.', '').replace(',', '.')
                        try:
                            return float(val_str)
                        except:
                            pass
                return float(params.get('value', 0))
            
            elif value_name == 'Percentage':
                # Porcentaje del precio actual
                for key, val in params.items():
                    if 'value' in key.lower():
                        percentage = float(val)
                        current_price = float(df['close'].iloc[-1])
                        return current_price * (percentage / 100.0)
                percentage = float(params.get('value', 0))
                current_price = float(df['close'].iloc[-1])
                return current_price * (percentage / 100.0)
            
            else:
                print(f"Unknown value type: {value_name}")
                return 0.0
                
        except Exception as e:
            print(f"Error getting constant value {value_name}: {e}")
            return 0.0
    
    def _compare_values(self, left: float, right: float, operator: str) -> bool:
        """Comparar dos valores"""
        try:
            if operator == 'GreaterThan':
                return left > right
            
            elif operator == 'LessThan':
                return left < right
            
            elif operator == 'GreaterOrEqual':
                return left >= right
            
            elif operator == 'LessOrEqual':
                return left <= right
            
            elif operator == 'Equal':
                # Usar tolerancia para comparación de floats
                return abs(left - right) < 0.0001
            
            elif operator == 'NotEqual':
                return abs(left - right) >= 0.0001
            
            elif operator == 'Crosses':
                # Cruce: necesitaríamos valores históricos para detectarlo
                # Por ahora, simplificado: left > right
                return left > right
            
            else:
                print(f"Unknown comparison operator: {operator}")
                return False
                
        except Exception as e:
            print(f"Error comparing values: {e}")
            return False
    
    def _apply_logic_operator(self, values: List[Any], operator: str) -> bool:
        """Aplicar operador lógico"""
        try:
            if operator == 'AND':
                if len(values) < 2:
                    return False
                right = bool(values.pop())
                left = bool(values.pop())
                return left and right
            
            elif operator == 'OR':
                if len(values) < 2:
                    return False
                right = bool(values.pop())
                left = bool(values.pop())
                return left or right
            
            elif operator == 'NOT':
                if len(values) < 1:
                    return False
                value = bool(values.pop())
                return not value
            
            elif operator == 'XOR':
                if len(values) < 2:
                    return False
                right = bool(values.pop())
                left = bool(values.pop())
                return left != right
            
            elif operator == 'NAND':
                if len(values) < 2:
                    return False
                right = bool(values.pop())
                left = bool(values.pop())
                return not (left and right)
            
            elif operator == 'NOR':
                if len(values) < 2:
                    return False
                right = bool(values.pop())
                left = bool(values.pop())
                return not (left or right)
            
            else:
                print(f"Unknown logic operator: {operator}")
                return False
                
        except Exception as e:
            print(f"Error applying logic operator: {e}")
            return False
    
    def generate_signal_message(self, symbol: str, signal_type: str, price: float, strategy_info: str = "") -> str:
        """Generar mensaje de señal para Telegram"""
        emoji = "🟢" if "LONG" in signal_type.upper() else "🔴" if "SHORT" in signal_type.upper() else "⚪"
        
        message = f"""
{emoji} <b>SEÑAL DE TRADING</b> {emoji}

📊 Par: <b>{symbol}</b>
📈 Tipo: <b>{signal_type}</b>
💰 Precio: <b>${price:.2f}</b>

🕐 Hora: <b>{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</b>

{strategy_info}

⚠️ <i>Este es un mensaje automatizado. Siempre haz tu propio análisis antes de operar.</i>
        """
        
        return message.strip()
