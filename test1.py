import time
#from tkinter import ttk
#import tkinter as tk

import krpc

def get_tel(vessel, flight, orbit):


    vs = flight.vertical_speed
    speed = flight.speed
    altitude = flight.mean_altitude
    twr = vessel.thrust / (vessel.mass * 9.81) if vessel.mass > 0 else 0
    mach = flight.mach


    return {
        "vs":vs,
        "speed":speed,
        "altitude":altitude,
        "twr":twr,
        "mach":mach
    }

def main():
    conn = krpc.connect(
        name='test',
        address = '127.0.0.1',
        rpc_port = 50000, stream_port=50001)


    vessel = conn.space_center.active_vessel
    vessel.name = "Ghidorah 9 - Crew Rodan"

    flight = vessel.flight(vessel.orbit.body.reference_frame)
    orbit = vessel.orbit


    while True:
        flight_perms = get_tel(vessel, flight, orbit)
        print(f"VS: {flight_perms['vs']:.2f}m/s, speed: {flight_perms['speed']:.2f}m/s, altitude: {flight_perms['altitude']:.2f}m, twr: {flight_perms['twr']:.2f}")
        print(f"mach: {flight_perms['mach']:.2f}")
        time.sleep(0.02)


if __name__ == '__main__':
    main()
