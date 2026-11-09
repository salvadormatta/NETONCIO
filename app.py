import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import math
from modules.datos import *
from modules.grafo import *
from modules.algoritmos import *

def posiciones_componentes(G, grupos):
    """Organiza los grupos y separa claramente a sus integrantes."""

    posiciones = {}

    cantidad = len(grupos)

    if cantidad == 0:
        return posiciones

    columnas = min(3, cantidad)
    filas = math.ceil(cantidad / columnas)

    separacion_x = 4.5
    separacion_y = 4.0

    for i, grupo in enumerate(grupos):

        ids = [p["id"] for p in grupo]
        n = len(ids)

        # Distribuir los integrantes en círculo
        if n == 1:
            pos_local = {ids[0]: (0, 0)}

        else:
            pos_local = nx.circular_layout(
                G.subgraph(ids),
                scale=max(1.5, n * 0.45)
            )

        columna = i % columnas
        fila = i // columnas

        centro_x = (
            columna - (columnas - 1) / 2
        ) * separacion_x

        centro_y = (
            (filas - 1) / 2 - fila
        ) * separacion_y

        for nodo, (x, y) in pos_local.items():
            posiciones[nodo] = (
                x + centro_x,
                y + centro_y
            )

    return posiciones

def dibujar_aristas(G, posiciones, ax):
    """
    Dibuja las conexiones.
    Si el grafo es dirigido, muestra las flechas.
    """

    nx.draw_networkx_edges(
        G,
        posiciones,
        ax=ax,
        edge_color="#718096",
        width=2,
        arrows=G.is_directed(),
        arrowstyle="-|>",
        arrowsize=24,
        min_source_margin=18,
        min_target_margin=22,
        connectionstyle="arc3,rad=0.10"
    )


# =====================================================
# CONFIGURACIÓN DE STREAMLIT
# =====================================================

st.set_page_config(
    page_title="NETONCIO",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 NETONCIO")

st.caption(
    "Construcción y análisis de grafos mediante "
    "componentes conexas"
)


# =====================================================
# CARGAR DATOS
# =====================================================

if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()

d = st.session_state.datos


def save():
    guardar_datos(d)


# =====================================================
# CONFIGURACIÓN DEL TIPO DE GRAFO
# =====================================================

tipo_grafo = st.sidebar.radio(
    "TIPO DE GRAFO",
    ["No dirigido", "Dirigido"]
)

d["tipo_grafo"] = tipo_grafo


if tipo_grafo == "Dirigido":

    modo_componentes = st.sidebar.radio(
        "TIPO DE COMPONENTES",
        [
            "Fuertemente conexas",
            "Débilmente conexas"
        ]
    )

else:
    modo_componentes = None


# =====================================================
# MENÚ PRINCIPAL
# =====================================================

menu = st.sidebar.radio(
    "MENÚ PRINCIPAL",
    [
        "Comunidad",
        "Relaciones",
        "Matriz de adyacencia",
        "Matriz de caminos",
        "Visualización del grafo",
        "Componentes conexas"
    ]
)


# Construir el grafo según el tipo seleccionado
G = construir_grafo(d)


# =====================================================
# 1. COMUNIDAD
# =====================================================

if menu == "Comunidad":

    st.header("Personas de la comunidad")

    st.caption(
        "Registra entre 4 y 12 personas."
    )

    with st.form("addperson", clear_on_submit=True):

        nombre = st.text_input("Nombre")

        if st.form_submit_button("Agregar persona"):

            ok, msg = agregar_persona(d, nombre)

            st.toast(msg)

            if ok:
                save()

            st.rerun()

    st.divider()

    st.subheader("Generar comunidad aleatoria")

    cantidad = st.number_input(
        "Cantidad de personas",
        min_value=4,
        max_value=12,
        value=6,
        step=1
    )

    if st.button("Generar comunidad aleatoria"):

        ok, msg = generar_datos_aleatorios(
            d,
            cantidad
        )

        st.toast(msg)

        if ok:
            save()

        st.rerun()

    st.divider()

    st.metric(
        "Personas registradas",
        f"{len(d['personas'])} / 12"
    )

    for p in d["personas"]:

        a, b = st.columns([5, 1])

        a.write("👤 **" + p["nombre"] + "**")

        if b.button(
            "Eliminar",
            key=f"p{p['id']}"
        ):

            ok, msg = eliminar_persona(d, p["id"])

            st.toast(msg)

            if ok:
                save()

            st.rerun()


# =====================================================
# 2. RELACIONES
# =====================================================

elif menu == "Relaciones":

    st.header("Registrar conexiones")

    if len(d["personas"]) < 2:

        st.info("Registra al menos dos personas.")

    else:

        names = {
            p["id"]: p["nombre"]
            for p in d["personas"]
        }

        with st.form("addrel"):

            c1, c2 = st.columns(2)

            a = c1.selectbox(
                "Persona de origen",
                list(names),
                format_func=lambda x: names[x]
            )

            b = c2.selectbox(
                "Persona de destino",
                list(names),
                index=1,
                format_func=lambda x: names[x]
            )

            tipo = st.selectbox(
                "Tipo de relación",
                ["Amistad", "Seguimiento"]
            )

            if st.form_submit_button("Agregar conexión"):

                ok, msg = agregar_relacion(
                    d,
                    a,
                    b,
                    tipo
                )

                st.toast(msg)

                if ok:
                    save()

                st.rerun()

        st.divider()

        st.subheader("Conexiones registradas")

        if not d["relaciones"]:

            st.info("Todavía no existen conexiones.")

        for i, r in enumerate(d["relaciones"]):

            origen = names.get(r["origen"], "?")
            destino = names.get(r["destino"], "?")

            if tipo_grafo == "Dirigido":
                descripcion = f"{origen} → {destino}"

            else:
                descripcion = f"{origen} — {destino}"

            x, y = st.columns([5, 1])

            x.write(
                f"**{descripcion}** · {r['tipo']}"
            )

            if y.button(
                "Quitar",
                key=f"r{i}"
            ):

                eliminar_relacion(d, i)

                save()

                st.rerun()


# =====================================================
# 3. MATRIZ DE ADYACENCIA
# =====================================================

elif menu == "Matriz de adyacencia":

    st.header("Matriz de adyacencia")

    st.caption(
        f"Tipo de grafo: {tipo_grafo}"
    )

    if d["personas"]:

        st.dataframe(
            matriz_adyacencia(d),
            use_container_width=True
        )

        if tipo_grafo == "Dirigido":

            st.info(
                "Las filas representan los vértices de origen "
                "y las columnas los vértices de destino."
            )

        else:

            st.info(
                "Al ser un grafo no dirigido, la matriz "
                "es simétrica."
            )

    else:

        st.info("Agrega personas para generar la matriz.")


# =====================================================
# 4. MATRIZ DE CAMINOS
# =====================================================


elif menu == "Matriz de caminos":
    st.header("Matriz de caminos")

    if len(d["personas"]) == 0:
        st.warning(
            "Primero debes agregar personas a la comunidad."
        )

    else:
        resultado = matriz_caminos_completo(d)

        st.subheader("1. Matriz inicial de caminos")

        st.write(
            "Se parte de la matriz de adyacencia y se "
            "colocan unos en la diagonal principal."
        )

        st.dataframe(
            resultado["inicial"],
            use_container_width=True
        )

        st.subheader("2. Matriz de caminos final")

        st.write(
            "Se utiliza cada vértice como intermediario "
            "para identificar todos los caminos posibles."
        )

        st.dataframe(
            resultado["final"],
            use_container_width=True
        )

        # Botón para mostrar u ocultar el procedimiento.
        if "mostrar_pasos_matriz" not in st.session_state:
            st.session_state.mostrar_pasos_matriz = False

        if st.button(
            "📘 Ver procedimiento paso a paso",
            use_container_width=True
        ):
            st.session_state.mostrar_pasos_matriz = (
                not st.session_state.mostrar_pasos_matriz
            )

        if st.session_state.mostrar_pasos_matriz:

            st.divider()

            st.subheader(
                "Desarrollo del cálculo de la matriz de caminos"
            )

            st.write(
                "En cada paso se toma un vértice como "
                "intermediario. Si existe un camino desde "
                "un vértice hasta el intermediario y desde "
                "este hasta otro vértice, se registra el "
                "camino correspondiente con un 1."
            )

            for paso in resultado["pasos"]:

                st.markdown(
                    f"### Paso {paso['numero']}: "
                    f"Vértice intermediario "
                    f"{paso['vertice']}"
                )

                st.info(paso["mensaje"])

                matriz_paso = pd.DataFrame(
                    paso["matriz"],
                    index=resultado["inicial"].index,
                    columns=resultado["inicial"].columns
                )

                st.dataframe(
                    matriz_paso,
                    use_container_width=True
                )

            st.success(
                "Procedimiento terminado. "
                "La matriz obtenida es la matriz de caminos final."
            )

        # Para grafos no dirigidos se aplica el ordenamiento
        # de filas y columnas para identificar los componentes.
        if not G.is_directed():

            st.subheader("3. Conteo de unos por fila")

            tabla_conteos = pd.DataFrame({
                "Vértice": resultado["orden"],
                "Cantidad de unos": resultado["conteos"]
            })

            st.dataframe(
                tabla_conteos,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("4. Matriz de caminos ordenada")

            st.write(
                "Las filas se ordenan de mayor a menor "
                "cantidad de unos y las columnas siguen "
                "el mismo orden."
            )

            st.dataframe(
                resultado["ordenada"],
                use_container_width=True
            )

            st.caption(
                "Los bloques cuadrados de unos en la "
                "diagonal principal permiten identificar "
                "las componentes conexas."
            )

        else:
            st.info(
                "En grafos dirigidos, esta matriz representa "
                "la alcanzabilidad. Para identificar componentes "
                "fuertemente o débilmente conexas se utiliza "
                "el método correspondiente."
            )

# =====================================================
# 5. VISUALIZACIÓN DEL GRAFO
# =====================================================

elif menu == "Visualización del grafo":

    st.header("Visualización de la comunidad")

    st.caption(
        "Comparación de la red original y sus componentes identificadas."
    )

    if not G.nodes():

        st.info(
            "Primero debes registrar personas "
            "o generar una comunidad."
        )

    else:

        # ---------------------------------------------
        # OBTENER COMPONENTES
        # ---------------------------------------------

        grupos = componentes_conexas(
            d,
            modo_componentes
        )

        # ---------------------------------------------
        # POSICIONES DEL GRAFO INICIAL
        # ---------------------------------------------

        posiciones_inicial = nx.circular_layout(
              G,
              scale=2.5
        )

        # ---------------------------------------------
        # POSICIONES DEL GRAFO FINAL
        # ---------------------------------------------

        posiciones_final = posiciones_componentes(
            G,
            grupos
        )

        # ---------------------------------------------
        # COLORES PARA LAS COMPONENTES
        # ---------------------------------------------

        paleta = [
            "#F4A261",
            "#2A9D8F",
            "#8E7DBE",
            "#E76F51",
            "#457B9D",
            "#E9C46A",
            "#90BE6D",
            "#F28482",
            "#577590",
            "#B5838D",
            "#6D597A",
            "#43AA8B"
        ]

        colores = {}

        for i, grupo in enumerate(grupos):

            for persona in grupo:

                colores[persona["id"]] = (
                    paleta[i % len(paleta)]
                )

        etiquetas = nx.get_node_attributes(
            G,
            "label"
        )

        # ---------------------------------------------
        # DOS GRÁFICOS EN COLUMNAS INDEPENDIENTES
        # ---------------------------------------------

        col1, col2 = st.columns(2, gap="large")

        # =============================================
        # GRÁFICO 1: GRAFO INICIAL
        # =============================================

        with col1:

            st.subheader("1. Grafo inicial")

            fig1, ax1 = plt.subplots(
                figsize=(7, 5)
            )

            dibujar_aristas(
                G,
                posiciones_inicial,
                ax1
            )

            nx.draw_networkx_nodes(
                G,
                posiciones_inicial,
                ax=ax1,
                node_color="#BFD7EA",
                node_size=1500,
                edgecolors="#527A9B",
                linewidths=1.5
            )

            nx.draw_networkx_labels(
                G,
                posiciones_inicial,
                labels=etiquetas,
                ax=ax1,
                font_size=10,
                font_weight="bold"
            )

            ax1.set_aspect("equal")
            ax1.margins(0.35)
            ax1.axis("off")

            fig1.tight_layout()

            st.pyplot(
                fig1,
                use_container_width=True
            )

            plt.close(fig1)

        # =============================================
        # GRÁFICO 2: COMPONENTES IDENTIFICADAS
        # =============================================

        with col2:

            st.subheader(
                "2. Componentes identificadas"
            )

            fig2, ax2 = plt.subplots(
                figsize=(7, 5)
            )

            dibujar_aristas(
                G,
                posiciones_final,
                ax2
            )

            nx.draw_networkx_nodes(
                G,
                posiciones_final,
                ax=ax2,
                node_color=[
                    colores[nodo]
                    for nodo in G.nodes()
                ],
                node_size=1500,
                edgecolors="#555555",
                linewidths=1.5
            )

            nx.draw_networkx_labels(
                G,
                posiciones_final,
                labels=etiquetas,
                ax=ax2,
                font_size=10,
                font_weight="bold"
            )

            ax2.set_aspect("equal")
            ax2.margins(0.35)
            ax2.axis("off")

            fig2.tight_layout()

            st.pyplot(
                fig2,
                use_container_width=True
            )

            plt.close(fig2)

        # ---------------------------------------------
        # RESULTADOS
        # ---------------------------------------------

        st.divider()

        st.subheader(
            "Resultados de las componentes"
        )

        st.metric(
            "Cantidad de componentes encontradas",
            len(grupos)
        )

        for i, grupo in enumerate(grupos, 1):

            nombres = [
                p["nombre"]
                for p in grupo
            ]

            st.write(
                f"**Componente {i}:** "
                f"{', '.join(nombres)}"
            )


# =====================================================
# 6. COMPONENTES CONEXAS
# =====================================================

elif menu == "Componentes conexas":

    st.header("Identificación de componentes")

    if tipo_grafo == "No dirigido":

        st.caption(
            "Identificación de componentes conexas."
        )

    elif modo_componentes == "Fuertemente conexas":

        st.caption(
            "Identificación de componentes fuertemente conexas."
        )

    else:

        st.caption(
            "Identificación de componentes débilmente conexas."
        )

    grupos = componentes_conexas(
        d,
        modo_componentes
    )

    st.metric(
        "Componentes encontradas",
        len(grupos)
    )

    for i, grupo in enumerate(grupos, 1):

        nombres = [
            p["nombre"]
            for p in grupo
        ]

        st.success(
            f"Componente {i}: "
            f"{', '.join(nombres)}"
        )

    st.divider()

    st.subheader("Recorrido DFS paso a paso")

    if d["personas"]:

        ids = {
            p["id"]: p["nombre"]
            for p in d["personas"]
        }

        inicio = st.selectbox(
            "Vértice inicial",
            list(ids),
            format_func=lambda x: ids[x]
        )

        pasos = recorrido_dfs(
            d,
            inicio
        )

        clave = (
            tuple(
                (p["id"], p["nombre"])
                for p in d["personas"]
            ),
            tuple(
                (r["origen"], r["destino"])
                for r in d["relaciones"]
            ),
            inicio,
            tipo_grafo
        )

        if st.session_state.get("clave_dfs") != clave:

            st.session_state.step = 0
            st.session_state.clave_dfs = clave

        if not pasos:

            st.info(
                "No hay pasos disponibles para el recorrido."
            )

        else:

            st.session_state.step = min(
                st.session_state.get("step", 0),
                len(pasos) - 1
            )

            c1, c2 = st.columns(2)

            if c1.button("Reiniciar recorrido"):

                st.session_state.step = 0

            if c2.button("Siguiente paso"):

                st.session_state.step = min(
                    st.session_state.step + 1,
                    len(pasos) - 1
                )

            paso = pasos[
                st.session_state.step
            ]

            st.info(
                paso["mensaje"]
            )

            st.write(
                "Orden visitado: "
                + " → ".join(paso["visitados"])
            )

            st.caption(
                f"Paso {st.session_state.step + 1} "
                f"de {len(pasos)}"
            )

    else:

        st.info(
            "Agrega personas para realizar el recorrido."
        )


# =====================================================
# PIE DE PÁGINA
# =====================================================

st.divider()

st.caption(
    "NETONCIO | Análisis de grafos y componentes conexas"
)
