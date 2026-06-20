import os
import sys
import sumolib
import networkx as nx
import matplotlib.pyplot as plt


net = sumolib.net.readNet('2026-06-20-18-50-41/osm.net.xml.gz')
print("No da problemas")

grafo_semaforos = nx.DiGraph()

print(net.getNodes())


for n in net.getNodes():
    if n.getType() == 'traffic_light':
        id_nodo = n.getID()