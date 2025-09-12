import time
from tkinter import ttk
import tkinter as tk

import krpc
def main():
    global conn, vessel, root


    root = tk.Tk()
    root.title("ksp tel")


    conn = krpc.connect(
        name='test',
        address = '127.0.0.1',
        rpc_port = 50000, stream_port=50001)


    vessel = conn.space_center.active_vessel
    vessel.name = "Ghidorah 9 - Crew Rodan"
    while True:
        flight_info = vessel.flight()
        print(flight_info.mean_altitude)
        print(flight_info.pitch)
        time.sleep(0.02)

    root.mainloop()

if __name__ == '__main__':
    main()
