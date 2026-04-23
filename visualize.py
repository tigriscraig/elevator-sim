import sys
import tkinter as tk
from elevator import Elevator, GO_UP, GO_DOWN, STOP

STEP_MS = 500
CANVAS_WIDTH = 300
CANVAS_HEIGHT = 500
INFO_WIDTH = 200
MIN_BAND_HEIGHT = 14
PAD_FLOORS = 2

COLOR_NORMAL = "#e8e8e8"
COLOR_PENDING = "#f5c542"
COLOR_VISITED = "#7ec87e"
COLOR_CAR = "#3a7bd5"
COLOR_DIR_UP = "#2ecc71"
COLOR_DIR_DOWN = "#e74c3c"
COLOR_DIR_STOP = "#888888"


class ElevatorApp:
    def __init__(self, root, elevator, all_floors):
        self.root = root
        self.elevator = elevator
        self.playing = False
        self._after_id = None
        self._tick = 0
        self._total_ticks = None  # unknown until done

        self._min_floor = 1
        self._max_floor = max(all_floors) + PAD_FLOORS
        self._num_floors = self._max_floor - self._min_floor + 1
        self._band_h = max(MIN_BAND_HEIGHT, CANVAS_HEIGHT / self._num_floors)
        self._canvas_h = int(self._band_h * self._num_floors)
        self._scrollable = self._band_h == MIN_BAND_HEIGHT

        self._build_ui()
        self.render()

    def _build_ui(self):
        self.root.title("Elevator Simulator")
        self.root.resizable(False, False)

        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- left: building canvas ---
        left = tk.Frame(top)
        left.pack(side=tk.LEFT, padx=8, pady=8)

        self.canvas = tk.Canvas(left, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                bg="white", scrollregion=(0, 0, CANVAS_WIDTH, self._canvas_h))
        if self._scrollable:
            vsb = tk.Scrollbar(left, orient=tk.VERTICAL, command=self.canvas.yview)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side=tk.LEFT)

        # --- right: info panel ---
        right = tk.Frame(top, width=INFO_WIDTH)
        right.pack(side=tk.LEFT, padx=8, pady=8, fill=tk.Y)
        right.pack_propagate(False)

        def lbl(text, **kw):
            l = tk.Label(right, text=text, anchor="w", **kw)
            l.pack(fill=tk.X, pady=2)
            return l

        lbl("Simulation State", font=("Helvetica", 12, "bold"))
        self.lbl_timer = lbl("Timer: 0 s")
        self.lbl_floor = lbl("Floor: —")
        self.lbl_dir = lbl("Direction: —")
        lbl("", pady=0)
        lbl("Pending requests:", font=("Helvetica", 10, "bold"))
        self.lbl_pending = lbl("—")
        lbl("Visited floors:", font=("Helvetica", 10, "bold"))
        self.lbl_visited = lbl("—")

        # --- bottom: controls ---
        bot = tk.Frame(self.root)
        bot.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)

        self.btn_play = tk.Button(bot, text="Play", width=10, command=self._toggle)
        self.btn_play.pack(side=tk.LEFT, padx=4)

        if not self.elevator.has_requests():
            self.btn_play.config(state=tk.DISABLED)

        self.lbl_tick = tk.Label(bot, text="Tick 0")
        self.lbl_tick.pack(side=tk.LEFT, padx=8)

    def _floor_y(self, floor):
        """Top y-coordinate of the band for the given floor."""
        offset = self._max_floor - floor
        return int(offset * self._band_h)

    def render(self):
        e = self.elevator
        self.canvas.delete("all")

        # draw floor bands
        for f in range(self._min_floor, self._max_floor + 1):
            y = self._floor_y(f)
            if f in e._requests:
                fill = COLOR_PENDING
            elif f in e._visited:
                fill = COLOR_VISITED
            else:
                fill = COLOR_NORMAL
            self.canvas.create_rectangle(0, y, CANVAS_WIDTH, y + self._band_h - 1,
                                         fill=fill, outline="#cccccc")
            self.canvas.create_text(8, y + self._band_h / 2,
                                    text=str(f), font=("Helvetica", 9, "bold"),
                                    anchor="w", fill="black")

        # draw elevator car
        car_y = self._floor_y(e._floor)
        car_x0 = 50
        car_x1 = CANVAS_WIDTH - 10
        self.canvas.create_rectangle(car_x0, car_y + 1, car_x1,
                                     car_y + self._band_h - 2,
                                     fill=COLOR_CAR, outline="#1a4fa0")

        # direction arrow on left side of car
        if e._move == GO_UP:
            arrow = "^"
        elif e._move == GO_DOWN:
            arrow = "v"
        else:
            arrow = "="
        self.canvas.create_text(car_x0 + 10, car_y + self._band_h / 2,
                                 text=arrow, fill="white",
                                 font=("Helvetica", 10, "bold"), anchor="center")

        # ASCII passengers — one per pending request
        passengers = " ".join("o\n|" if self._band_h >= 28 else "o"
                               for _ in e._requests)
        if passengers:
            self.canvas.create_text(car_x0 + 28, car_y + self._band_h / 2,
                                     text=passengers, fill="white",
                                     font=("Courier", 8, "bold"), anchor="w")

        # scroll canvas to keep car visible
        if self._scrollable:
            frac = (self._floor_y(e._floor) / self._canvas_h)
            self.canvas.yview_moveto(max(0, frac - 0.1))

        # update labels
        self.lbl_timer.config(text=f"Timer: {e._timer} s")
        self.lbl_floor.config(text=f"Floor: {e._floor}")

        if e._move == GO_UP:
            dir_text, dir_color = "UP  ^", COLOR_DIR_UP
        elif e._move == GO_DOWN:
            dir_text, dir_color = "DOWN  v", COLOR_DIR_DOWN
        else:
            dir_text, dir_color = "STOPPED  =", COLOR_DIR_STOP
        self.lbl_dir.config(text=f"Direction: {dir_text}", fg=dir_color)

        self.lbl_pending.config(text=", ".join(map(str, e._requests)) or "—")
        self.lbl_visited.config(text=", ".join(map(str, e._visited)) or "—")
        self.lbl_tick.config(text=f"Tick {self._tick}")

    def _step(self):
        self.elevator.update()
        self._tick += 1
        self.render()
        if self.elevator.has_requests():
            self._after_id = self.root.after(STEP_MS, self._step)
        else:
            self.playing = False
            self.btn_play.config(text="Done", state=tk.DISABLED)

    def _toggle(self):
        if self.playing:
            self._pause()
        else:
            self._resume()

    def _pause(self):
        self.playing = False
        self.btn_play.config(text="Resume")
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _resume(self):
        if not self.elevator.has_requests():
            return
        self.playing = True
        self.btn_play.config(text="Pause")
        self._after_id = self.root.after(STEP_MS, self._step)


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <start_floor> [req1] [req2] ...")
        sys.exit(1)

    floors = [int(x) for x in sys.argv[1:]]
    start = floors[0]
    requests = floors[1:]

    elevator = Elevator(start)
    elevator.add_requests(requests)

    all_floors = [start] + requests if requests else [start]

    root = tk.Tk()
    ElevatorApp(root, elevator, all_floors)
    root.mainloop()


if __name__ == "__main__":
    main()
