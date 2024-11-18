import argparse, datetime  # Importamos las librerías
import LIB_TC2008B		   # Importamos el script
import sys
import io
from contextlib import redirect_stdout
from log_to_csv import save_to_csv

def main():
	parser = argparse.ArgumentParser("TC2008B Base reto", description = "Base del reto");
	subparsers = parser.add_subparsers();
	
 	# Subparsers para la Simulación (Agentes, basuras, tiempo, theta, radious) 
	subparser = subparsers.add_parser("Simulacion",  description = "Corre simulacion");
	subparser.add_argument("--lifters", required = True, type = int, help = "Numero de montacargas");
	subparser.add_argument("--Basuras", required = True, type = int, help = "Numero de cajas a descargar");			
	subparser.add_argument("--Delta", required = False, type = float, default = 0.05, help = "Velocidad de simulacion");
	
	subparser.add_argument("--theta", required = False, type = float, default = 0, help = "");	
	subparser.add_argument("--radious", required = False, type = float, default = 30, help = "");
	subparser.add_argument("--distancia", required = True, type = float, default = 20.0, help = "Distancia entre agentes");
	subparser.add_argument("--velocidad", required = False, type = float, default = 0.7, help = "Velocidad base de los lifters");
	subparser.add_argument("--trailer_coords", required = False, type = str, default = "1:1", help = "Coordenadas del trailer (8:2)");
	subparser.add_argument("--descarga_coords", required = False, type = str, default = "0:0", help = "Coordenadas de la zona de descarga (2:2)");
	subparser.set_defaults(func = LIB_TC2008B.Simulacion);

	# Subparsers para los Nodos (Número de nodos)
	Options = parser.parse_args();
	
	print(str(Options) + "\n");

	# Capturar la salida de la simulación
	output = io.StringIO()
	# Crear un objeto que escriba tanto a stdout como al StringIO
	class TeeOutput:
		def write(self, data):
			output.write(data)
			sys.__stdout__.write(data)
		def flush(self):
			output.flush()
			sys.__stdout__.flush()

	with redirect_stdout(TeeOutput()):
		try:
			Options.func(Options)
		except KeyboardInterrupt:
			print("\nSimulación terminada por el usuario")
		finally:
			output_lines = output.getvalue().split('\n')
			save_to_csv(output_lines)
			print("\nRegistros guardados en Registros.csv")


if __name__ == "__main__":
	print("\n" + "\033[0;32m" + "[start] " + str(datetime.datetime.now()) + "\033[0m" + "\n");
	main();
	print("\n" + "\033[0;32m" + "[end] "+ str(datetime.datetime.now()) + "\033[0m" + "\n");