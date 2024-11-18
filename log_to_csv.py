# Módulos necesarios para el procesamiento de datos y visualización
import csv  # Para lectura/escritura de archivos CSV
import re   # Para procesamiento de expresiones regulares
from datetime import datetime  # Para manejo de fechas y tiempos
import matplotlib.pyplot as plt  # Para generación de gráficas
import math  # Para operaciones matemáticas


def calcular_numero_optimo(basuras, tiempo_base):
    """
    basuras: número total de basuras a recolectar
    tiempo_base: tiempo que toma un montacargas en completar un ciclo
    
    La fórmula considera:
    - Tiempo de ciclo por montacargas
    - Interferencia entre montacargas
    - Capacidad del sistema
    """
    # Factor de interferencia (aumenta con más montacargas)
    factor_interferencia = 0.15
    
    # Número óptimo teórico
    n_optimo = math.sqrt(basuras * tiempo_base / factor_interferencia)
    
    return max(1, min(round(n_optimo), basuras))

def save_to_csv(output_lines):
    # Patrones para extraer información
    lifter_pattern = r'Lifter (\d+) - Nodo: (\d+), Status: (\w+), Basuras totales: (\d+)/(\d+)'
    start_pattern = r'\[start\] (.*?)$'
    end_pattern = r'\[end\] (.*?)$'
    
    start_time = None
    end_time = None
    
    # Buscar tiempo de inicio y fin
    for line in output_lines:
        start_match = re.search(start_pattern, line)
        if start_match:
            start_time = datetime.strptime(start_match.group(1).strip(), '%Y-%m-%d %H:%M:%S.%f')
        
        end_match = re.search(end_pattern, line)
        if end_match:
            end_time = datetime.strptime(end_match.group(1).strip(), '%Y-%m-%d %H:%M:%S.%f')
    
    with open('Registros.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'agent_id', 'state', 'pos_x', 'pos_y', 'pos_z', 
                        'nodo_actual', 'nodo_siguiente', 'velocidad', 'tiempo_total', 
                        'basuras_recolectadas'])
        
        for line in output_lines:
            match = re.search(lifter_pattern, line)
            if match:
                agent_id = match.group(1)
                nodo = match.group(2)
                state = match.group(3)
                basuras = match.group(4)
                
                current_time = datetime.now()
                tiempo_total = (current_time - start_time).total_seconds() if start_time else 0
                
                writer.writerow([
                    current_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    agent_id,
                    state,
                    0,  # pos_x
                    0,  # pos_y
                    0,  # pos_z
                    nodo,
                    '',  # nodo_siguiente
                    0,   # velocidad
                    tiempo_total,
                    basuras
                ])
    
    # Generar gráfica
    if start_time and end_time:
        tiempo_total = (end_time - start_time).total_seconds()
        num_lifters = len(agent_states)
        eficiencia = basuras_total / (tiempo_total * num_lifters)
        
        # Calcular número óptimo de montacargas
        tiempo_base = tiempo_total / num_lifters  # tiempo promedio por montacargas
        n_optimo = calcular_numero_optimo(basuras_total, tiempo_base)
        
        print(f"\nNúmero óptimo teórico de montacargas: {n_optimo}")
        
        plt.figure(figsize=(10, 6))
        plt.bar(['Tiempo Total', 'Num Lifters', 'Basuras Total', 'Eficiencia'],
                [tiempo_total, num_lifters, basuras_total, eficiencia])
        plt.title('Métricas de la Simulación')
        plt.ylabel('Valor')
        plt.savefig('metricas_simulacion.png')
        plt.close()
        
        # Imprimir métricas
        print("\nMétricas de la simulación:")
        print(f"Tiempo total: {tiempo_total:.2f} segundos")
        print(f"Número de lifters: {num_lifters}")
        print(f"Total de basuras recolectadas: {basuras_total}")
        print(f"Eficiencia (basuras/tiempo*lifters): {eficiencia:.4f}") 