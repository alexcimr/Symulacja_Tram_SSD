import bisect
import math
from dataclasses import dataclass


@dataclass
class ShapePath:
    points: list
    distances: list

    def at(self, distance):
        if distance <= 0:
            return self.points[0]
        if distance >= self.distances[-1]:
            return self.points[-1]
        index = bisect.bisect_right(self.distances, distance) - 1
        length = self.distances[index + 1] - self.distances[index]
        if length <= 0:
            return self.points[index]
        ratio = (distance - self.distances[index]) / length
        a, b = self.points[index], self.points[index + 1]
        return (a[0] + ratio * (b[0] - a[0]), a[1] + ratio * (b[1] - a[1]))


def build_path(points):
    if len(points) < 2:
        return None
    lat_ref = sum(lat for _, lat in points) / len(points)
    x_factor = 111320 * math.cos(math.radians(lat_ref))
    y_factor = 111320
    distances = [0.0]
    for (lon1, lat1), (lon2, lat2) in zip(points, points[1:]):
        length = math.hypot((lon2 - lon1) * x_factor, (lat2 - lat1) * y_factor)
        distances.append(distances[-1] + length)
    if distances[-1] == 0:
        return None
    return ShapePath(points, distances)


def match_stops(path, stops, max_distance=200):
    # Szukamy kolejnych punktow przystankowych na tej samej trasie.
    # Przeszukiwanie od poprzedniego dopasowania pilnuje kierunku jazdy.
    lat_ref = sum(lat for _, lat in path.points) / len(path.points)
    x_factor = 111320 * math.cos(math.radians(lat_ref))
    y_factor = 111320
    progress = []
    previous = 0.0

    for stop in stops:
        best = None
        for i, ((lon1, lat1), (lon2, lat2)) in enumerate(zip(path.points, path.points[1:])):
            start = path.distances[i]
            finish = path.distances[i + 1]
            if finish < previous:
                continue
            vx = (lon2 - lon1) * x_factor
            vy = (lat2 - lat1) * y_factor
            px = (stop['lon'] - lon1) * x_factor
            py = (stop['lat'] - lat1) * y_factor
            denominator = vx * vx + vy * vy
            fraction = max(0.0, min(1.0, (px * vx + py * vy) / denominator)) if denominator else 0.0
            if finish > start:
                fraction = max(fraction, (previous - start) / (finish - start))
                fraction = min(1.0, fraction)
            distance = start + fraction * (finish - start)
            dx = px - fraction * vx
            dy = py - fraction * vy
            error = math.hypot(dx, dy)
            candidate = (error, distance)
            if best is None or candidate < best:
                best = candidate

        if best is None or best[0] > max_distance:
            return None
        previous = best[1]
        progress.append(previous)
    return progress
