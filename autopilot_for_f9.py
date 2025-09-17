import threading
import math
import krpc
import time

conn = None
vessel = None

first_stage_cut_off_apo = 67000
first_stage_pitch_end = 45
second_stage_pitch_end = -15
final_orbit_altitude = 160000





def create_circularization_node():
    global  conn, vessel
    orbit = vessel.orbit
    mu = orbit.body.gravitational_parameter
    r = orbit.apoapsis
    a1 = orbit.semi_major_axis
    v1 = math.sqrt(mu * ((2 / r) - (1 / a1)))
    v2 = math.sqrt(mu * ((2 / r) - (1 / r)))
    delta_v = v2 - v1

    ut = conn.space_center.ut
    node_time = ut + orbit.time_to_apoapsis
    node = vessel.control.add_node(node_time, prograde=delta_v)

    return node, delta_v

def circularize(node, delta_v):
    global vessel, conn
    orbit = vessel.orbit
    control = vessel.control
    f = vessel.available_thrust
    m0 = vessel.mass
    isp = vessel.specific_impulse
    g = 9.81
    m1 = m0 / math.exp(delta_v / (isp * g))
    flow_rate = f / (isp * g)
    burn_time = (m0 - m1) / flow_rate

    warp_to_time = node.ut - 60
    conn.space_center.warp_to(warp_to_time)

    while conn.space_center.ut < warp_to_time + 1:
        time.sleep(0.1)

    vessel.auto_pilot.disengage()
    vessel.control.sas = True
    vessel.control.rcs = True
    vessel.control.sas_mode = conn.space_center.SASMode.maneuver


    while True:
        direction = vessel.flight(vessel.orbit.body.reference_frame).pitch
        target_dir = vessel.auto_pilot.target_pitch
        print(direction, target_dir)
        if abs(direction - target_dir) < 2:
            break
        time.sleep(0.1)


    burn_start_time = node.ut - (burn_time / 2)
    while conn.space_center.ut < burn_start_time:
        time.sleep(0.1)

    vessel.control.throttle = 1.0

    while node.remaining_delta_v > 8:
        time.sleep(0.1)

    vessel.control.throttle = 0

    time.sleep(0.5)
    vessel.control.remove_nodes()


    vessel.auto_pilot.disengage()
    vessel.control.sas = True
    vessel.control.rcs = True

def launch_sequence():
    global vessel, conn

    orbit = vessel.orbit
    control = vessel.control
    flight = vessel.flight(vessel.orbit.body.reference_frame)

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
        time_to_apo = orbit.time_to_apoapsis

        print(f"apo: {apo:.2f}, alt: {alt:.2f}, t to apo: {time_to_apo}")


        if alt > 600 and apo < first_stage_cut_off_apo and stage_of_flight == 1:
            frac = (apo / first_stage_cut_off_apo) * 1.8
            pitch = 90 - frac * (90 - first_stage_pitch_end)
            pitch = max(pitch, first_stage_pitch_end)
            vessel.auto_pilot.target_pitch_and_heading(pitch , 90)
            print(pitch)

        if apo > first_stage_cut_off_apo and stage_of_flight == 1:
            stage_of_flight = 2
            control.throttle = 0

        if stage_of_flight == 2:
            time.sleep(1)
            control.activate_next_stage()

            time.sleep(1)
            control.rcs = True
            control.throttle = 1

            time.sleep(4)
            control.rcs = False
            control.throttle =0
            control.activate_next_stage()
            control.throttle = 0.2

            time.sleep(2)
            control.throttle = 1
            stage_of_flight = 3

        if stage_of_flight == 3 and pre < final_orbit_altitude and apo < final_orbit_altitude:
            for i in range(first_stage_pitch_end,second_stage_pitch_end-1, -1):
                vessel.auto_pilot.target_pitch_and_heading(i , 90)
                time.sleep(0.6)
                if i == second_stage_pitch_end:
                    stage_of_flight = 4

        if stage_of_flight == 4 and time_to_apo < 18:
            for p in range(second_stage_pitch_end, 0, 1):
                vessel.auto_pilot.target_pitch_and_heading(p , 90)
                time.sleep(0.5)
            stage_of_flight = 5

        if stage_of_flight == 4 and (pre > (final_orbit_altitude - 4000) or apo > final_orbit_altitude - 4000):
            control.throttle = 0.01
            stage_of_flight = 5

        if stage_of_flight == 5 and (pre >= final_orbit_altitude or apo >=  final_orbit_altitude):
            control.throttle = 0
            stage_of_flight = 6

        if stage_of_flight == 6:
            time.sleep(0.3)
            node, dv = create_circularization_node()
            circularize(node, dv)








        time.sleep(0.1)

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