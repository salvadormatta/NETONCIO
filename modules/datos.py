import json 
import random
from pathlib import Path

RUTA = Path(__file__).resolve().parent.parent / "data" / "comunidad.json"
def cargar_datos():
    RUTA.parent.mkdir(exist_ok=True)
    try:
        return json.loads(RUTA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"personas": [], "relaciones": []}
def guardar_datos(d):
    RUTA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
def agregar_persona(d, nombre):
    n = nombre.strip()
    if not n:
        return False, "Escribe un nombre."
    if len(d["personas"]) >= 12:
        return False, "Máximo 12 personas."
    if any(p["nombre"].casefold() == n.casefold() for p in d["personas"]):
        return False, "Ese nombre ya existe."
    i = max([p["id"] for p in d["personas"]], default=0) + 1
    d["personas"].append({"id": i, "nombre": n})
    return True, f"{n} fue agregado."
def eliminar_persona(d, i):
    if len(d["personas"]) <= 4:
        return False, "Deben quedar al menos 4 personas."
    p = next((p for p in d["personas"] if p["id"] == i), None)
    if not p:
        return False, "Persona no encontrada."
    d["personas"] = [x for x in d["personas"] if x["id"] != i]
    d["relaciones"] = [r for r in d["relaciones"] if i not in (r["origen"], r["destino"])]
    return True, f"{p['nombre']} fue eliminado."
def agregar_relacion(d, a, b, tipo):
    if a == b:
        return False, "Elige dos personas diferentes."
    dirigido = d.get("tipo_grafo", "No dirigido") == "Dirigido"
    if dirigido:
        existe = any(
            r["origen"] == a and r["destino"] == b
            for r in d["relaciones"]
        )
    else:
        existe = any(
            {r["origen"], r["destino"]} == {a, b}
            for r in d["relaciones"]
        )
    if existe:
        return False, "La conexión ya existe."
    d["relaciones"].append({
        "origen": a,
        "destino": b,
        "tipo": tipo
    })
    return True, "Relación agregada."
def eliminar_relacion(d, i):
    d["relaciones"].pop(i)
def generar_datos_aleatorios(d,cantidad):
    if cantidad < 4 or cantidad >12:
        return False, "Cantidad debe estar entre 4 y 12."
    nombres_elegibles = ["Ana", "Luis", "Pedro", "María", "Juan", "Lucía", "Carlos", "Sofía", "Jorge", "Elena", "Diego", "Valeria"]
    personas = []
    for i in range(cantidad):
        personas.append({
            "id": i + 1,
            "nombre": nombres_elegibles[i]
        })
    relaciones =[]
    for i in range(cantidad):
        for j in range(i + 1, cantidad):
            if random.random() < 0.30:
                relaciones.append({
                    "origen": personas[i]["id"],
                    "destino": personas[j]["id"],
                    "tipo": random.choice(["amistad", "seguimiento"])
                })
    d["personas"] = personas
    d["relaciones"] = relaciones
    return True, "Se genero una comunidad aleatoria con {} personas y {} relaciones.".format(cantidad, len(relaciones))