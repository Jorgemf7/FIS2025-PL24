from datetime import datetime, timedelta

def validar_fecha(fecha_texto):
    """Valida formato YYYY-MM-DD y devuelve un objeto date."""
    try:
        return datetime.strptime(fecha_texto, "%Y-%m-%d").date()
    except ValueError:
        print("❌ Error: Formato de fecha incorrecto. Use YYYY-MM-DD.")
        return None
