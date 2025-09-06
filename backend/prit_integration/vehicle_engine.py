"""
PRIT Vehicle Engine Integration
Realistic vehicle simulation with pygame physics integration
"""

import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class VehicleType(Enum):
    """Vehicle types with realistic properties (PRIT compatible)"""
    CAR = 0
    BIKE = 1
    BUS = 2
    TRUCK = 3
    RICKSHAW = 4

@dataclass
class VehicleProperties:
    """Physical properties of different vehicle types"""
    length: float      # meters
    width: float       # meters
    max_speed: float   # m/s
    acceleration: float # m/s²
    priority: float    # 0-1, higher = more priority
    lane_preference: int # 0=any, 1=outer, 2=inner

# PRIT vehicle configurations
VEHICLE_CONFIG = {
    VehicleType.CAR: VehicleProperties(4.5, 2.0, 13.89, 3.0, 0.5, 0),
    VehicleType.BIKE: VehicleProperties(2.0, 0.8, 16.67, 4.0, 0.3, 0),
    VehicleType.BUS: VehicleProperties(12.0, 2.5, 11.11, 1.5, 0.9, 2),
    VehicleType.TRUCK: VehicleProperties(8.0, 2.5, 11.11, 2.0, 0.7, 2),
    VehicleType.RICKSHAW: VehicleProperties(3.0, 1.5, 8.33, 2.5, 0.4, 1)
}

class Direction(Enum):
    """Traffic flow directions (PRIT format)"""
    UP = 0      # North
    RIGHT = 1   # East  
    DOWN = 2    # South
    LEFT = 3    # West

# Direction mapping for integration
DIRECTION_MAPPING = {
    Direction.UP: "North",
    Direction.RIGHT: "East", 
    Direction.DOWN: "South",
    Direction.LEFT: "West"
}

class TurnDirection(Enum):
    """Turn directions at intersection"""
    STRAIGHT = 0
    LEFT = 1
    RIGHT = 2

class Vehicle:
    """PRIT-style vehicle with realistic physics"""
    
    def __init__(self, vehicle_id: int, vehicle_type: VehicleType, 
                 spawn_direction: Direction, position: Tuple[float, float]):
        
        self.id = vehicle_id
        self.type = vehicle_type
        self.properties = VEHICLE_CONFIG[vehicle_type]
        
        # Position and movement
        self.x, self.y = position
        self.speed = 0.0
        self.target_speed = self.properties.max_speed
        self.direction = spawn_direction
        
        # Turn decision (random for now, could be NEAT-controlled)
        self.turn_direction = random.choice([TurnDirection.STRAIGHT, TurnDirection.LEFT, TurnDirection.RIGHT])
        self.turn_probabilities = [0.6, 0.2, 0.2]  # straight, left, right
        
        # State tracking
        self.wait_time = 0.0
        self.distance_traveled = 0.0
        self.stopped = False
        self.in_intersection = False
        
        # Lane assignment (PRIT logic)
        if vehicle_type == VehicleType.RICKSHAW:
            self.lane = 0  # Always outer lane
        else:
            self.lane = random.randint(0, 1) + 1
    
    def update_position(self, delta_time: float, signal_state: bool = True):
        """Update vehicle position with realistic physics"""
        
        if not signal_state and not self.in_intersection:
            # Vehicle must stop at red signal
            self.stopped = True
            self.speed = max(0, self.speed - self.properties.acceleration * delta_time)
            self.wait_time += delta_time
        else:
            self.stopped = False
            # Accelerate towards target speed
            if self.speed < self.target_speed:
                self.speed = min(self.target_speed, 
                               self.speed + self.properties.acceleration * delta_time)
        
        # Update position based on direction
        distance = self.speed * delta_time
        self.distance_traveled += distance
        
        if self.direction == Direction.UP:
            self.y -= distance
        elif self.direction == Direction.DOWN:
            self.y += distance
        elif self.direction == Direction.LEFT:
            self.x -= distance
        elif self.direction == Direction.RIGHT:
            self.x += distance
    
    def calculate_following_distance(self, front_vehicle: 'Vehicle') -> float:
        """Calculate safe following distance (PRIT car-following model)"""
        
        if not front_vehicle:
            return float('inf')
        
        # Distance between vehicles
        if self.direction in [Direction.UP, Direction.DOWN]:
            distance = abs(front_vehicle.y - self.y) - self.properties.length
        else:
            distance = abs(front_vehicle.x - self.x) - self.properties.length
        
        return max(0, distance)
    
    def adjust_speed_for_following(self, front_vehicle: Optional['Vehicle'], 
                                  min_gap: float = 2.0):
        """Adjust speed based on vehicle ahead (realistic car-following)"""
        
        if not front_vehicle:
            return
        
        following_distance = self.calculate_following_distance(front_vehicle)
        
        if following_distance < min_gap:
            # Too close - reduce speed
            self.target_speed = min(front_vehicle.speed * 0.8, self.properties.max_speed * 0.5)
        elif following_distance < min_gap * 2:
            # Moderate distance - match speed
            self.target_speed = min(front_vehicle.speed, self.properties.max_speed)
        else:
            # Safe distance - resume normal speed
            self.target_speed = self.properties.max_speed
    
    def get_prit_metrics(self) -> Dict[str, float]:
        """Get PRIT-compatible vehicle metrics"""
        return {
            "id": self.id,
            "type": self.type.value,
            "speed": self.speed,
            "wait_time": self.wait_time,
            "distance": self.distance_traveled,
            "stopped": self.stopped,
            "priority": self.properties.priority,
            "lane": self.lane,
            "x": self.x,
            "y": self.y
        }


class TrafficSignal:
    """PRIT-style traffic signal with NEAT integration"""
    
    def __init__(self, signal_id: int, position: Tuple[float, float]):
        self.id = signal_id
        self.x, self.y = position
        
        # Signal phases (PRIT 4-way intersection)
        self.phases = {
            0: [Direction.UP, Direction.DOWN],    # North-South
            1: [Direction.LEFT, Direction.RIGHT]  # East-West
        }
        
        self.current_phase = 0
        self.time_in_phase = 0.0
        self.transition_time = 3.0  # Yellow + all-red
        self.in_transition = False
        
        # NEAT-controlled timing
        self.green_times = {0: 30.0, 1: 30.0}  # Default green times
        self.min_green = 10.0
        self.max_green = 60.0
        
        # Performance tracking
        self.vehicles_served = {direction: 0 for direction in Direction}
        self.total_wait_time = 0.0
    
    def update(self, delta_time: float, neat_action: Optional[int] = None):
        """Update signal state with optional NEAT control"""
        
        self.time_in_phase += delta_time
        
        if self.in_transition:
            # Handle transition phase
            if self.time_in_phase >= self.transition_time:
                self.current_phase = 1 - self.current_phase
                self.time_in_phase = 0.0
                self.in_transition = False
        else:
            # Check for phase switch
            should_switch = False
            
            if neat_action is not None:
                # NEAT-controlled switching
                should_switch = neat_action == 1
            else:
                # Default timing-based switching
                current_green = self.green_times[self.current_phase]
                should_switch = self.time_in_phase >= current_green
            
            if should_switch and self.time_in_phase >= self.min_green:
                self.in_transition = True
                self.time_in_phase = 0.0
    
    def is_green_for_direction(self, direction: Direction) -> bool:
        """Check if signal is green for given direction"""
        if self.in_transition:
            return False
        return direction in self.phases[self.current_phase]
    
    def set_neat_green_times(self, north_south: float, east_west: float):
        """Update green times from NEAT network output"""
        self.green_times[0] = max(self.min_green, min(self.max_green, north_south))
        self.green_times[1] = max(self.min_green, min(self.max_green, east_west))
    
    def get_signal_state(self) -> Dict[str, any]:
        """Get current signal state for UrbanFlow360 integration"""
        return {
            "phase": self.current_phase,
            "time_in_phase": self.time_in_phase,
            "in_transition": self.in_transition,
            "active_directions": [DIRECTION_MAPPING[d] for d in self.phases[self.current_phase]],
            "green_times": self.green_times,
            "vehicles_served": self.vehicles_served.copy()
        }


class PritSimulationCore:
    """Core simulation engine combining PRIT vehicles with NEAT AI"""
    
    def __init__(self, intersection_size: Tuple[int, int] = (800, 600)):
        self.width, self.height = intersection_size
        self.center_x, self.center_y = self.width // 2, self.height // 2
        
        # Traffic signal at center
        self.signal = TrafficSignal(0, (self.center_x, self.center_y))
        
        # Vehicle management
        self.vehicles: List[Vehicle] = []
        self.next_vehicle_id = 1
        self.spawn_points = self._calculate_spawn_points()
        
        # Generation parameters (PRIT-style)
        self.generation_rate = 0.25  # seconds between generations
        self.last_generation = 0.0
        
        # Performance metrics
        self.total_vehicles_generated = 0
        self.total_vehicles_completed = 0
        self.total_wait_time = 0.0
        
        # NEAT integration
        self.neat_network = None
        
    def _calculate_spawn_points(self) -> Dict[Direction, Tuple[float, float]]:
        """Calculate vehicle spawn points for each direction"""
        margin = 50
        return {
            Direction.UP: (self.center_x, self.height - margin),      # South spawn for northbound
            Direction.DOWN: (self.center_x, margin),                 # North spawn for southbound  
            Direction.LEFT: (self.width - margin, self.center_y),    # East spawn for westbound
            Direction.RIGHT: (margin, self.center_y)                # West spawn for eastbound
        }
    
    def generate_vehicle(self, direction: Direction) -> Vehicle:
        """Generate new vehicle with PRIT characteristics"""
        
        # Vehicle type selection (PRIT distribution)
        type_weights = [40, 25, 10, 15, 10]  # car, bike, bus, truck, rickshaw
        vehicle_type = VehicleType(random.choices(range(5), weights=type_weights)[0])
        
        spawn_pos = self.spawn_points[direction]
        vehicle = Vehicle(self.next_vehicle_id, vehicle_type, direction, spawn_pos)
        
        self.next_vehicle_id += 1
        self.total_vehicles_generated += 1
        
        return vehicle
    
    def update(self, delta_time: float) -> Dict[str, any]:
        """Update entire simulation state"""
        
        # Vehicle generation
        self.last_generation += delta_time
        if self.last_generation >= self.generation_rate:
            # Generate vehicles based on current demand
            for direction in Direction:
                if random.random() < 0.3:  # 30% chance per direction
                    new_vehicle = self.generate_vehicle(direction)
                    self.vehicles.append(new_vehicle)
            
            self.last_generation = 0.0
        
        # NEAT signal control
        neat_action = None
        if self.neat_network:
            observation = self._get_neat_observation()
            neat_output = self.neat_network.activate(observation)
            neat_action = 1 if neat_output[0] > 0.5 else 0
        
        # Update signal
        self.signal.update(delta_time, neat_action)
        
        # Update vehicles
        vehicles_to_remove = []
        for vehicle in self.vehicles:
            # Check signal state for this vehicle's direction
            signal_green = self.signal.is_green_for_direction(vehicle.direction)
            
            # Update vehicle position
            vehicle.update_position(delta_time, signal_green)
            
            # Check if vehicle completed journey
            if self._vehicle_completed_journey(vehicle):
                vehicles_to_remove.append(vehicle)
                self.total_vehicles_completed += 1
                self.signal.vehicles_served[vehicle.direction] += 1
        
        # Remove completed vehicles
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
        
        return self._get_simulation_state()
    
    def _vehicle_completed_journey(self, vehicle: Vehicle) -> bool:
        """Check if vehicle has completed its journey"""
        margin = 100
        
        if vehicle.direction == Direction.UP and vehicle.y < -margin:
            return True
        elif vehicle.direction == Direction.DOWN and vehicle.y > self.height + margin:
            return True
        elif vehicle.direction == Direction.LEFT and vehicle.x < -margin:
            return True
        elif vehicle.direction == Direction.RIGHT and vehicle.x > self.width + margin:
            return True
        
        return False
    
    def _get_neat_observation(self) -> List[float]:
        """Generate observation vector for NEAT network"""
        observation = []
        
        # Vehicle counts by direction and type
        for direction in Direction:
            direction_vehicles = [v for v in self.vehicles if v.direction == direction]
            
            # Count by vehicle type
            type_counts = [0] * 5
            total_wait = 0.0
            
            for vehicle in direction_vehicles:
                type_counts[vehicle.type.value] += 1
                total_wait += vehicle.wait_time
            
            observation.extend(type_counts)  # 5 values per direction
            observation.append(total_wait)   # Total wait time for direction
        
        # Signal state
        observation.append(self.signal.current_phase)
        observation.append(self.signal.time_in_phase)
        observation.append(1.0 if self.signal.in_transition else 0.0)
        
        return observation
    
    def _get_simulation_state(self) -> Dict[str, any]:
        """Get complete simulation state for integration"""
        
        # Calculate queue lengths by direction
        queues = {}
        wait_times = {}
        
        for direction in Direction:
            direction_name = DIRECTION_MAPPING[direction]
            direction_vehicles = [v for v in self.vehicles if v.direction == direction]
            
            queues[direction_name] = len(direction_vehicles)
            wait_times[direction_name] = sum(v.wait_time for v in direction_vehicles)
        
        return {
            "signal_state": self.signal.get_signal_state(),
            "vehicle_queues": queues,
            "wait_times": wait_times,
            "total_vehicles": len(self.vehicles),
            "vehicles_generated": self.total_vehicles_generated,
            "vehicles_completed": self.total_vehicles_completed,
            "performance_metrics": self._calculate_performance()
        }
    
    def _calculate_performance(self) -> Dict[str, float]:
        """Calculate PRIT-style performance metrics"""
        
        if self.total_vehicles_generated == 0:
            return {"throughput": 0.0, "efficiency": 0.0, "avg_wait": 0.0}
        
        # Throughput (vehicles per hour)
        simulation_hours = max(0.001, self.signal.time_in_phase / 3600)
        throughput = self.total_vehicles_completed / simulation_hours
        
        # Efficiency (% of generated vehicles completed)
        efficiency = (self.total_vehicles_completed / self.total_vehicles_generated) * 100
        
        # Average wait time
        total_wait = sum(v.wait_time for v in self.vehicles)
        avg_wait = total_wait / len(self.vehicles) if self.vehicles else 0.0
        
        return {
            "throughput": throughput,
            "efficiency": efficiency,
            "avg_wait": avg_wait,
            "total_queue": len(self.vehicles)
        }
    
    def connect_neat_network(self, network):
        """Connect NEAT neural network for AI control"""
        self.neat_network = network
    
    def get_neat_fitness(self) -> float:
        """Calculate fitness score for NEAT evolution"""
        performance = self._calculate_performance()
        
        # PRIT fitness function (maximize throughput, minimize wait)
        fitness = (
            performance["throughput"] * 0.4 +
            performance["efficiency"] * 0.3 +
            max(0, 100 - performance["avg_wait"]) * 0.3
        )
        
        return fitness
