import pandas as pd
import pytest

from simulation import Simulation


def sample():
    rows = []
    for index, (arrival, departure, lon) in enumerate([(0, 0, 0), (60, 90, 10), (150, 150, 20)]):
        rows.append(dict(trip_id="one", route_short_name="4", stop_id=f"S{index}",
                         stop_lon=lon, stop_lat=50, arrival=arrival,
                         departure=departure, stop_sequence=index))
    return pd.DataFrame(rows)


def test_movement_and_stop():
    sim = Simulation(sample())
    sim.advance_to(30)
    tram = sim.trams["one"]
    assert tram.status == "moving"
    assert tram.position(30) == (5, 50)
    sim.advance_to(60)
    assert tram.status == "stopped"
    assert tram.position(70) == (10, 50)
    sim.advance_to(90)
    assert tram.status == "moving"
    sim.advance_to(150)
    assert tram.status == "finished"
    assert [x[3] for x in sim.log] == ["departure", "arrival", "departure", "arrival"]


def test_clock_cannot_go_backwards():
    sim = Simulation(sample())
    sim.advance_to(30)
    with pytest.raises(ValueError):
        sim.advance_to(29)


def test_no_double_events_same_time():
    sim = Simulation(sample())
    sim.advance_to(150)
    old_len = len(sim.log)
    sim.advance_to(150)
    assert len(sim.log) == old_len
