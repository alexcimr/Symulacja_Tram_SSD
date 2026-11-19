import argparse
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from gtfs import read, timetable
from simulation import Simulation


def seconds(clock):
    hour, minute = map(int, clock.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Godzina musi miec format HH:MM")
    return hour * 3600 + minute * 60


def clock_label(second):
    return f"{int(second // 3600):02d}:{int(second % 3600 // 60):02d}"


def draw_network(ax):
    routes = read("routes.txt")
    trips = read("trips.txt")
    stops = read("stops.txt")
    shapes = read("shapes.txt")
    lines = trips[["route_id", "shape_id"]].drop_duplicates().merge(routes, on="route_id")
    paths = dict(tuple(shapes.sort_values("shape_pt_sequence").groupby("shape_id")))
    colors = plt.get_cmap("tab20")

    for i, (_, group) in enumerate(lines.groupby("route_short_name")):
        for shape_id in group.shape_id:
            if shape_id not in paths:
                continue
            path = paths[shape_id]
            ax.plot(path.shape_pt_lon, path.shape_pt_lat, color=colors(i % 20), linewidth=1, alpha=0.6, zorder=1)
    ax.scatter(stops.stop_lon, stops.stop_lat, s=5, color="black", zorder=2)
    ax.set_aspect(1.55)
    ax.set_xlabel("Dlugosc geograficzna")
    ax.set_ylabel("Szerokosc geograficzna")


def save_log(sim, filename):
    import csv

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["second", "trip_id", "line", "event", "stop_id"])
        writer.writerows(sim.log)
    print(f"Zapisano zdarzenia: {path}")


def main():
    parser = argparse.ArgumentParser(description="Checkpoint 2 - symulacja tramwajow Krakowa")
    parser.add_argument("clock", nargs="?", default="08:00")
    parser.add_argument("day", nargs="?", default=date.today().isoformat())
    parser.add_argument("--duration", type=int, default=60, help="Czas symulacji w minutach")
    parser.add_argument("--step", type=int, default=30, help="Sekundy symulacji na klatke")
    parser.add_argument("--interval", type=int, default=100, help="Milisekundy miedzy klatkami")
    parser.add_argument("--no-animation", action="store_true", help="Uruchom bez okna wykresu")
    parser.add_argument("--log", default="", help="Zapisz zdarzenia do CSV")
    parser.add_argument("--labels", type=int, default=50, help="Maksymalna liczba numerow linii na mapie (0 = brak)")
    args = parser.parse_args()
    if args.duration <= 0 or args.step <= 0 or args.interval <= 0:
        parser.error("duration, step i interval musza byc dodatnie")

    start = seconds(args.clock)
    end = start + args.duration * 60
    day = date.fromisoformat(args.day)
    times = timetable(day)
    if times.empty:
        raise SystemExit("Brak kursow w GTFS dla podanej daty. Sprawdz zakres dat pliku ZIP.")
    sim = Simulation(times)
    sim.advance_to(start)

    if args.no_animation:
        sim.advance_to(end)
        print(f"Koniec: {clock_label(end)} | {sim.stats()} | zdarzenia: {len(sim.log)}")
        if args.log:
            save_log(sim, args.log)
        return

    fig, ax = plt.subplots(figsize=(10, 8))
    draw_network(ax)
    moving_points = ax.scatter([], [], s=35, c="red", edgecolors="white", zorder=4)
    stopped_points = ax.scatter([], [], s=35, c="orange", edgecolors="white", zorder=4)
    info = ax.text(0.01, 0.99, "", transform=ax.transAxes, va="top", bbox={"facecolor": "white", "alpha": 0.85})
    labels = [ax.text(0, 0, "", fontsize=7, zorder=5) for _ in range(max(0, args.labels))]
    frames = (args.duration * 60 + args.step - 1) // args.step + 1

    def update(frame):
        sim.advance_to(min(end, start + frame * args.step))
        moving = [t.position(sim.now) for t in sim.visible() if t.status == "moving"]
        stopped = [t.position(sim.now) for t in sim.visible() if t.status == "stopped"]
        moving_points.set_offsets(moving if moving else [(float("nan"), float("nan"))])
        stopped_points.set_offsets(stopped if stopped else [(float("nan"), float("nan"))])
        visible = sim.visible()
        for label, tram in zip(labels, visible):
            label.set_position(tram.position(sim.now))
            label.set_text(tram.line)
        for label in labels[len(visible):]:
            label.set_text("")
        stats = sim.stats()
        info.set_text(f"{day} {clock_label(sim.now)}\nJada: {stats['moving']}  Stoja: {stats['stopped']}")
        return moving_points, stopped_points, info

    animation = FuncAnimation(fig, update, frames=range(frames), interval=args.interval, repeat=False, blit=False)
    fig._animation = animation
    ax.set_title("Symulacja tramwajow Krakowa (czerwony = jazda, pomaranczowy = postoj)")
    plt.show()
    if args.log:
        sim.advance_to(end)
        save_log(sim, args.log)


if __name__ == "__main__":
    main()
