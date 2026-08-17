"""
dijkstra.py
Wraps Dijkstra's algorithm with crowd-weighted edges, returns safest path.
"""

import heapq
from floor_map import EXIT_NODES


# ─────────────────────────────────────────────
# DIJKSTRA'S ALGORITHM
# Returns (distances_dict, predecessors_dict)
# ─────────────────────────────────────────────

def dijkstra(start, graph):
    """
    Classic Dijkstra using a min-heap priority queue.
    dist[node]  = current shortest cost from 'start'
    prev[node]  = which node we came from (for path reconstruction)
    """
    dist = {n: float('inf') for n in graph}
    prev = {n: None for n in graph}
    dist[start] = 0
    heap = [(0, start)]  # (cost, node)

    while heap:
        current_cost, u = heapq.heappop(heap)

        # Skip if we already found a shorter path to u
        if current_cost > dist[u]:
            continue

        for v, weight in graph[u]:
            new_cost = dist[u] + weight
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    return dist, prev


def reconstruct_path(prev, start, target):
    """Walk backwards through 'prev' to build the path list."""
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    # Return path only if it actually reaches 'start'
    return path if path and path[0] == start else []


def best_exit(dist):
    """Return the exit with the minimum Dijkstra cost."""
    exits = [n for n in EXIT_NODES if dist[n] < float('inf')]
    if not exits:
        return None, float('inf')
    best = min(exits, key=lambda x: dist[x])
    return best, dist[best]
