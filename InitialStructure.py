from dataclasses import dataclass
from typing import List, Dict, Callable
import enum	

class EventType(enum.Enum):
    DELAY = "Delay"
    TRAVEL = "Travel"
    OFFLOAD = "Offload to station"
    FILL = "Fill trailer at plant"

@dataclass
class Station:
    volume: float
    max_pressure: float
    min_pressure: float
    current_mass: float = 0
    current_pressure: float = 0
    dp_vs_mass_function: Callable[[float], float] = lambda x: x  # Placeholder

@dataclass
class Trailer:
    volume: float
    max_pressure: float
    min_pressure: float
    current_mass: float = 0
    current_pressure: float = 0
    dp_vs_mass_function: Callable[[float], float] = lambda x: x  # Placeholder

@dataclass
class Event:
    type: EventType
    duration: float
    target: str = ""  # For OFFLOAD and FILL events

@dataclass
class SimulationState:
    time: float
    trailer: Trailer
    stations: Dict[str, Station]
    temperature: float

def simulate_lh2_refill(events: List[Event], trailer: Trailer, stations: Dict[str, Station], initial_temperature: float) -> List[SimulationState]:
    state = SimulationState(time=0, trailer=trailer, stations=stations, temperature=initial_temperature)
    log = [state]

    for event in events:
        if event.type == EventType.DELAY:
            state.time += event.duration
        elif event.type == EventType.TRAVEL:
            state.time += event.duration
            # You might want to add some fuel consumption or other effects here
        elif event.type == EventType.OFFLOAD:
            station = state.stations[event.target]
            # Implement offloading logic here
            # Update trailer and station properties
        elif event.type == EventType.FILL:
            # Implement filling logic here
            # Update trailer properties

        # Update temperature (simplified thermal model)
        # In the final version, you'd implement a more complex thermal model here

        # Log the new state
        log.append(SimulationState(
            time=state.time,
            trailer=Trailer(**vars(state.trailer)),
            stations={name: Station(**vars(station)) for name, station in state.stations.items()},
            temperature=state.temperature
        ))

    return log

def main():
    # Define initial conditions
    trailer = Trailer(volume=100, max_pressure=10, min_pressure=1)
    stations = {
        "Station1": Station(volume=500, max_pressure=8, min_pressure=2),
        "Plant": Station(volume=1000, max_pressure=15, min_pressure=5)
    }
    initial_temperature = 20  # Celsius

    # Define events
    events = [
        Event(type=EventType.FILL, duration=2, target="Plant"),
        Event(type=EventType.TRAVEL, duration=5),
        Event(type=EventType.OFFLOAD, duration=1, target="Station1"),
        Event(type=EventType.TRAVEL, duration=5),
        Event(type=EventType.FILL, duration=2, target="Plant"),
    ]

    # Run simulation
    simulation_log = simulate_lh2_refill(events, trailer, stations, initial_temperature)

    # Print results (you can modify this to suit your needs)
    for state in simulation_log:
        print(f"Time: {state.time}, Trailer Mass: {state.trailer.current_mass}, Temperature: {state.temperature}")
        for name, station in state.stations.items():
            print(f"  {name} Mass: {station.current_mass}")
        print()

if __name__ == "__main__":
    main()
