import heapq
from dataclasses import dataclass
from itertools import count


@dataclass
class Tram:
    trip_id: str
    line: str
    stops: list
    index: int = 0
    status: str = "waiting"
    departure: float = 0
    arrival: float = 0

    def position(self, now):
        current = self.stops[self.index]
        if self.status == "moving" and self.index + 1 < len(self.stops):
            following = self.stops[self.index + 1]
            total = self.arrival - self.departure
            ratio = (now - self.departure) / total if total > 0 else 1
            ratio = max(0, min(1, ratio))
            lon = current["lon"] + ratio * (following["lon"] - current["lon"])
            lat = current["lat"] + ratio * (following["lat"] - current["lat"])
            return lon, lat
        return current["lon"], current["lat"]


class Simulation:
    def __init__(self, timetable):
        self.now = 0
        self.trams = {}
        self.events = []
        self.counter = count()
        self.log = []

        for trip_id, group in timetable.groupby("trip_id", sort=False):
            stops = [
                {
                    "id": str(row.stop_id),
                    "lon": float(row.stop_lon),
                    "lat": float(row.stop_lat),
                    "arrival": int(row.arrival),
                    "departure": int(row.departure),
                }
                for row in group.itertuples()
            ]
            if len(stops) < 2:
                continue
            tram = Tram(str(trip_id), str(group.iloc[0].route_short_name), stops)
            self.trams[tram.trip_id] = tram
            self.schedule(stops[0]["departure"], "departure", tram.trip_id)

    def schedule(self, when, kind, trip_id):
        heapq.heappush(self.events, (when, next(self.counter), kind, trip_id))

    def advance_to(self, target):
        if target < self.now:
            raise ValueError("Nie mozna cofnac czasu symulacji")
        while self.events and self.events[0][0] <= target:
            when, _, kind, trip_id = heapq.heappop(self.events)
            self.now = when
            tram = self.trams[trip_id]
            if kind == "departure":
                self.depart(tram)
            elif kind == "arrival":
                self.arrive(tram)
        self.now = target

    def depart(self, tram):
        if tram.index + 1 >= len(tram.stops):
            return
        current = tram.stops[tram.index]
        following = tram.stops[tram.index + 1]
        duration = max(0, following["arrival"] - current["departure"])
        tram.status = "moving"
        tram.departure = self.now
        tram.arrival = self.now + duration
        self.log.append((self.now, tram.trip_id, tram.line, "departure", current["id"]))
        self.schedule(tram.arrival, "arrival", tram.trip_id)

    def arrive(self, tram):
        tram.index += 1
        current = tram.stops[tram.index]
        self.log.append((self.now, tram.trip_id, tram.line, "arrival", current["id"]))
        if tram.index + 1 == len(tram.stops):
            tram.status = "finished"
        else:
            tram.status = "stopped"
            self.schedule(max(self.now, current["departure"]), "departure", tram.trip_id)

    def visible(self):
        return [tram for tram in self.trams.values() if tram.status in ("moving", "stopped")]

    def stats(self):
        return {
            "moving": sum(t.status == "moving" for t in self.trams.values()),
            "stopped": sum(t.status == "stopped" for t in self.trams.values()),
            "finished": sum(t.status == "finished" for t in self.trams.values()),
        }
