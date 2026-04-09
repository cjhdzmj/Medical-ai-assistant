from models import SessionLocal, Cita

# services/citas_service.py

def agendar_cita(datos):
    db = SessionLocal()
    try:
        nombre = datos.get("paciente_nombre")
        fecha = datos.get("fecha")
        # Si la IA manda "mañana" como texto en lugar de fecha YYYY-MM-DD
        # el backend fallará. Asegúrate de que llegue como string.
        
        hora = datos.get("hora")
        if not hora or hora == "null":
            hora = "10:00"

        # Validaciones de interrupción temprana
        if not nombre or nombre == "null":
            return {"respuesta_bot": "¡Claro! ¿A nombre de quién registro la cita?"}
        
        if not fecha or fecha == "null":
            return {"respuesta_bot": f"Perfecto {nombre}, ¿para qué día la necesitas?"}

        # --- BUSCAR DUPLICADOS ---
        cita_previa = db.query(Cita).filter(
            Cita.fecha == str(fecha),
            Cita.hora == str(hora),
            Cita.estado == "programada"
        ).first()

        if cita_previa:
            return {"respuesta_bot": f"Lo siento {nombre}, a las {hora} ya hay una cita. ¿Otra hora?"}

        # --- INSERTAR ---
        nueva_cita = Cita(
            paciente_nombre=str(nombre).capitalize(),
            fecha=str(fecha),
            hora=str(hora),
            motivo=str(datos.get("motivo", "Consulta General")),
            estado="programada"
        )

        db.add(nueva_cita)
        db.commit()
        db.refresh(nueva_cita)

        return {
            "respuesta_bot": f"¡Listo {nombre}! Cita guardada para el {fecha} a las {hora}.",
            "cita": {"id": nueva_cita.id}
        }

    except Exception as e:
        db.rollback()
        # ESTA LÍNEA ES LA MÁS IMPORTANTE PARA TI AHORA:
        print(f"ERROR CRÍTICO EN DATABASE: {e}") 
        return {"respuesta_bot": f"Error técnico: {str(e)}"} 
    finally:
        db.close()
        
def cancelar_cita(datos):
    db = SessionLocal()
    try:
        # Buscamos la cita
        cita = db.query(Cita).filter(
            Cita.paciente_nombre == datos.get("paciente_nombre"),
            Cita.fecha == datos.get("fecha"),
            Cita.estado == "programada" # Solo cancelar las que están activas
        ).first()

        if cita:
            cita.estado = "cancelada"
            db.commit()
            return {
                "respuesta_bot": f"Entendido Carlos, tu cita para el {datos.get('fecha')} ha sido cancelada con éxito."
            }
        else:
            return {
                "respuesta_bot": "No encontré ninguna cita programada a tu nombre para esa fecha."
            }
    except Exception as e:
        db.rollback() # Si hay error, deshacemos cambios
        return {"error_sistema": str(e)}
    finally:
        db.close() # <--- ESTO ES VITAL para que el disco no se "llene" o bloquee
