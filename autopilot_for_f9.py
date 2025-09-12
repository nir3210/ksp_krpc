import threading
import krpc
import time

conn = None
vessel = None

first_stage_cut_off_apo = 73000
first_stage_pitch_end = 45

def launch_sequence():
    global vessel, conn
    control = vessel.control
    flight = vessel.flight(vessel.orbit.body.reference_frame)
    orbit = vessel.orbit

    control.sas = False
    control.rcs = False
    control.throttle = 0
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(90, 90)

    control.activate_next_stage()
    #launch_time = conn.space_center.ut
    for i in range(101):
        control.throttle = i/100
        time.sleep(0.01)

    time.sleep(0.12)

    control.activate_next_stage()

    while True:
        #ut = conn.space_center
        #t_since_launch = ut - launch_time
        apo = orbit.apoapsis_altitude
        alt = flight.mean_altitude
        print(f"apo: {apo:.2f}, alt: {alt:.2f}")

        if alt > 500 and apo < first_stage_cut_off_apo:
            frac = apo / first_stage_cut_off_apo
            frac = min(frac, 1.0)
            pitch = 90 - frac * (90 - first_stage_pitch_end)
            vessel.auto_pilot.target_pitch_and_heading(pitch , 90)
            print(pitch)
        time.sleep(0.02)





def main():
    global conn, vessel
    conn = krpc.connect(
        name='test',
        address = '127.0.0.1',
        rpc_port = 50000, stream_port=50001
    )

    vessel = conn.space_center.active_vessel
    vessel.name = "Ghidorah 9 - Crew Rodan"


    threading.Thread(target=launch_sequence, daemon=True).start()

if __name__ == '__main__':
    main()
    while True:
        time.sleep(1)