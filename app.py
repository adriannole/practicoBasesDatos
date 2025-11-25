

from flask import Flask, render_template, jsonify, request
import time
import random
import threading
import psycopg2
from pymongo import MongoClient
from datetime import datetime

# ============================================================
# 1. CONFIGURACIÓN DE LA APP FLASK
# ============================================================
app = Flask(__name__)

# Configuración de pruebas
NUM_REGISTROS = 50000  # Total de registros a insertar
NUM_HILOS = 50        # Hilos simultáneos (simula concurrencia)

# ============================================================
# 2. CONEXIÓN A BASES DE DATOS
# ============================================================

def get_pg_connection():
    """Devuelve una conexión a PostgreSQL"""
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password123",
        port="5432"
    )

def get_mongo_collection():
    """Devuelve la colección de MongoDB"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test"]
    return db["eventos_logistica"]

# ============================================================
# 3. PREPARACIÓN DE DATOS
# ============================================================

def setup_sql():
    """Prepara PostgreSQL: crea datos base y limpia tablas"""
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        # Limpiamos datos previos
        cur.execute("TRUNCATE telemetria, conductores, camiones RESTART IDENTITY CASCADE;")
        
        # Insertamos datos base
        cur.execute("INSERT INTO conductores (nombre, licencia) VALUES ('Juan Perez', 'LIC-001')")
        cur.execute("INSERT INTO camiones (placa, modelo) VALUES ('P-101', 'Volvo FH')")
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error setup SQL: {e}")
        return False

def setup_mongo():
    """Prepara MongoDB: limpia la colección"""
    try:
        col = get_mongo_collection()
        col.drop()
        return True
    except Exception as e:
        print(f"Error setup MongoDB: {e}")
        return False

# ============================================================
# 4. FUNCIONES DE ESCRITURA (INSERCIÓN)
# ============================================================

def tarea_sql():
    """Inserta registros en PostgreSQL (tarea de un hilo)"""
    conn = get_pg_connection()
    cur = conn.cursor()
    for _ in range(int(NUM_REGISTROS / NUM_HILOS)):
        query = """
            INSERT INTO telemetria (camion_id, conductor_id, latitud, longitud, temperatura)
            VALUES (1, 1, %s, %s, %s)
        """
        lat = random.uniform(-1.0, 1.0)
        lon = random.uniform(-80.0, -70.0)
        temp = random.uniform(20.0, 30.0)
        cur.execute(query, (lat, lon, temp))
    conn.commit()
    cur.close()
    conn.close()

def tarea_nosql():
    """Inserta documentos en MongoDB (tarea de un hilo)"""
    col = get_mongo_collection()
    for _ in range(int(NUM_REGISTROS / NUM_HILOS)):
        documento = {
            "camion_id": "P-101",
            "conductor": {"nombre": "Juan Perez", "licencia": "LIC-001"},
            "telemetria": {
                "lat": random.uniform(-1.0, 1.0),
                "lon": random.uniform(-80.0, -70.0),
                "temp": random.uniform(20.0, 30.0)
            },
            "timestamp": datetime.now()
        }
        col.insert_one(documento)

# ============================================================
# 5. FUNCIONES DE BÚSQUEDA (CONSULTAS)
# ============================================================

def busqueda_sql(tipo="simple"):
    """
    Realiza búsquedas en PostgreSQL
    tipo: 'simple', 'rango', 'agregacion'
    """
    conn = get_pg_connection()
    cur = conn.cursor()
    
    inicio = time.time()
    
    if tipo == "simple":
        # Búsqueda simple por temperatura
        cur.execute("SELECT * FROM telemetria WHERE temperatura > 25.0 LIMIT 100")
    elif tipo == "rango":
        # Búsqueda con rango
        cur.execute("SELECT * FROM telemetria WHERE latitud BETWEEN -0.5 AND 0.5 AND temperatura > 24.0")
    elif tipo == "agregacion":
        # Agregación (promedio de temperatura)
        cur.execute("SELECT AVG(temperatura), MAX(temperatura), MIN(temperatura) FROM telemetria")
    
    resultado = cur.fetchall()
    fin = time.time()
    
    cur.close()
    conn.close()
    
    return fin - inicio, len(resultado)

def busqueda_mongo(tipo="simple"):
    """
    Realiza búsquedas en MongoDB
    tipo: 'simple', 'rango', 'agregacion'
    """
    col = get_mongo_collection()
    
    inicio = time.time()
    
    if tipo == "simple":
        # Búsqueda simple
        resultado = list(col.find({"telemetria.temp": {"$gt": 25.0}}).limit(100))
    elif tipo == "rango":
        # Búsqueda con rango
        resultado = list(col.find({
            "telemetria.lat": {"$gte": -0.5, "$lte": 0.5},
            "telemetria.temp": {"$gt": 24.0}
        }))
    elif tipo == "agregacion":
        # Agregación con pipeline
        resultado = list(col.aggregate([
            {"$group": {
                "_id": None,
                "avg_temp": {"$avg": "$telemetria.temp"},
                "max_temp": {"$max": "$telemetria.temp"},
                "min_temp": {"$min": "$telemetria.temp"}
            }}
        ]))
    
    fin = time.time()
    
    return fin - inicio, len(resultado)

# ============================================================
# 6. FUNCIÓN PRINCIPAL DE BENCHMARK
# ============================================================

def ejecutar_benchmark():
    """Ejecuta el benchmark completo de escritura"""
    resultados = {}
    
    # Prueba PostgreSQL
    setup_sql()
    hilos = []
    inicio = time.time()
    
    for _ in range(NUM_HILOS):
        t = threading.Thread(target=tarea_sql)
        hilos.append(t)
        t.start()
    
    for t in hilos:
        t.join()
    
    tiempo_sql = time.time() - inicio
    resultados['sql'] = tiempo_sql
    
    # Prueba MongoDB
    setup_mongo()
    hilos = []
    inicio = time.time()
    
    for _ in range(NUM_HILOS):
        t = threading.Thread(target=tarea_nosql)
        hilos.append(t)
        t.start()
    
    for t in hilos:
        t.join()
    
    tiempo_mongo = time.time() - inicio
    resultados['mongo'] = tiempo_mongo
    resultados['registros'] = NUM_REGISTROS
    
    return resultados

# ============================================================
# 7. RUTAS DE LA APLICACIÓN WEB
# ============================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/benchmark', methods=['POST'])
def api_benchmark():
    """Ejecuta el benchmark de escritura y devuelve resultados"""
    try:
        resultados = ejecutar_benchmark()
        return jsonify({
            'success': True,
            'data': resultados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/busqueda', methods=['POST'])
def api_busqueda():
    """Ejecuta benchmarks de búsqueda"""
    try:
        tipo = request.json.get('tipo', 'simple')
        
        # Ejecutar búsqueda en PostgreSQL
        tiempo_sql, count_sql = busqueda_sql(tipo)
        
        # Ejecutar búsqueda en MongoDB
        tiempo_mongo, count_mongo = busqueda_mongo(tipo)
        
        return jsonify({
            'success': True,
            'data': {
                'sql': {
                    'tiempo': tiempo_sql,
                    'registros': count_sql
                },
                'mongo': {
                    'tiempo': tiempo_mongo,
                    'registros': count_mongo
                },
                'tipo': tipo
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# 8. EJECUCIÓN DE LA APP
# ============================================================

if __name__ == "__main__":
    print("Iniciando aplicación web...")
    print("Accede a: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)