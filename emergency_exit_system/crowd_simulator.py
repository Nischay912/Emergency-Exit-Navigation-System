"""
crowd_simulator.py
Generates random density per exit, simulates live camera data.
"""

import random
from floor_map import EXIT_NODES, crowd_levels


# ─────────────────────────────────────────────
# CROWD SIMULATOR  — auto-randomise every 8 s
# ─────────────────────────────────────────────

class CrowdSimulator:
    """Randomly updates crowd levels to simulate camera readings."""
    levels  = ["Low", "Medium", "High"]
    weights = [0.5, 0.35, 0.15]  # Low is most common

    def randomise(self):
        for node in EXIT_NODES:
            crowd_levels[node] = random.choices(
                self.levels, weights=self.weights, k=1
            )[0]
