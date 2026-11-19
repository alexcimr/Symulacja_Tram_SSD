from datetime import date
from pathlib import Path
from zipfile import ZipFile

import gtfs
from simulation import Simulation


def test_sample_zip(tmp_path, monkeypatch):
    archive = tmp_path / "GTFS_KRK_T.zip"
    content = {
        "routes.txt": "route_id,route_short_name\nr1,4\n",
        "trips.txt": "route_id,service_id,trip_id,shape_id\nr1,s1,t1,sh1\n",
        "stops.txt": "stop_id,stop_lat,stop_lon\na,50.0,19.0\nb,50.1,19.1\nc,50.2,19.2\n",
        "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\nt1,08:00:00,08:00:00,a,1\nt1,08:05:00,08:06:00,b,2\nt1,08:10:00,08:10:00,c,3\n",
        "calendar_dates.txt": "service_id,date,exception_type\ns1,20261120,1\n",
        "shapes.txt": "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nsh1,50.0,19.0,1\nsh1,50.2,19.2,2\n",
    }
    with ZipFile(archive, "w") as zipfile:
        for name, data in content.items():
            zipfile.writestr(name, data)
    monkeypatch.setattr(gtfs, "PATH", archive)
    times = gtfs.timetable(date(2026, 11, 20))
    assert len(times) == 3
    sim = Simulation(times)
    sim.advance_to(8 * 3600 + 5 * 60 + 30)
    assert sim.trams["t1"].status == "stopped"
    sim.advance_to(8 * 3600 + 10 * 60)
    assert sim.trams["t1"].status == "finished"
    assert len(sim.log) == 4
