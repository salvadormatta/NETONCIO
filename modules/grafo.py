import networkx as nx
import pandas as pd


def construir_grafo(d):
    # Seleccionar el tipo de grafo
    tipo = d.get("tipo_grafo", "No dirigido")

    if tipo == "Dirigido":
        g = nx.DiGraph()
    else:
        g = nx.Graph()

    # Agregar vértices
    for p in d["personas"]:
        g.add_node(p["id"], label=p["nombre"])

    # Agregar aristas
    for r in d["relaciones"]:
        g.add_edge(
            r["origen"],
            r["destino"],
            tipo=r.get("tipo", "Amistad")
        )

    return g
def matriz_adyacencia(d):
    ids = [p["id"] for p in d["personas"]]
    labels = [p["nombre"] for p in d["personas"]]

    g = construir_grafo(d)

    matriz = nx.to_numpy_array(
        g,
        nodelist=ids,
        dtype=int
    )

    return pd.DataFrame(
        matriz,
        index=labels,
        columns=labels
    )
def matriz_inicial_caminos(d):
    matriz = matriz_adyacencia(d).copy()

    for i in range(len(matriz)):
        matriz.iloc[i, i] = 1

    return matriz