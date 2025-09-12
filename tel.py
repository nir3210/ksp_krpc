import time
import krpc

def get_tel(vessel, flight, orbit, control):

    vs = flight.vertical_speed
    speed = flight.speed
    altitude = flight.mean_altitude
    twr = vessel.thrust / (vessel.mass * 9.81) if vessel.mass > 0 else 0
    mach = flight.mach
    thr = control.throttle

    return {
        "vs":vs,
        "speed":speed,
        "altitude":altitude,
        "twr":twr,
        "mach":mach,
        "thr":thr
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
    control = vessel.control


    while True:
        flight_perms = get_tel(vessel, flight, orbit, control)
        print(f"VS: {flight_perms['vs']:.2f}m/s, speed: {flight_perms['speed']:.2f}m/s, altitude: {flight_perms['altitude']:.2f}m, twr: {flight_perms['twr']:.2f}")
        print(f"mach: {flight_perms['mach']:.2f}, thr: {flight_perms['thr']:.2f}")
        time.sleep(0.05)


if __name__ == '__main__':
    main()
