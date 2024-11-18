import subprocess
import time

for i in range(1, 6):
    print(f"Ejecutando simulación con {i} montacargas...")
    cmd = f"python Main.py Simulacion --lifters {i} --Basuras 10 --Delta 0.05 --distancia 20.0 --trailer_coords 8:2 --descarga_coords 2:2"
    subprocess.run(cmd, shell=True)
    time.sleep(2)