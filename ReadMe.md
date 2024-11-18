# Sistema Multi-Agente para Recolección

## Autora
**Andrea Bahena Valdés**  
Estudiante de Ingeniería en Tecnologías Computacionales  
Tecnológico de Monterrey

## 📝 Descripción General
Este proyecto implementa un simulador 3D de un sistema multi-agente (SMA) diseñado para optimizar la recolección y gestión de residuos. El sistema utiliza agentes autónomos (montacargas) que trabajan de manera coordinada para transportar residuos desde un punto de recolección (trailer) hasta una zona de descarga (incinerador).

### 🎯 Objetivos del Proyecto
1. Simular un entorno 3D realista para la operación de montacargas autónomos
2. Implementar algoritmos de coordinación multi-agente
3. Analizar y optimizar la eficiencia del sistema
4. Generar métricas y visualizaciones para análisis de rendimiento

## 🛠️ Arquitectura del Sistema

### Componentes Principales

#### 1. Sistema de Simulación (`LIB_TC2008B.py`)
- Motor de renderizado 3D usando OpenGL
- Gestión de texturas y materiales
- Sistema de coordenadas y transformaciones
- Control de cámara y visualización

#### 2. Agentes Montacargas (`Lifter.py`)
```python
class Lifter:
    def __init__(self, dim, vel, textures, id, start_pos, start_node, delay_inicio=0, distancia_min=20):
        # Inicialización de atributos
        self.status = "searching"  # Estados: searching, lifting, unloading
        self.Position = numpy.array(start_pos, dtype=numpy.float64)
        self.velocidad = vel
```
- Implementación de comportamientos autónomos
- Sistema de estados (búsqueda, carga, descarga)
- Algoritmos de pathfinding
- Detección y evasión de colisiones

#### 3. Gestión de Objetos (`Basura.py`, `Trailer.py`)
```python
class Trailer:
    def __init__(self, position=None):
        self.Position = position if position is not None else [-100, 0, -100]
        self.scale = 15.0
```
- Modelado de objetos 3D
- Sistema de posicionamiento
- Gestión de estados y propiedades

## 🔄 Flujo de Trabajo del Sistema

### 1. Inicialización
```python
def Init(Options):
    # Configuración inicial del sistema
    global lifters, basuras, trailer
    
    # Inicializar contadores globales
    LifterModule.max_basuras = Options.Basuras
    LifterModule.basuras_recolectadas = 0
```

### 2. Ciclo Principal
```python
def update(self, delta):
    # Lógica principal de los agentes
    if self.status == "searching":
        # Búsqueda de objetivos
    elif self.status == "lifting":
        # Proceso de carga
    elif self.status == "unloading":
        # Proceso de descarga
```

### 3. Sistema de Análisis
```python
def analizar_resultados():
    # Procesamiento de métricas
    resultados = []
    for i in range(1, 6):
        try:
            df = pd.read_csv(f'Registros_{i}.csv')
            # Análisis de eficiencia
```

## 📊 Métricas y Análisis

### Métricas Principales
1. **Tiempo Total de Operación**
   - Tiempo desde inicio hasta completar todas las tareas
   - Medido en segundos

2. **Eficiencia por Agente**
   - Basuras recolectadas / (tiempo total * número de agentes)
   - Optimización de recursos

3. **Distancia Recorrida**
   - Tracking de rutas
   - Optimización de trayectorias

### Visualizaciones
- Gráficas de tiempo vs número de agentes
- Mapas de calor de actividad
- Diagramas de eficiencia

## 🚀 Guía de Uso

### Instalación
```bash
# 1. Clonar repositorio
git clone [https://github.com/AndreaBaV/Evidencia1]

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Configuración
```yaml
# Settings.yaml
DimBoard: 100
screen_width: 800
screen_height: 600
FOVY: 60.0
```

### Ejecución
```bash
# Simulación básica
python Main.py Simulacion --lifters 3 --Basuras 10 --Delta 0.05

# Simulación con parámetros avanzados
python Main.py Simulacion \
    --lifters 5 \
    --Basuras 20 \
    --Delta 0.05 \
    --distancia 20.0 \
    --trailer_coords "8:2" \
    --descarga_coords "2:2" \
    --velocidad 0.7
```

### Parámetros Detallados
| Parámetro | Descripción | Valor Default |
|-----------|-------------|---------------|
| lifters | Número de montacargas | Requerido |
| Basuras | Cantidad de residuos | Requerido |
| Delta | Velocidad de simulación | 0.05 |
| distancia | Distancia mínima entre agentes | 20.0 |
| velocidad | Velocidad base de agentes | 0.7 |

## 📁 Estructura del Proyecto
```
proyecto/
├── src/
│   ├── Main.py                 # Punto de entrada
│   ├── LIB_TC2008B.py         # Motor principal
│   ├── Lifter.py              # Lógica de agentes
│   ├── Trailer.py             # Objeto trailer
│   ├── Basura.py              # Objeto residuo
│   └── Cubo.py                # Base geométrica
├── analysis/
│   ├── analyze_results.py      # Análisis
│   └── log_to_csv.py          # Logging
├── config/
│   └── Settings.yaml          # Configuración
├── scripts/
│   └── run_simulations.py     # Automatización
└── docs/
    └── README.md              # Documentación
```

## 🔍 Detalles Técnicos

### Algoritmos Principales
1. **Pathfinding**
   - Implementación de A*
   - Optimización de rutas

2. **Coordinación Multi-agente**
   - Sistema de prioridades
   - Evitación de colisiones

3. **Análisis de Eficiencia**
   - Métricas de rendimiento
   - Optimización de recursos

## 🤝 Contribuciones
Las contribuciones son bienvenidas 

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Contacto
Andrea Bahena Valdés
- Email: [andreabahenavs@gmail.com]
- GitHub: [@AndreaBaV]
- LinkedIn: [Andrea Bahena Valdés]
