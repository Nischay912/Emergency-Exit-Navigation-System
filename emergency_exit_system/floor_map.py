"""
floor_map.py
Loads floor_graph.json, builds adjacency list with crowd-weighted edges.
"""

import json
import os

# ─────────────────────────────────────────────
# Load graph data from JSON
# ─────────────────────────────────────────────

_data_path = os.path.join(os.path.dirname(__file__), "data", "floor_graph.json")
with open(_data_path) as _f:
    _graph_data = json.load(_f)

NODES = {k: tuple(v) for k, v in _graph_data["nodes"].items()}
EDGES = [tuple(e) for e in _graph_data["edges"]]

# Exit / staircase nodes that receive crowd penalties
EXIT_NODES = {"Exit_North", "Exit_East", "Exit_South", "Staircase"}

# Map crowd label → weight multiplier applied to that edge
CROWD_MULTIPLIER = {"Low": 1.0, "Medium": 2.2, "High": 5.0}

# Initial crowd densities (start as Low everywhere)
crowd_levels = {n: "Low" for n in EXIT_NODES}

# Colours used in the canvas
COLORS = {
    "user"       : "#E74C3C",
    "corridor"   : "#BDC3C7",
    "room"       : "#2980B9",
    "exit"       : "#27AE60",
    "staircase"  : "#8E44AD",
    "path_edge"  : "#F39C12",
    "normal_edge": "#95A5A6",
    "best_exit"  : "#F1C40F",
    "crowd_low"  : "#27AE60",
    "crowd_med"  : "#E67E22",
    "crowd_high" : "#E74C3C",
}


# ─────────────────────────────────────────────
# GRAPH BUILDER — creates adjacency list
# applying crowd penalty to edges leading INTO
# an exit / staircase node
# ─────────────────────────────────────────────

def build_weighted_graph():
    """Return adjacency list: {node: [(neighbour, weight), ...]}"""
    graph = {n: [] for n in NODES}
    for u, v, base_dist in EDGES:
        w_uv = base_dist * CROWD_MULTIPLIER.get(crowd_levels.get(v, "Low"), 1.0)
        w_vu = base_dist * CROWD_MULTIPLIER.get(crowd_levels.get(u, "Low"), 1.0)
        graph[u].append((v, w_uv))
        graph[v].append((u, w_vu))
    return graph
