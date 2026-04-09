import sqlite3

try:
    # Conectamos a la base de datos
    conexion = sqlite3.connect('database/agenda.db')
    cursor = conexion.cursor()

    # Borramos todo para empezar de cero
    cursor.execute("DELETE FROM citas")
    
    conexion.commit()
    print("✅ ¡Éxito! La base de datos ha sido vaciada completamente.")
    
except Exception as e:
    print(f"❌ Error al limpiar: {e}")
finally:
    if conexion:
        conexion.close()