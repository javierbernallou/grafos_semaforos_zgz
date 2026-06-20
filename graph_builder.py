import sumolib
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque


# ============================================================
# 1. CARGA DE RED SUMO
# ============================================================

net = sumolib.net.readNet('2026-06-20-18-50-41/osm.net.xml.gz')
print("Red cargada correctamente.")

grafo_semaforos = nx.DiGraph()


# ============================================================
# 2. FUNCIÓN PARA AÑADIR NODOS (ROBUSTA)
# ============================================================
# IMPORTANTE:
# - No usamos "if exists" porque NetworkX permite overwrite seguro
# - Garantizamos siempre atributos completos
# ============================================================

def add_semaforo(node):
    node_id = node.getID()
    x, y = node.getCoord()

    grafo_semaforos.add_node(
        node_id,
        pos_x=float(x),
        pos_y=float(y),
        tipo="semaforo"
    )


# ============================================================
# 3. INICIALIZAR NODOS (SEMÁFOROS + CLUSTERS)
# ============================================================

for n in net.getNodes():
    if n.getType() == "traffic_light" or "cluster" in n.getID():
        add_semaforo(n)

print(f"Nº inicial de semáforos/clusters: {grafo_semaforos.number_of_nodes()}")


# ============================================================
# 4. EXPLORACIÓN DE CONEXIONES ENTRE SEMÁFOROS
# ============================================================
# BFS sobre calles hasta encontrar otro semáforo/cluster
# ============================================================

nodos_iniciales = list(grafo_semaforos.nodes())

for id_origen in nodos_iniciales:

    nodo_origen = net.getNode(id_origen)

    for calle in nodo_origen.getOutgoing():

        nodo_sig = calle.getToNode()
        id_sig = nodo_sig.getID()

        if nodo_sig.getType() == "traffic_light" or "cluster" in id_sig:

            add_semaforo(nodo_sig)

            grafo_semaforos.add_edge(
                id_origen,
                id_sig,
                calle=calle.getID()
            )

            continue

        por_visitar = deque(nodo_sig.getOutgoing())
        visitadas = set()

        while por_visitar:

            c = por_visitar.popleft()
            c_id = c.getID()

            if c_id in visitadas:
                continue
            visitadas.add(c_id)

            nodo_final = c.getToNode()
            id_final = nodo_final.getID()

            if nodo_final.getType() == "traffic_light" or "cluster" in id_final:

                add_semaforo(nodo_final)

                grafo_semaforos.add_edge(
                    id_origen,
                    id_final,
                    calle=calle.getID()
                )

                break

            else:
                for nxt in nodo_final.getOutgoing():
                    por_visitar.append(nxt)


print("Conexiones creadas correctamente.")


sin_coord = [
    n for n, d in grafo_semaforos.nodes(data=True)
    if "pos_x" not in d or "pos_y" not in d
]

print(f"Nodos sin coordenadas: {len(sin_coord)}")

if sin_coord:
    print("Ejemplo:", sin_coord[:10])


pos = {
    n: (d["pos_x"], d["pos_y"])
    for n, d in grafo_semaforos.nodes(data=True)
    if "pos_x" in d and "pos_y" in d
}


plt.figure(figsize=(12, 10))

nx.draw_networkx_nodes(
    grafo_semaforos,
    pos,
    node_size=20,
    node_color="red",
    alpha=0.8
)

nx.draw_networkx_edges(
    grafo_semaforos,
    pos,
    width=0.5,
    edge_color="gray",
    arrows=True,
    arrowsize=5
)

plt.title("Grafo de semáforos - Zaragoza")
plt.axis("off")

plt.savefig(
    "grafo_semaforos_zaragoza.png",
    dpi=300,
    bbox_inches="tight"
)

print("Imagen guardada correctamente.")


nx.write_graphml(
    grafo_semaforos,
    "grafo_semaforos.graphml"
)

print("GraphML exportado correctamente.")
print("Nodos:", grafo_semaforos.number_of_nodes())
print("Aristas:", grafo_semaforos.number_of_edges())