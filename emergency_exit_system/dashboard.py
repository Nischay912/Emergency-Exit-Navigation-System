"""
dashboard.py
Header, Crowd Control Panel, and Info Bar — updates in real-time.
"""

import tkinter as tk
from tkinter import ttk
from floor_map import EXIT_NODES, crowd_levels


# ─────────────────────────────────────────────
# DASHBOARD MIXIN
# Provides header, control panel, info bar
# ─────────────────────────────────────────────

class DashboardMixin:
    """Mixin: header, control panel with crowd dropdowns, and info bar."""

    # ── HEADER ───────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg="#16213E", pady=8)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="🚨 AI-Based Dynamic Emergency Exit Recommendation System",
            bg="#16213E", fg="#E94560",
            font=("Arial Black", 13, "bold")
        ).pack()
        tk.Label(
            hdr, text="20-30% Implementation Demo  |  Dijkstra's Algorithm + Simulated Crowd Data",
            bg="#16213E", fg="#A0AEC0", font=("Arial", 9)
        ).pack()

    # ── CONTROL PANEL ────────────────────────

    def _build_controls(self):
        panel = tk.Frame(self.root, bg="#16213E", width=230)
        panel.pack(side="right", fill="y", padx=(0, 12), pady=10)
        panel.pack_propagate(False)

        # Title
        tk.Label(
            panel, text="Crowd Control Panel",
            bg="#16213E", fg="#E2E8F0",
            font=("Arial", 11, "bold")
        ).pack(pady=(10, 2))
        tk.Label(
            panel, text="(Simulates camera readings)",
            bg="#16213E", fg="#718096", font=("Arial", 8)
        ).pack(pady=(0, 8))

        # Divider
        tk.Frame(panel, bg="#E94560", height=2).pack(fill="x", padx=10, pady=4)

        # One dropdown per exit/staircase
        self.crowd_vars = {}
        for node in sorted(EXIT_NODES):
            frame = tk.Frame(panel, bg="#16213E")
            frame.pack(fill="x", padx=10, pady=4)

            label_text = node.replace("_", " ")
            tk.Label(
                frame, text=label_text,
                bg="#16213E", fg="#CBD5E0",
                font=("Arial", 9, "bold"), width=14, anchor="w"
            ).pack(side="left")

            var = tk.StringVar(value=crowd_levels[node])
            self.crowd_vars[node] = var
            combo = ttk.Combobox(
                frame, textvariable=var,
                values=["Low", "Medium", "High"],
                state="readonly", width=9
            )
            combo.pack(side="right")
            combo.bind("<<ComboboxSelected>>",
                       lambda e, n=node: self._on_crowd_change(n))

        tk.Frame(panel, bg="#E94560", height=2).pack(fill="x", padx=10, pady=8)

        # Manual recompute button
        tk.Button(
            panel, text="▶  Recompute Path",
            command=self.recompute,
            bg="#E94560", fg="white",
            font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", pady=6
        ).pack(fill="x", padx=10, pady=4)

        # Auto-simulate toggle
        self.sim_btn = tk.Button(
            panel, text="🎲  Start Auto-Simulate",
            command=self._toggle_auto_sim,
            bg="#805AD5", fg="white",
            font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", pady=6
        )
        self.sim_btn.pack(fill="x", padx=10, pady=4)

        # Legend — use real coloured Canvas dots (emoji colours don't render on Windows)
        tk.Frame(panel, bg="#2D3748", height=2).pack(fill="x", padx=10, pady=8)
        tk.Label(
            panel, text="Legend",
            bg="#16213E", fg="#E2E8F0", font=("Arial", 9, "bold")
        ).pack(pady=(0, 4))
        legend_items = [
            ("You (Start)",     "#E74C3C"),
            ("Exit",            "#27AE60"),
            ("Staircase",       "#8E44AD"),
            ("Room / Corridor", "#2980B9"),
            ("Best Exit",       "#F1C40F"),
            ("Safest Path",     "#F39C12"),
        ]
        for label, color in legend_items:
            row = tk.Frame(panel, bg="#16213E")
            row.pack(fill="x", padx=14, pady=2)
            # Coloured circle dot
            dot = tk.Canvas(row, width=14, height=14, bg="#16213E",
                            highlightthickness=0)
            dot.pack(side="left", padx=(0, 6))
            dot.create_oval(2, 2, 12, 12, fill=color, outline="")
            tk.Label(
                row, text=label,
                bg="#16213E", fg="#A0AEC0",
                font=("Arial", 8), anchor="w"
            ).pack(side="left")

    # ── INFO BAR (bottom) ────────────────────

    def _build_info_bar(self):
        self.info_label = tk.Label(
            self.root,
            text="",
            bg="#16213E", fg="#68D391",
            font=("Arial", 11, "bold"),
            pady=6
        )
        self.info_label.pack(fill="x", side="bottom")
