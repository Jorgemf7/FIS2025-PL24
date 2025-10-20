import json
import csv

def cargar_json(ruta):
    """Carga un JSON desde archivo y devuelve una lista de registros.
    Acepta tanto una lista directa como un objeto con una sola clave. """
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    
    if isinstance(data, list):
        return data

    # Si es un dict con una sola clave 
    if isinstance(data, dict):
        
        for v in data.values():
            if isinstance(v, list):
                return v
        
        return [data]

    
    raise ValueError(f"Formato JSON inesperado en {ruta}")


def cargar_csv(ruta):
    """Carga un CSV y devuelve una lista de diccionarios."""
    with open(ruta, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)
