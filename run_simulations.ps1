# run_simulations.ps1

# Crear un archivo para almacenar los resultados consolidados
"num_lifters,tiempo_total,basuras_recolectadas,eficiencia" | Out-File -FilePath "resultados_consolidados.csv"

for ($i = 1; $i -le 5; $i++) {
    Write-Host "`nEjecutando simulación con $i montacargas..."
    python Main.py Simulacion --lifters $i --Basuras 10 --Delta 0.05 --distancia 20.0 --trailer_coords "8:2" --descarga_coords "2:2" --velocidad 0.7
    
    # Renombrar los archivos generados para no sobrescribirlos
    if (Test-Path "metricas_simulacion.png") {
        Move-Item -Force "metricas_simulacion.png" "metricas_simulacion_$i.png"
    }
    if (Test-Path "Registros.csv") {
        Move-Item -Force "Registros.csv" "Registros_$i.csv"
    }
    
    Start-Sleep -Seconds 2
}

# Ejecutar script de análisis
python analyze_results.py