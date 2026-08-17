"""
ui_map.py
Draws the floor map on a tkinter Canvas — shows location dot + highlighted path.
"""

import tkinter as tk
from floor_map import NODES, EDGES, EXIT_NODES, COLORS, crowd_levels


# ─────────────────────────────────────────────
# UI MAP MIXIN
# Provides canvas creation and map drawing
# ─────────────────────────────────────────────

class UIMapMixin:
    """Mixin: canvas widget + floor-map drawing logic."""

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=640, height=460,
            bg="#0F3460", highlightthickness=0
        )
        self.canvas.pack(side="left", padx=(12, 6), pady=10)

    def _draw_map(self, safe_path, best, dist):
        """Redraw the entire floor-map canvas."""
        self.canvas.delete("all")

        # Build set of edges in the safe path for quick lookup
        path_edges = set()
        for i in range(len(safe_path) - 1):
            path_edges.add((safe_path[i], safe_path[i + 1]))
            path_edges.add((safe_path[i + 1], safe_path[i]))  # undirected

        # ── Draw edges ──
        for u, v, base_dist in EDGES:
            x1, y1 = NODES[u][:2]
            x2, y2 = NODES[v][:2]
            on_path = (u, v) in path_edges
            color   = COLORS["path_edge"] if on_path else COLORS["normal_edge"]
            width   = 5 if on_path else 2
            dash    = () if on_path else (4, 4)
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=width, dash=dash
            )
            # Distance label on edge mid-point
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_text(
                mx, my - 8,
                text=f"{base_dist}m",
                fill="#CBD5E0" if not on_path else "#FBD38D",
                font=("Arial", 7)
            )

        # ── Draw nodes ──
        r = 18  # node radius
        for name, (x, y, ntype) in NODES.items():
            is_best  = (name == best)
            is_crowd = (name in EXIT_NODES)

            # Pick fill colour
            if is_best:
                fill = COLORS["best_exit"]
            elif ntype == "user":
                fill = COLORS["user"]
            elif ntype == "exit":
                fill = COLORS["exit"]
            elif ntype == "staircase":
                fill = COLORS["staircase"]
            else:
                fill = COLORS["corridor"] if ntype == "corridor" else COLORS["room"]

            # Outer glow ring for best exit
            if is_best:
                self.canvas.create_oval(
                    x - r - 6, y - r - 6, x + r + 6, y + r + 6,
                    fill="", outline="#F1C40F", width=3
                )

            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill, outline="white", width=2
            )

            # Short display label inside node
            short = name.split("_")[-1] if "_" in name else name
            if short == "CorridorA": short = "CorrA"
            if short == "CorridorB": short = "CorrB"
            if short == "CorridorC": short = "CorrC"
            self.canvas.create_text(
                x, y, text=short,
                fill="white" if ntype != "corridor" else "#1A1A2E",
                font=("Arial", 7, "bold")
            )

            # Full name label below node
            self.canvas.create_text(
                x, y + r + 8,
                text=name.replace("_", "\n"),
                fill="#E2E8F0", font=("Arial", 7),
                justify="center"
            )

            # Crowd badge for exits/staircase
            if is_crowd:
                crowd = crowd_levels.get(name, "Low")
                badge_color = (
                    COLORS["crowd_low"]  if crowd == "Low"    else
                    COLORS["crowd_med"]  if crowd == "Medium" else
                    COLORS["crowd_high"]
                )
                self.canvas.create_rectangle(
                    x - 18, y - r - 24, x + 18, y - r - 10,
                    fill=badge_color, outline="", tags="badge"
                )
                self.canvas.create_text(
                    x, y - r - 17,
                    text=crowd, fill="white",
                    font=("Arial", 7, "bold")
                )

        # ── Arrow along the safest path (direction indicator) ──
        if len(safe_path) >= 2:
            u, v = safe_path[-2], safe_path[-1]
            x1, y1 = NODES[u][:2]
            x2, y2 = NODES[v][:2]
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=COLORS["path_edge"], width=5,
                arrow=tk.LAST, arrowshape=(10, 12, 5)
            )

        # ── Title watermark on canvas ──
        self.canvas.create_text(
            320, 14,
            text="Department Floor Map — ISE Dept (Simulated)",
            fill="#4A5568", font=("Arial", 8, "italic")
        )
