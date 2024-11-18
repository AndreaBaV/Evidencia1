import pandas as pd
import matplotlib.pyplot as plt
import glob
from datetime import datetime

def analizar_resultados():
    # Leer todos los archivos de registro
    resultados = []
    for i in range(1, 6):
        try:
            df = pd.read_csv(f'Registros_{i}.csv')
            
            # Obtener el primer y último timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            tiempo_inicio = df['timestamp'].min()
            tiempo_fin = df['timestamp'].max()
            tiempo_total = (tiempo_fin - tiempo_inicio).total_seconds()
            
            # Asegurarse de que el tiempo total no sea 0
            if tiempo_total == 0:
                tiempo_total = 0.1  # valor mínimo para evitar división por cero
            
            basuras = df['basuras_recolectadas'].max()
            if pd.isna(basuras):  # Si no hay valor, usar 0
                basuras = 0
                
            eficiencia = basuras / (tiempo_total * i) if tiempo_total > 0 else 0
            
            resultados.append({
                'num_lifters': i,
                'tiempo_total': tiempo_total,
                'basuras_recolectadas': basuras,
                'eficiencia': eficiencia
            })
            print(f"\nSimulación con {i} montacargas:")
            print(f"Tiempo total: {tiempo_total:.2f} segundos")
            print(f"Basuras recolectadas: {basuras}")
            print(f"Eficiencia: {eficiencia:.4f}")
            
        except Exception as e:
            print(f"Error procesando Registros_{i}.csv: {str(e)}")
    
    # Crear DataFrame con resultados
    df_resultados = pd.DataFrame(resultados)
    
    if len(df_resultados) > 0:
        # Encontrar número óptimo de montacargas
        eficiencias = df_resultados['eficiencia'].values
        tiempos = df_resultados['tiempo_total'].values
        
        # Calcular mejoras de tiempo solo si hay más de un resultado
        if len(tiempos) > 1:
            mejoras_tiempo = []
            for i in range(len(tiempos)-1):
                if tiempos[i] > 0:
                    mejora = (tiempos[i] - tiempos[i+1])/tiempos[i] * 100
                    mejoras_tiempo.append(mejora)
                else:
                    mejoras_tiempo.append(0)
            
            # Encontrar donde la mejora es menor al 25%
            optimo = 1
            for i, mejora in enumerate(mejoras_tiempo):
                if mejora < 25:
                    optimo = i + 1
                    break
        else:
            optimo = 1
            mejoras_tiempo = []
        
        # Crear gráfica comparativa
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfica de tiempo total
        ax1.plot(df_resultados['num_lifters'], df_resultados['tiempo_total'], 
                marker='o', linewidth=2, markersize=8)
        ax1.set_title('Tiempo Total vs Número de Montacargas')
        ax1.set_xlabel('Número de Montacargas')
        ax1.set_ylabel('Tiempo Total (s)')
        ax1.grid(True)
        
        # Gráfica de eficiencia
        ax2.plot(df_resultados['num_lifters'], df_resultados['eficiencia'], 
                marker='o', linewidth=2, markersize=8)
        ax2.set_title('Eficiencia vs Número de Montacargas')
        ax2.set_xlabel('Número de Montacargas')
        ax2.set_ylabel('Eficiencia (basuras/tiempo*lifters)')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('analisis_final.png')
        
        # Imprimir resultados
        print("\nResultados del análisis:")
        print(df_resultados)
        print(f"\nNúmero óptimo de montacargas: {optimo}")
        print("\nMejoras de tiempo entre configuraciones:")
        for i, mejora in enumerate(mejoras_tiempo):
            print(f"De {i+1} a {i+2} montacargas: {mejora:.2f}% de mejora")
    else:
        print("No se encontraron datos para analizar")

if __name__ == "__main__":
    analizar_resultados()