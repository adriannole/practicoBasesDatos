# 🚀 Comparación de Bases de Datos: SQL vs NoSQL

Aplicación web profesional con Flask para comparar el rendimiento entre **PostgreSQL (SQL)** y **MongoDB (NoSQL)**.

## 📋 Características

✅ **Benchmark de Escritura**: Inserta 50,000 registros con 10 hilos concurrentes  
✅ **Benchmark de Búsqueda**: 3 tipos de consultas (simple, rango, agregación)  
✅ **Gráficas en Tiempo Real**: Visualización con Chart.js  
✅ **Código Simple**: Bien comentado para entender fácilmente  
✅ **Interfaz Moderna**: Bootstrap 5 con diseño responsive  

## 🎯 ¿Qué hace?

Esta aplicación compara el rendimiento real entre SQL y NoSQL en dos escenarios:

1. **Escritura Masiva** (INSERT): Inserta 5,000 registros de telemetría de camiones
2. **Búsquedas** (SELECT/find): Ejecuta consultas con diferentes complejidades

## 🛠️ Instalación

```bash
# 1. Instalar Flask (ya lo hicimos)
pip install flask

# 2. Asegúrate de tener PostgreSQL y MongoDB corriendo
# PostgreSQL en puerto 5432
# MongoDB en puerto 27017
```

## ▶️ Ejecutar la Aplicación

```bash
python app.py
```

Luego abre tu navegador en: **http://localhost:5000**

## 📊 Cómo Usar

### 1️⃣ Benchmark de Escritura
- Click en **"Ejecutar Benchmark de ESCRITURA"**
- Espera unos segundos mientras inserta los datos
- Verás una gráfica comparando los tiempos

### 2️⃣ Benchmark de Búsqueda
- Click en **"Ejecutar Benchmark de BÚSQUEDA"**
- Selecciona el tipo de búsqueda:
  - **Simple**: WHERE temperatura > 25
  - **Rango**: Múltiples condiciones AND
  - **Agregación**: AVG, MAX, MIN
- Verás los tiempos en milisegundos

## 🔧 Explicación del Código (para tu exposición)

### Backend (app.py)

```python
# RUTAS PRINCIPALES:

@app.route('/')  
# → Muestra la interfaz web

@app.route('/api/benchmark', methods=['POST'])  
# → Ejecuta el benchmark de ESCRITURA
# → Usa threading para simular carga concurrente
# → Devuelve tiempos en JSON

@app.route('/api/busqueda', methods=['POST'])  
# → Ejecuta benchmarks de BÚSQUEDA
# → Compara SELECT vs find()
# → Devuelve tiempos y cantidad de registros
```

### Frontend (templates/index.html)

- **Bootstrap 5**: Para el diseño moderno
- **Chart.js**: Para las gráficas interactivas
- **Fetch API**: Para llamadas asíncronas al backend

### Funciones Clave

```python
def ejecutar_benchmark():
    """
    1. Limpia las bases de datos
    2. Crea 10 hilos (threads)
    3. Cada hilo inserta 500 registros
    4. Cronometra el tiempo total
    """

def busqueda_sql(tipo="simple"):
    """
    Ejecuta diferentes tipos de consultas SQL:
    - simple: WHERE temperatura > 25
    - rango: BETWEEN + múltiples condiciones
    - agregacion: AVG, MAX, MIN
    """
```

## 📈 Resultados Esperados

**Escritura**: MongoDB suele ser más rápido (menos validaciones)  
**Búsquedas**: Depende del tipo:
- Simples: MongoDB gana
- Agregaciones: PostgreSQL puede ser más rápido (índices)

## 🎓 Puntos Clave para Exponer

1. **Threading**: Simula carga real con 10 usuarios simultáneos
2. **ACID vs BASE**: SQL garantiza integridad, NoSQL prioriza velocidad
3. **Normalización**: SQL normalizado vs MongoDB desnormalizado
4. **Índices**: Ambos pueden usar índices para acelerar búsquedas
5. **Escalabilidad**: MongoDB horizontal, SQL vertical

## 📝 Notas

- Asegúrate de que las bases de datos estén corriendo antes de ejecutar
- Los tiempos varían según el hardware
- La primera ejecución puede ser más lenta (cache frío)

## 🎨 Personalización

Puedes cambiar estos valores en `app.py`:

```python
NUM_REGISTROS = 5000  # Cantidad de registros
NUM_HILOS = 10        # Hilos concurrentes
```

## 📞 Soporte

Si tienes errores, verifica:
1. PostgreSQL está corriendo (`postgres` user, password `password123`)
2. MongoDB está corriendo en puerto 27017
3. Las tablas existen (conductores, camiones, telemetria)

---

**¡Listo para exponer!** 🎯
