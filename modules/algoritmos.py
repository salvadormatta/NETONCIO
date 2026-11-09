import networkx as nx
import pandas as pd

from modules.grafo import (
    construir_grafo,
    matriz_inicial_caminos
)


def componentes_conexas(d, modo=None):
    g = construir_grafo(d)

    por_id = {
        p["id"]: p
        for p in d["personas"]
    }

    # Para grafos dirigidos se utiliza NetworkX.
    if g.is_directed():
        if modo == "Fuertemente conexas":
            grupos = nx.strongly_connected_components(g)
        else:
            grupos = nx.weakly_connected_components(g)

        return [
            [por_id[v] for v in grupo]
            for grupo in grupos
        ]

    # Para grafos no dirigidos se utiliza la matriz de caminos.
    resultado = matriz_caminos_completo(d)
    matriz = resultado["ordenada"].values.tolist()
    indices = resultado["indices_ordenados"]

    componentes = []
    inicio = 0
    n = len(matriz)

    while inicio < n:
        tamanio = sum(matriz[inicio])
        fin = inicio + tamanio

        grupo = [
            por_id[indices[i]]
            for i in range(inicio, fin)
        ]

        componentes.append(grupo)
        inicio = fin

    return componentes


def recorrido_dfs(d, inicio):
    g = construir_grafo(d)

    nombres = {
        p["id"]: p["nombre"]
        for p in d["personas"]
    }

    visitados = []
    pasos = []

    def dfs(v):
        visitados.append(v)

        pasos.append({
            "visitados": [
                nombres[x] for x in visitados
            ],
            "mensaje": (
                f"Se visita a {nombres[v]}. "
                "Ahora se revisan sus vecinos no visitados."
            )
        })

        for w in sorted(g.neighbors(v)):
            if w not in visitados:
                dfs(w)

    if inicio in g:
        dfs(inicio)

    return pasos or [{
        "visitados": [],
        "mensaje": "No hay vértices para recorrer."
    }]


def matriz_caminos_completo(d):
    inicial = matriz_inicial_caminos(d)

    nombres = list(inicial.index)
    matriz = inicial.values.tolist()
    n = len(matriz)

    pasos = []

    if n == 0:
        return {
            "inicial": inicial,
            "final": inicial.copy(),
            "ordenada": inicial.copy(),
            "pasos": [],
            "orden": [],
            "conteos": [],
            "indices_ordenados": []
        }

    # PASO 2: Construcción de la matriz de caminos.
    # Cada vértice se utiliza como intermediario.
    # Se aplica el algoritmo de Warshall.

    for k in range(n):
        nuevos_caminos = []

        for i in range(n):
            for j in range(n):

                if (
                    matriz[i][k] == 1
                    and matriz[k][j] == 1
                    and matriz[i][j] == 0
                ):
                    matriz[i][j] = 1

                    nuevos_caminos.append(
                        f"{nombres[i]} → {nombres[j]}"
                    )

        if nuevos_caminos:
            descripcion = (
                "Se encontraron nuevos caminos: "
                + ", ".join(nuevos_caminos)
                + "."
            )
        else:
            descripcion = (
                "No se encontraron caminos nuevos "
                "utilizando este vértice intermediario."
            )

        pasos.append({
            "numero": k + 1,
            "vertice": nombres[k],
            "mensaje": (
                f"Se utiliza a {nombres[k]} como "
                f"vértice intermediario. {descripcion}"
            ),
            "matriz": [
                fila.copy()
                for fila in matriz
            ]
        })

    # Matriz de caminos final.
    final = pd.DataFrame(
        matriz,
        index=nombres,
        columns=nombres
    )

    # PASO 3: Contar los unos de cada fila.
    conteos = [
        sum(fila)
        for fila in matriz
    ]

    # PASO 4: Ordenar filas de mayor a menor.
    # En caso de empate, se prioriza el primer 1
    # más cercano a la primera columna.

    def primer_uno(fila):
        for posicion, valor in enumerate(fila):
            if valor == 1:
                return posicion
        return n

    indices_ordenados = sorted(
        range(n),
        key=lambda i: (
            -conteos[i],
            primer_uno(matriz[i])
        )
    )

    # PASO 5: Ordenar las columnas siguiendo
    # exactamente el mismo orden de las filas.

    matriz_ordenada = [
        [
            matriz[i][j]
            for j in indices_ordenados
        ]
        for i in indices_ordenados
    ]

    nombres_ordenados = [
        nombres[i]
        for i in indices_ordenados
    ]

    ordenada = pd.DataFrame(
        matriz_ordenada,
        index=nombres_ordenados,
        columns=nombres_ordenados
    )

    orden = [
        nombres[i]
        for i in indices_ordenados
    ]

    conteos_ordenados = [
        conteos[i]
        for i in indices_ordenados
    ]

    return {
        "inicial": inicial,
        "final": final,
        "ordenada": ordenada,
        "pasos": pasos,
        "orden": orden,
        "conteos": conteos_ordenados,
        "indices_ordenados": [
            nombres[i]
            for i in indices_ordenados
        ]
    }
