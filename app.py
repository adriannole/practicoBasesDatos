import time
import random
import threading
import psycopg2
from pymongo import MongoClient
from datetime import datetime

# --- CONFIGURACIÓN ---
NUM_REGISTROS = 5000  # Total de datos a enviar por prueba
NUM_HILOS = 10        # Simula 10 camiones enviando datos simultáneamente

# --- 1. PREPARACIÓN DE POSTGRESQL (SQL) ---
def get_pg_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password123",
        port="5432"
    )

# Pre-cargamos datos base (Conductores y Camiones) para respetar la Integridad Referencial
def setup_sql():
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        # Limpiamos datos previos
        cur.execute("TRUNCATE telemetria, conductores, camiones RESTART IDENTITY CASCADE;")
        
        # Insertamos un conductor y un camión genérico para las pruebas
        cur.execute("INSERT INTO conductores (nombre, licencia) VALUES ('Juan Perez', 'LIC-001')")
        cur.execute("INSERT INTO camiones (placa, modelo) VALUES ('P-101', 'Volvo FH')")
        
        conn.commit()
        cur.close()
        conn.close()
        print(" SQL: Datos base (Conductor/Camión) creados.")
    except Exception as e:
        print(f" Error setup SQL: {e}")

# Función que ejecutará cada "hilo" para SQL
def tarea_sql():
    conn = get_pg_connection()
    cur = conn.cursor()
    for _ in range(int(NUM_REGISTROS / NUM_HILOS)):
        # En SQL, insertamos solo la telemetría referenciando los IDs existentes (1 y 1)
        # El costo aquí es la verificación de las Claves Foráneas (ACID)
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

# --- 2. PREPARACIÓN DE MONGODB (NoSQL) ---
def get_mongo_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test"]
    return db["eventos_logistica"]

def setup_mongo():
    # En Mongo simplemente borramos la colección para empezar de cero
    col = get_mongo_collection()
    col.drop()
    print(" NoSQL: Colección limpia.")

# Función que ejecutará cada "hilo" para NoSQL
def tarea_nosql():
    col = get_mongo_collection()
    datos_batch = []
    for _ in range(int(NUM_REGISTROS / NUM_HILOS)):
        # En NoSQL, enviamos TODO el documento junto (Desnormalizado)
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
        # Insertamos uno por uno para simular tráfico real (no bulk)
        col.insert_one(documento)

# --- 3. EL JUEZ (MEDICIÓN DE TIEMPO) ---
def correr_prueba(nombre, funcion_tarea, funcion_setup):
    print(f"\n--- Iniciando prueba: {nombre} ---")
    funcion_setup()
    
    hilos = []
    inicio = time.time()
    
    # Creamos los "camiones" (hilos) simultáneos
    for _ in range(NUM_HILOS):
        t = threading.Thread(target=funcion_tarea)
        hilos.append(t)
        t.start()
    
    # Esperamos a que todos terminen
    for t in hilos:
        t.join()
        
    fin = time.time()
    duracion = fin - inicio
    print(f" {nombre} terminó en: {duracion:.4f} segundos")
    return duracion

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print(f" Iniciando Benchmark con {NUM_REGISTROS} registros...")
    
    tiempo_sql = correr_prueba("PostgreSQL (SQL)", tarea_sql, setup_sql)
    tiempo_nosql = correr_prueba("MongoDB (NoSQL)", tarea_nosql, setup_mongo)

    print("\n--- RESULTADOS FINALES ---")
    if tiempo_nosql < tiempo_sql:
        diff = (tiempo_sql / tiempo_nosql)
        print(f" MongoDB fue {diff:.2f}x veces más rápido.")
    else:
        print(" PostgreSQL fue más rápido (¡Sorpresa!).")