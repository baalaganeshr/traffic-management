"""
NEAT Adapter - Enhanced integration with PRIT's pygame simulation
Combines neural evolution with realistic vehicle physics
"""
from __future__ import annotations

import os
import sys
from typing import Dict, Any, Optional, List
import numpy as np

# Set headless mode before importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

try:
    from ..sim_api import SimulationEngine
except ImportError:
    # Fallback base class
    class SimulationEngine:
        def get_metrics(self):
            return {}

try:
    import pygame
    import random
    import math
    NEAT_AVAILABLE = True
    
    # Initialize pygame in headless mode
    pygame.init()
    
except ImportError:
    NEAT_AVAILABLE = False
    pygame = None

# Mock NEAT if not available
try:
    import neat
except ImportError:
    class MockConfig:
        def __init__(self, filename): pass
    class MockPopulation:
        def __init__(self, config): pass
        def run(self, eval_genomes, generations): return None
    neat = type('neat', (), {
        'Config': MockConfig,
        'Population': MockPopulation,
        'DefaultGenome': object,
        'DefaultReproduction': object,
        'DefaultSpeciesSet': object,
        'DefaultStagnation': object
    })()


class EnhancedNeatAdapter(SimulationEngine):
    """Enhanced NEAT-based traffic simulation with PRIT integration"""
    
    def __init__(self, config_path: str = None):
        if not NEAT_AVAILABLE:
            raise ImportError("NEAT dependencies not available. Install with: pip install pygame neat-python")
            
        # Vehicle types from PRIT simulation
        self.vehicle_types = ['car', 'bike', 'bus', 'truck', 'rickshaw']
        self.vehicle_speeds = {'car': 2.25, 'bike': 2.5, 'bus': 1.8, 'truck': 1.8, 'rickshaw': 2}
        
        # Intersection configuration (4-way)
        self.directions = ['right', 'down', 'left', 'up']  # PRIT format
        self.approaches = ["North", "East", "South", "West"]  # UrbanFlow360 format
        self.phases = {0: ["North", "South"], 1: ["East", "West"]}
        
        # Direction mapping (PRIT → UrbanFlow360)
        self.dir_mapping = {'up': 'North', 'right': 'East', 'down': 'South', 'left': 'West'}
        
        # Traffic state
        self.reset()
        
        # NEAT network (will be loaded if available)
        self.neat_net = None
        self.neat_config = config_path
        
        # Performance tracking for gamification
        self.performance_history = []
        
    def reset(self) -> Dict[str, Any]:
        """Reset simulation with PRIT-style vehicle generation"""
        
        # Initialize traffic state
        self.state = {}
        for approach in self.approaches:
            self.state[approach] = {
                "q": 0,                    # Queue length
                "last_arrival": 0.0,       # Seconds since last arrival
                "max_wait": 0.0,          # Maximum wait time
                "total_arrivals": 0,       # Cumulative arrivals
                "total_served": 0,         # Cumulative served
                "vehicle_types": {'car': 0, 'bike': 0, 'bus': 0, 'truck': 0, 'rickshaw': 0}
            }
        
        # Signal state
        self.simulation_time = 0
        self.current_phase = 0
        self.time_in_phase = 0.0
        self.transition_timer = 0
        
        # PRIT-style traffic generation parameters
        self.arrival_distributions = {
            'North': [400, 800, 900, 1000],   # Based on PRIT's probability distribution
            'East': [300, 700, 850, 1000],
            'South': [450, 750, 900, 1000],
            'West': [350, 650, 800, 1000]
        }
        
        # Vehicle generation timing (PRIT uses 0.25s intervals)
        self.last_generation_time = 0
        self.generation_interval = 0.25
        
        return self._get_snapshot()
    
    def _generate_prit_style_vehicles(self):
        """Generate vehicles using PRIT's algorithm"""
        
        if self.simulation_time - self.last_generation_time >= self.generation_interval:
            # PRIT's vehicle generation logic
            vehicle_type = random.randint(0, 4)  # 0-4 for different vehicle types
            vehicle_class = self.vehicle_types[vehicle_type]
            
            # Lane selection (PRIT logic)
            if vehicle_type == 4:  # rickshaw
                lane_number = 0
            else:
                lane_number = random.randint(0, 1) + 1
            
            # Direction selection based on PRIT distribution
            temp = random.randint(0, 999)
            direction_number = 0
            
            # Use dynamic distribution based on current traffic
            for approach in self.approaches:
                distribution = self.arrival_distributions[approach]
                if temp < distribution[0]:
                    direction_number = 0
                    target_approach = approach
                    break
                elif temp < distribution[1]:
                    direction_number = 1
                    target_approach = approach
                    break
                elif temp < distribution[2]:
                    direction_number = 2
                    target_approach = approach
                    break
                elif temp < distribution[3]:
                    direction_number = 3
                    target_approach = approach
                    break
            else:
                # Default to North if no match
                target_approach = 'North'
            
            # Add vehicle to queue
            self.state[target_approach]["q"] += 1
            self.state[target_approach]["total_arrivals"] += 1
            self.state[target_approach]["vehicle_types"][vehicle_class] += 1
            self.state[target_approach]["last_arrival"] = 0.0
            
            self.last_generation_time = self.simulation_time
    
    def _get_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot with NEAT observations"""
        return {
            "time": self.simulation_time,
            "cur_phase": self.current_phase,
            "t_in_phase": self.time_in_phase,
            "phases": self.phases,
            "approaches": self.state.copy(),
            "in_transition": self.transition_timer > 0,
            "neat_observation": self._get_neat_observation()
        }
    
    def _get_neat_observation(self) -> List[float]:
        """Generate NEAT network observation vector"""
        observation = []
        
        # Queue lengths (4 approaches)
        for approach in self.approaches:
            observation.append(self.state[approach]["q"])
        
        # Wait times (4 approaches)
        for approach in self.approaches:
            observation.append(self.state[approach]["max_wait"])
        
        # Current phase and time in phase
        observation.append(self.current_phase)
        observation.append(self.time_in_phase)
        
        # Vehicle type distribution (weighted by priority)
        for approach in self.approaches:
            vehicle_priority = (
                self.state[approach]["vehicle_types"]["bus"] * 2.0 +    # Buses have priority
                self.state[approach]["vehicle_types"]["truck"] * 1.5 +  # Trucks medium priority
                self.state[approach]["vehicle_types"]["car"] * 1.0 +
                self.state[approach]["vehicle_types"]["bike"] * 0.8 +
                self.state[approach]["vehicle_types"]["rickshaw"] * 0.9
            )
            observation.append(vehicle_priority)
        
        return observation
    
    def step(self, action: Optional[Any] = None) -> Dict[str, Any]:
        """Advance simulation with NEAT-based decision making"""
        
        self.simulation_time += 1
        
        # Generate new vehicles (PRIT style)
        self._generate_prit_style_vehicles()
        
        # NEAT decision making
        if self.neat_net and action is None:
            observation = self._get_neat_observation()
            output = self.neat_net.activate(observation)
            
            # Interpret NEAT output (0 = hold, 1 = switch)
            should_switch = output[0] > 0.5
            if should_switch and self.transition_timer == 0:
                self._switch_phase()
        elif action == "SWITCH" and self.transition_timer == 0:
            self._switch_phase()
        
        # Handle signal transitions
        served = {approach: 0 for approach in self.approaches}
        
        if self.transition_timer > 0:
            self.transition_timer -= 1
            if self.transition_timer == 0:
                self.time_in_phase = 0.0
        else:
            self.time_in_phase += 1
            
            # Serve vehicles (PRIT-style realistic serving)
            active_approaches = self.phases[self.current_phase]
            
            for approach in active_approaches:
                if self.state[approach]["q"] > 0:
                    # Realistic serving rate based on vehicle mix
                    base_rate = 2.0  # vehicles per second
                    
                    # Adjust rate based on vehicle types (buses are slower)
                    total_vehicles = sum(self.state[approach]["vehicle_types"].values())
                    if total_vehicles > 0:
                        bus_ratio = self.state[approach]["vehicle_types"]["bus"] / total_vehicles
                        truck_ratio = self.state[approach]["vehicle_types"]["truck"] / total_vehicles
                        serving_rate = base_rate * (1.0 - 0.3 * bus_ratio - 0.2 * truck_ratio)
                    else:
                        serving_rate = base_rate
                    
                    served_count = min(self.state[approach]["q"], max(1, int(serving_rate)))
                    self.state[approach]["q"] -= served_count
                    served[approach] = served_count
                    self.state[approach]["total_served"] += served_count
                    
                    # Update vehicle type counts proportionally
                    if served_count > 0:
                        for vtype in self.vehicle_types:
                            if self.state[approach]["vehicle_types"][vtype] > 0:
                                served_of_type = min(
                                    self.state[approach]["vehicle_types"][vtype],
                                    max(1, int(served_count * 
                                              self.state[approach]["vehicle_types"][vtype] / 
                                              sum(self.state[approach]["vehicle_types"].values())))
                                )
                                self.state[approach]["vehicle_types"][vtype] -= served_of_type
        
        # Update wait times and arrival tracking
        for approach in self.approaches:
            self.state[approach]["last_arrival"] += 1
            
            if self.state[approach]["q"] > 0:
                self.state[approach]["max_wait"] += 1
            else:
                self.state[approach]["max_wait"] = 0.0
        
        snapshot = self._get_snapshot()
        snapshot["served"] = served
        
        return snapshot
    
    def _switch_phase(self):
        """Switch traffic signal phase with realistic transition timing"""
        if self.transition_timer == 0:
            self.transition_timer = 4  # 3s yellow + 1s all-red (PRIT standard)
            self.current_phase = 1 - self.current_phase
    
    def metrics(self) -> Dict[str, float]:
        """Calculate performance metrics with PRIT-style scoring"""
        
        total_queue = sum(self.state[a]["q"] for a in self.approaches)
        total_wait = sum(self.state[a]["max_wait"] * self.state[a]["q"] 
                        for a in self.approaches)
        vehicles_waiting = sum(self.state[a]["q"] for a in self.approaches)
        
        avg_wait = total_wait / max(1, vehicles_waiting)
        total_served = sum(self.state[a]["total_served"] for a in self.approaches)
        
        if self.simulation_time > 0:
            throughput = (total_served / self.simulation_time) * 3600
        else:
            throughput = 0.0
        
        # PRIT-style efficiency calculation
        total_arrivals = sum(self.state[a]["total_arrivals"] for a in self.approaches)
        efficiency = (total_served / max(1, total_arrivals)) * 100
        
        # Vehicle type efficiency (buses and trucks get priority scoring)
        priority_served = 0
        for approach in self.approaches:
            priority_served += (
                self.state[approach]["total_served"] * 1.0 +  # Base score
                self.state[approach]["vehicle_types"]["bus"] * 1.5 +      # Bus bonus
                self.state[approach]["vehicle_types"]["truck"] * 1.2      # Truck bonus
            )
        
        return {
            "avg_wait": avg_wait,
            "throughput": throughput,
            "total_queue": total_queue,
            "efficiency": efficiency,
            "priority_score": priority_served,
            "vehicles_served": total_served,
            "simulation_time": self.simulation_time,
            "neat_fitness": self._calculate_neat_fitness()
        }
    
    def _calculate_neat_fitness(self) -> float:
        """Calculate NEAT fitness score (higher is better)"""
        metrics = self.metrics()
        
        # PRIT-inspired fitness function
        fitness = (
            metrics["throughput"] * 0.4 +           # Reward high throughput
            (100 - metrics["avg_wait"]) * 0.3 +     # Penalize long waits
            metrics["efficiency"] * 0.2 +           # Reward efficiency
            (100 - metrics["total_queue"]) * 0.1    # Penalize long queues
        )
        
        return max(0, fitness)
    
    def load_neat_network(self, network):
        """Load trained NEAT network for AI control"""
        self.neat_net = network
    
    def render_snapshot(self) -> Optional[np.ndarray]:
        """Generate visualization compatible with PRIT's pygame rendering"""
        # This would integrate PRIT's visualization in headless mode
        # For now, return traffic density heatmap
        
        try:
            # Create simple traffic density visualization
            density_map = np.zeros((400, 400, 3), dtype=np.uint8)
            
            # Draw intersection
            center_x, center_y = 200, 200
            
            # Draw approaches with queue-based coloring
            approaches_positions = {
                'North': (center_x, center_y - 100),
                'East': (center_x + 100, center_y),
                'South': (center_x, center_y + 100),
                'West': (center_x - 100, center_y)
            }
            
            for approach, (x, y) in approaches_positions.items():
                queue_size = self.state[approach]["q"]
                # Color intensity based on queue size (red = congested)
                intensity = min(255, queue_size * 25)
                color = (intensity, 255 - intensity, 0)
                
                # Draw queue visualization
                for i in range(min(queue_size, 10)):
                    if approach == 'North':
                        density_map[y - i*5:y - i*5 + 3, x-5:x+5] = color
                    elif approach == 'South':
                        density_map[y + i*5:y + i*5 + 3, x-5:x+5] = color
                    elif approach == 'East':
                        density_map[y-5:y+5, x + i*5:x + i*5 + 3] = color
                    elif approach == 'West':
                        density_map[y-5:y+5, x - i*5:x - i*5 + 3] = color
            
            # Draw current active phase (green)
            active_approaches = self.phases[self.current_phase]
            for approach in active_approaches:
                x, y = approaches_positions[approach]
                density_map[y-2:y+2, x-2:x+2] = (0, 255, 0)  # Green for active
            
            return density_map
            
        except Exception:
            return None


# Alias for backward compatibility
NeatAdapter = EnhancedNeatAdapter

# Optional pygame support for visualization
try:
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    _HAVE_PYGAME = True
except Exception:
    _HAVE_PYGAME = False

try:
    # When executed as a package
    from urbanflow360.backend.sim_api import SimulationEngine  # type: ignore
except Exception:  # pragma: no cover - fallback for direct runs
    from ..sim_api import SimulationEngine  # type: ignore


class NeatAdapter(SimulationEngine):
    """Minimal NEAT-like engine implementing SimulationEngine.

    Behavior: similar to the toy model but with slightly different service rates
    to simulate a distinct policy. This makes the NEAT tab usable now and keeps
    a stable API for later true integration.
    """

    approaches: List[str] = ["North", "East", "South", "West"]

    def __init__(self, seed: int = 123) -> None:
        if _HAVE_PYGAME:
            try:
                pygame.init()
            except Exception:
                pass
        self.phases: Dict[int, List[str]] = {0: ["North", "South"], 1: ["East", "West"]}
        self.cur_phase = 0
        self.t_in_phase = 0.0
        self.time = 0
        self.yellow = 3
        self.all_red = 1
        self.transition = 0
        # fixed arrivals slightly higher on EW to differentiate behavior
        import numpy as _np

        _np.random.seed(seed)
        self.lam: Dict[str, float] = {
            "North": 0.30,
            "South": 0.30,
            "East": 0.40,
            "West": 0.40,
        }
        self._served_hist: List[int] = []
        self._wait_hist: List[float] = []
        self._reset_state()

    def _reset_state(self) -> None:
        self.state: Dict[str, Dict[str, float]] = {
            a: {"q": 0.0, "last_arrival": 0.0, "max_wait": 0.0} for a in self.approaches
        }

    def reset(self) -> Dict[str, Any]:
        self.cur_phase = 0
        self.t_in_phase = 0.0
        self.time = 0
        self.transition = 0
        self._served_hist.clear()
        self._wait_hist.clear()
        self._reset_state()
        return self._snapshot()

    def _snapshot(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "cur_phase": self.cur_phase,
            "t_in_phase": float(self.t_in_phase),
            "phases": self.phases,
            "approaches": self.state,
        }

    def step(self, action: Optional[str | int] = None) -> Dict[str, Any]:
        dt = 1
        self.time += dt
        import numpy as _np

        # stochastic arrivals, with a bit of burstiness
        for a, lam in self.lam.items():
            arrivals = int(_np.random.poisson(lam * (1.2 if _np.random.rand() < 0.2 else 1.0)))
            self.state[a]["q"] += arrivals
            self.state[a]["last_arrival"] = 0.0 if arrivals > 0 else self.state[a]["last_arrival"] + dt
            self.state[a]["max_wait"] = self.state[a]["max_wait"] + dt if self.state[a]["q"] > 0 else 0.0

        served = {a: 0 for a in self.approaches}
        if self.transition == 0:
            # slightly higher service vs toy
            rate = 3
            for a in self.phases[self.cur_phase]:
                s = min(int(self.state[a]["q"]), rate)
                self.state[a]["q"] -= s
                served[a] = s
                if self.state[a]["q"] <= 0:
                    self.state[a]["q"] = 0
                    self.state[a]["max_wait"] = 0.0
            self.t_in_phase += dt
        else:
            self.transition -= dt
            if self.transition <= 0:
                self.t_in_phase = 0

        self._served_hist.append(int(sum(served.values())))
        avg_wait_proxy = float(sum(v["max_wait"] for v in self.state.values())) / max(
            1, int(sum(v["q"] for v in self.state.values()))
        )
        self._wait_hist.append(avg_wait_proxy)
        return self._snapshot() | {"served": served}

    def switch_phase(self) -> Dict[str, Any]:
        self.transition = self.yellow + self.all_red
        self.cur_phase = 1 - self.cur_phase
        return self._snapshot()

    def metrics(self) -> Dict[str, Any]:
        total_queue = int(sum(int(v["q"]) for v in self.state.values()))
        avg_wait = float(sum(self._wait_hist) / max(1, len(self._wait_hist)))
        veh_per_sec = float(sum(self._served_hist) / max(1, len(self._served_hist)))
        throughput = int(veh_per_sec * 3600)
        return {
            "avg_wait": avg_wait,
            "throughput": throughput,
            "total_queue": total_queue,
        }

    def render_snapshot(self):  # optional
        return None
