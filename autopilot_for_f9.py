import threading

import krpc
import time

conn = None
vessel = None

first_stage_cut_off_apo = 73000
first_stage_pitch_end = 45
second_stage_pitch_end = -15
final_orbit_altitude = 160000

def launch_sequence():
    global vessel, conn
    control = vessel.control
    flight = vessel.flight(vessel.orbit.body.reference_frame)
    orbit = vessel.orbit

    stage_of_flight = 1

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

    time.sleep(0.25)

    control.activate_next_stage()

    while True:
        #ut = conn.space_center
        #t_since_launch = ut - launch_time
        apo = orbit.apoapsis_altitude
        alt = flight.mean_altitude
        pre = orbit.periapsis_altitude

        print(f"apo: {apo:.2f}, alt: {alt:.2f}")

        if alt > 600 and apo < first_stage_cut_off_apo and stage_of_flight == 1:
            frac = (apo / first_stage_cut_off_apo) * 1.85
            pitch = 90 - frac * (90 - first_stage_pitch_end)
            if pitch <= first_stage_pitch_end:
                vessel.auto_pilot.target_pitch_and_heading(first_stage_pitch_end, 90)
            else:
                vessel.auto_pilot.target_pitch_and_heading(pitch , 90)
            print(pitch)

        if apo > first_stage_cut_off_apo and stage_of_flight == 1:
            stage_of_flight = 2
            control.throttle = 0

        if stage_of_flight == 2:
            time.sleep(2)
            control.activate_next_stage()
            time.sleep(8)
            control.activate_next_stage()
            control.throttle = 0.2
            time.sleep(5)
            control.throttle = 1
            stage_of_flight = 3

        if stage_of_flight == 3 and pre < final_orbit_altitude and apo < final_orbit_altitude:
            for i in range(first_stage_pitch_end,second_stage_pitch_end-1, -1):
                vessel.auto_pilot.target_pitch_and_heading(i , 90)
                time.sleep(0.14)
                if i == second_stage_pitch_end:
                    stage_of_flight = 4


        if stage_of_flight == 4 and (pre > final_orbit_altitude or apo > final_orbit_altitude):
            control.throttle = 0






        time.sleep(0.01)

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