"""
PRIT-UrbanFlow360 Integration Bridge
Connects PRIT's vehicle simulation with UrbanFlow360's gamified interface
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, Any, Optional, List

# Add the root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from backend.sim_engines.neat_adapter import EnhancedNeatAdapter
    from backend.prit_integration.vehicle_engine import PritSimulationCore, VehicleType, Direction
except ImportError:
    # Fallback imports for different path structures
    try:
        from sim_engines.neat_adapter import EnhancedNeatAdapter
        from vehicle_engine import PritSimulationCore, VehicleType, Direction
    except ImportError:
        # Create mock classes if imports fail
        print("⚠️ PRIT dependencies not available, using mock implementation")
        
        class EnhancedNeatAdapter:
            def __init__(self): pass
            def step(self, action): return {"neat_fitness": 50}
        
        class PritSimulationCore:
            def __init__(self): 
                self.vehicles = []
            def update(self, dt): 
                return {
                    "vehicle_queues": {"North": 0, "South": 0, "East": 0, "West": 0},
                    "performance_metrics": {"throughput": 0, "avg_wait": 0, "efficiency": 50}
                }
        
        class VehicleType:
            CAR = 0
            BIKE = 1
            BUS = 2
            TRUCK = 3 
            RICKSHAW = 4
        
        class Direction:
            UP = 0
            RIGHT = 1
            DOWN = 2
            LEFT = 3


class PritGameBridge:
    """Bridge between PRIT simulation and UrbanFlow360 gamification"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize PRIT core simulation
        self.prit_core = PritSimulationCore()
        
        # Initialize NEAT adapter for UrbanFlow360 compatibility
        self.neat_adapter = EnhancedNeatAdapter()
        
        # Game state management
        self.player_stats = {
            "xp": 0,
            "level": 1,
            "badges": [],
            "total_score": 0,
            "best_efficiency": 0.0,
            "vehicles_managed": 0
        }
        
        # Performance tracking
        self.session_metrics = []
        self.real_time_data = []
        
        # Auto-generation settings (user's requirement)
        self.auto_mode = True
        self.generation_interval = 1.0  # 1 second updates
        
        self.is_running = False
        self.start_time = time.time()
    
    def start_automatic_simulation(self, duration_minutes: int = 60):
        """Start automatic data generation simulation"""
        self.is_running = True
        self.start_time = time.time()
        
        print(f"🚀 Starting PRIT-Enhanced Auto-Simulation for {duration_minutes} minutes...")
        print("📊 Automatic Input → Output Generation Active")
        
        # Initialize with random traffic patterns
        self._initialize_traffic_patterns()
        
        return {
            "status": "started",
            "mode": "automatic",
            "duration": duration_minutes,
            "prit_integration": "active",
            "neat_ai": "enabled"
        }
    
    def get_automatic_input_output(self) -> Dict[str, Any]:
        """Generate automatic input/output data (User's exact requirement)"""
        
        if not self.is_running:
            self.start_automatic_simulation()
        
        # Update PRIT simulation
        delta_time = self.generation_interval
        prit_state = self.prit_core.update(delta_time)
        
        # Generate UrbanFlow360 compatible state
        neat_state = self.neat_adapter.step("AUTO")
        
        # Create input/output pair
        simulation_input = self._generate_simulation_inputs(prit_state)
        simulation_output = self._generate_simulation_outputs(prit_state, neat_state)
        
        # Update player stats
        self._update_player_progress(simulation_output)
        
        # Store for CSV export
        timestamp = time.time() - self.start_time
        data_point = {
            "timestamp": timestamp,
            "input": simulation_input,
            "output": simulation_output,
            "player_stats": self.player_stats.copy()
        }
        
        self.real_time_data.append(data_point)
        
        return {
            "timestamp": timestamp,
            "automatic_input": simulation_input,
            "automatic_output": simulation_output,
            "prit_vehicles": len(self.prit_core.vehicles),
            "neat_performance": neat_state.get("neat_fitness", 0),
            "player_progress": self.player_stats,
            "generation_active": True
        }
    
    def _generate_simulation_inputs(self, prit_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic simulation inputs from PRIT data"""
        
        vehicle_queues = prit_state["vehicle_queues"]
        signal_state = prit_state["signal_state"]
        
        return {
            "traffic_demand": {
                "north_bound": vehicle_queues.get("North", 0),
                "south_bound": vehicle_queues.get("South", 0),
                "east_bound": vehicle_queues.get("East", 0),
                "west_bound": vehicle_queues.get("West", 0)
            },
            "vehicle_composition": self._get_vehicle_composition(),
            "signal_timing": {
                "current_phase": signal_state["phase"],
                "time_in_phase": signal_state["time_in_phase"],
                "green_times": signal_state["green_times"]
            },
            "environmental_factors": {
                "weather": "clear",  # Could be randomized
                "time_of_day": self._get_time_of_day(),
                "traffic_density": "moderate"
            },
            "ai_parameters": {
                "neat_enabled": True,
                "learning_rate": 0.1,
                "population_size": 50
            }
        }
    
    def _generate_simulation_outputs(self, prit_state: Dict[str, Any], 
                                   neat_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive simulation outputs"""
        
        performance = prit_state["performance_metrics"]
        
        return {
            "traffic_flow_metrics": {
                "throughput": performance["throughput"],
                "average_wait_time": performance["avg_wait"],
                "queue_lengths": prit_state["vehicle_queues"],
                "efficiency_score": performance["efficiency"]
            },
            "ai_performance": {
                "neat_fitness": neat_state.get("neat_fitness", 0),
                "decision_accuracy": self._calculate_decision_accuracy(),
                "learning_progress": self._get_learning_progress()
            },
            "environmental_impact": {
                "fuel_consumption": self._calculate_fuel_usage(performance),
                "emissions_reduction": self._calculate_emissions(performance),
                "noise_level": "moderate"
            },
            "optimization_results": {
                "signal_optimization": f"{performance['efficiency']:.1f}%",
                "congestion_reduction": self._calculate_congestion_reduction(),
                "time_savings": f"{max(0, 100 - performance['avg_wait']):.1f}%"
            },
            "real_time_status": {
                "vehicles_in_system": len(self.prit_core.vehicles),
                "completed_journeys": prit_state["vehicles_completed"],
                "active_signals": 1,
                "system_health": "optimal"
            }
        }
    
    def _get_vehicle_composition(self) -> Dict[str, int]:
        """Get current vehicle type distribution"""
        composition = {vtype.name.lower(): 0 for vtype in VehicleType}
        
        for vehicle in self.prit_core.vehicles:
            composition[vehicle.type.name.lower()] += 1
        
        return composition
    
    def _get_time_of_day(self) -> str:
        """Simulate time of day based on elapsed time"""
        minutes_elapsed = (time.time() - self.start_time) / 60
        hour = (8 + int(minutes_elapsed / 10)) % 24  # Accelerated time
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon" 
        elif 17 <= hour < 20:
            return "evening"
        else:
            return "night"
    
    def _calculate_decision_accuracy(self) -> float:
        """Calculate AI decision accuracy score"""
        if not self.session_metrics:
            return 85.0
        
        recent_performance = self.session_metrics[-10:]  # Last 10 decisions
        avg_efficiency = sum(m.get("efficiency", 50) for m in recent_performance) / len(recent_performance)
        
        return min(100.0, avg_efficiency * 1.2)
    
    def _get_learning_progress(self) -> float:
        """Show NEAT learning progress"""
        if len(self.session_metrics) < 2:
            return 0.0
        
        initial_performance = self.session_metrics[0].get("efficiency", 50)
        current_performance = self.session_metrics[-1].get("efficiency", 50)
        
        improvement = ((current_performance - initial_performance) / initial_performance) * 100
        return max(0, min(100, improvement))
    
    def _calculate_fuel_usage(self, performance: Dict[str, float]) -> str:
        """Calculate fuel consumption based on traffic efficiency"""
        base_consumption = 100
        efficiency_factor = performance.get("efficiency", 50) / 100
        
        # Better efficiency = lower fuel consumption
        fuel_saved = base_consumption * (1 - efficiency_factor)
        return f"{fuel_saved:.1f}L saved"
    
    def _calculate_emissions(self, performance: Dict[str, float]) -> str:
        """Calculate emissions reduction"""
        efficiency = performance.get("efficiency", 50)
        reduction = min(45, efficiency * 0.8)  # Up to 45% reduction
        
        return f"{reduction:.1f}% reduction"
    
    def _calculate_congestion_reduction(self) -> str:
        """Calculate congestion reduction percentage"""
        if not self.prit_core.vehicles:
            return "0%"
        
        avg_wait = sum(v.wait_time for v in self.prit_core.vehicles) / len(self.prit_core.vehicles)
        reduction = max(0, 100 - avg_wait * 10)  # Simplified calculation
        
        return f"{reduction:.1f}%"
    
    def _update_player_progress(self, output_data: Dict[str, Any]):
        """Update gamification stats based on performance"""
        
        efficiency = output_data["traffic_flow_metrics"]["efficiency_score"]
        vehicles_managed = output_data["real_time_status"]["vehicles_in_system"]
        
        # XP calculation
        base_xp = 10
        efficiency_bonus = int(efficiency / 10)  # 1-10 bonus XP
        volume_bonus = min(5, vehicles_managed // 5)  # Volume bonus
        
        xp_gained = base_xp + efficiency_bonus + volume_bonus
        self.player_stats["xp"] += xp_gained
        
        # Level progression
        new_level = min(50, 1 + self.player_stats["xp"] // 100)
        if new_level > self.player_stats["level"]:
            self.player_stats["level"] = new_level
        
        # Badge system
        self._check_badge_achievements(output_data)
        
        # Records
        self.player_stats["best_efficiency"] = max(
            self.player_stats["best_efficiency"], efficiency
        )
        self.player_stats["vehicles_managed"] += vehicles_managed
        self.player_stats["total_score"] += int(efficiency * 10)
    
    def _check_badge_achievements(self, output_data: Dict[str, Any]):
        """Check and award badges based on performance"""
        
        efficiency = output_data["traffic_flow_metrics"]["efficiency_score"]
        throughput = output_data["traffic_flow_metrics"]["throughput"]
        
        badges_to_check = [
            ("efficiency_master", efficiency > 90, "Achieve 90%+ efficiency"),
            ("traffic_guru", throughput > 1800, "Handle 1800+ vehicles/hour"),
            ("ai_optimizer", output_data["ai_performance"]["neat_fitness"] > 85, "NEAT AI Score 85+"),
            ("eco_warrior", "45%" in output_data["environmental_impact"]["emissions_reduction"], "Maximum emissions reduction"),
            ("flow_master", len(self.prit_core.vehicles) > 20, "Manage 20+ concurrent vehicles")
        ]
        
        for badge_id, condition, description in badges_to_check:
            if condition and badge_id not in self.player_stats["badges"]:
                self.player_stats["badges"].append(badge_id)
    
    def _initialize_traffic_patterns(self):
        """Initialize realistic traffic patterns"""
        
        # Pre-populate with initial vehicles for immediate data generation
        for direction in Direction:
            for _ in range(3):  # 3 vehicles per direction to start
                vehicle = self.prit_core.generate_vehicle(direction)
                self.prit_core.vehicles.append(vehicle)
    
    def export_session_data(self, filename: str = None) -> str:
        """Export all generated input/output data to CSV"""
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"prit_urbanflow_session_{timestamp}.csv"
        
        import pandas as pd
        
        # Flatten data for CSV export
        export_data = []
        for point in self.real_time_data:
            flat_point = {
                "timestamp": point["timestamp"],
                "input_north_demand": point["input"]["traffic_demand"]["north_bound"],
                "input_south_demand": point["input"]["traffic_demand"]["south_bound"],
                "input_east_demand": point["input"]["traffic_demand"]["east_bound"],
                "input_west_demand": point["input"]["traffic_demand"]["west_bound"],
                "input_signal_phase": point["input"]["signal_timing"]["current_phase"],
                "input_time_in_phase": point["input"]["signal_timing"]["time_in_phase"],
                "output_throughput": point["output"]["traffic_flow_metrics"]["throughput"],
                "output_avg_wait": point["output"]["traffic_flow_metrics"]["average_wait_time"],
                "output_efficiency": point["output"]["traffic_flow_metrics"]["efficiency_score"],
                "output_neat_fitness": point["output"]["ai_performance"]["neat_fitness"],
                "output_vehicles_active": point["output"]["real_time_status"]["vehicles_in_system"],
                "player_xp": point["player_stats"]["xp"],
                "player_level": point["player_stats"]["level"],
                "player_badges": len(point["player_stats"]["badges"])
            }
            export_data.append(flat_point)
        
        df = pd.DataFrame(export_data)
        full_path = f"G:\\c\\OneDrive\\Desktop\\og\\urbanflow360\\data\\{filename}"
        df.to_csv(full_path, index=False)
        
        return full_path
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary for dashboard display"""
        
        if not self.real_time_data:
            return {"status": "No data generated yet"}
        
        latest = self.real_time_data[-1]
        
        return {
            "status": "🟢 Auto-Generation Active",
            "mode": "PRIT + NEAT Integration",
            "data_points_generated": len(self.real_time_data),
            "current_performance": {
                "efficiency": latest["output"]["traffic_flow_metrics"]["efficiency_score"],
                "throughput": latest["output"]["traffic_flow_metrics"]["throughput"],
                "ai_fitness": latest["output"]["ai_performance"]["neat_fitness"]
            },
            "player_progress": self.player_stats,
            "vehicles_simulated": self.player_stats["vehicles_managed"],
            "session_duration": f"{(time.time() - self.start_time)/60:.1f} minutes"
        }
