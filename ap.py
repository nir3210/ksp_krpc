import threading
import krpc
import time

conn = None
vessel = None

def launch_sequence():
    global vessel
    control = vessel.control
    flight = vessel.flight(vessel.orbit.body.reference_frame)
    orbit = vessel.orbit

    control.sas = False
    control.rcs = False
    control.throttle = 0
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(90, 90)

    control.activate_next_stage()
    for i in range(101):
        control.throttle = i/100
        time.sleep(0.01)

    control.activate_next_stage()



def main():
    global conn, vessel
    conn = krpc.connect(
        name='test',
        address = '127.0.0.1',
        rpc_port = 50000, stream_port=50001
    )

    vessel = conn.space_center.active_vessel
    vessel.name = "Ghidorah 9 - Crew Rodan"


    threading.Thread(target=launch_sequence(), daemon=True).start()

if __name__ == '__main__':
    main()