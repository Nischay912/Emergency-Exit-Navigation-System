"""
main.py
Entry point — orchestrates all modules, runs auto-refresh loop every 5 seconds.

AI-Based Dynamic Emergency Exit Recommendation System
20% Implementation Demo — Software Simulation
Uses Dijkstra's Algorithm with simulated crowd density weights
"""

import tkinter as tk

from floor_map        import build_weighted_graph, crowd_levels
from dijkstra         import dijkstra, reconstruct_path, best_exit
from crowd_simulator  import CrowdSimulator
from ui_map           import UIMapMixin
from dashboard        import DashboardMixin


# ─────────────────────────────────────────────
# MAIN GUI APPLICATION
# Inherits canvas drawing from UIMapMixin
# Inherits controls/header from DashboardMixin
# ─────────────────────────────────────────────

class ExitRecommenderApp(UIMapMixin, DashboardMixin):
    def __init__(self, root):
        self.root = root
        root.title("AI Emergency Exit Recommender — 20% Demo")
        root.configure(bg="#1A1A2E")
        root.geometry("900x680")
        root.resizable(False, False)

        self.simulator = CrowdSimulator()
        self.auto_sim  = tk.BooleanVar(value=False)  # Auto-simulate toggle
        self._sim_job  = None                         # Holds .after() job id

        self._build_header()
        self._build_canvas()
        self._build_controls()
        self._build_info_bar()

        self.recompute()  # Draw initial state

    # ── EVENT HANDLERS ───────────────────────

    def _on_crowd_change(self, node):
        """Called when user manually picks a crowd level."""
        crowd_levels[node] = self.crowd_vars[node].get()
        self.recompute()

    def _toggle_auto_sim(self):
        """Start or stop the auto-simulation."""
        self.auto_sim.set(not self.auto_sim.get())
        if self.auto_sim.get():
            self.sim_btn.config(text="⏹  Stop Auto-Simulate", bg="#C53030")
            self._run_simulation()
        else:
            self.sim_btn.config(text="🎲  Start Auto-Simulate", bg="#805AD5")
            if self._sim_job:
                self.root.after_cancel(self._sim_job)

    def _run_simulation(self):
        """Randomise crowds, recompute, then schedule itself again."""
        if not self.auto_sim.get():
            return
        self.simulator.randomise()
        # Sync combo boxes with new crowd values
        for node, var in self.crowd_vars.items():
            var.set(crowd_levels[node])
        self.recompute()
        self._sim_job = self.root.after(3000, self._run_simulation)  # every 3 s

    # ── CORE LOGIC ───────────────────────────

    def recompute(self):
        """Rebuild graph, run Dijkstra, redraw map."""
        graph               = build_weighted_graph()
        dist, prev          = dijkstra("You", graph)
        recommended, cost   = best_exit(dist)
        path                = reconstruct_path(prev, "You", recommended) if recommended else []

        self._draw_map(path, recommended, dist)

        if recommended:
            crowd    = crowd_levels.get(recommended, "—")
            path_str = " → ".join(path)
            self.info_label.config(
                text=f"✅  Best Exit: {recommended.replace('_', ' ')}   |   "
                     f"Crowd: {crowd}   |   "
                     f"Weighted Cost: {cost:.1f}m   |   "
                     f"Path: {path_str}",
                fg="#68D391"
            )
        else:
            self.info_label.config(
                text="⚠️  No reachable exit found!", fg="#FC8181"
            )


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = ExitRecommenderApp(root)
    root.mainloop()
