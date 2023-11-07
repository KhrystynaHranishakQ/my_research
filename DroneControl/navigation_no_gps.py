"""
An example of simulation of how to control drone with attitude in no GPS mode.
The script uses Drone.py and gps_prediction.py modules from visual navigation.
"""
import threading
from Drone import Mavlink
from config import MAVLINK_PORT, MAVLINK_BAUD, MAVLINK_SOURCE_TARGET, MAVLINK_SOURCE_ID, LOG_DRONE, WORKING_DIR, SIMULATION, LOG_GNSS
import time
from gps_predicton import LinearPredictor

lock = threading.Lock()

drone = Mavlink(MAVLINK_PORT, MAVLINK_BAUD, LOG_DRONE, MAVLINK_SOURCE_TARGET, MAVLINK_SOURCE_ID,
                output_path=WORKING_DIR, simulation=SIMULATION)


drone.start()  # drone class is threading.Thread


gps_predictor = LinearPredictor(drone, LOG_GNSS, WORKING_DIR)
gps_predictor.start()
print(gps_predictor.set_valid_gps_coord)
drone.subscribe_event("GLOBAL_POSITION_INT", gps_predictor.set_valid_gps_coord)
time.sleep(5)

initial_data = drone.autopilot_data["GLOBAL_POSITION"]
init_lon, init_lat = initial_data["lon"], initial_data["lat"]
print(f"Global position: {initial_data}")
#print(drone.get_armed_status())

# enable GPS
drone.set_parameter('SIM_GPS_DISABLE', 0)

# take off
height = 50
drone.arm_and_takeoff(height)
time.sleep(5)

# disable GPS
print('Disable GPS')
drone.set_mode("GUIDED_NoGPS")
drone.set_parameter('SIM_GPS_DISABLE', 1)
time.sleep(5)


def run_trajectory(master, trajectory):
    for step in trajectory:
        # Unpack the step
        roll_angle, pitch_angle, yaw_angle, yaw_rate, use_yaw_rate, thrust, duration, expected_action = step

        # Pack the parameters into a dictionary
        args_dict = {
            'roll_angle': roll_angle,
            'pitch_angle': pitch_angle,
            'yaw_angle': yaw_angle,
            'yaw_rate': yaw_rate,
            'use_yaw_rate': use_yaw_rate,
            'thrust': thrust,
            'duration': duration,
            'expected_action': expected_action
        }

        # Execute the set_attitude function in a separate thread
        thread = threading.Thread(target=master.set_attitude, kwargs=args_dict)
        thread.start()
        thread.join()  # Wait for the command to finish before starting the next


print('Control attitude without GPS')
trajectory = [
    (0, 0, 0, 0, False, 0.5, 3, 'hold the position for 3 seconds'),
    (0, -10, 0, 0, False, 0.5, 10, 'move forward'),  # move forward
    (0, 0, 0, 0, False, 0.5, 3, 'hold the position for 3 seconds'),  # will fly with inertion
    (0, -10, 90, 0, False, 0.5, 10, 'turn right'),
    (0, 0, 0, 0, False, 0.5, 3, 'hold the position for 3 seconds'),  # will fly with inertion
    (0, 10, 0, 0, False, 0.5, 10, 'move backward'),   # move backward but because of inertion a drone does not move backword
]

# trajectory = [
#     # Step 1: Go forward
#     (0.0, 5.0, 0.0, 0.0, False, 0.5, 5, 'Go forward'),
#     # Step 2: Hover in place
#     (0.0, 0.0, 0.0, 0.0, False, 0.5, 2, 'Hover in place'),
#     # Step 3: Turn left 90 degrees
#     (0.0, 5.0, 90.0, 0.0, False, 0.5, 5, 'Turn left 90 degrees and forward'),
#     # Step 4: Go forward
#     #(0.0, -5.0, 0.0, 0.0, False, 0.5, 5, 'Go forward'),
#     # Step 5: Hover in place
#     (0.0, 0.0, 0.0, 0.0, False, 0.5, 2, 'Hover in place'),
#     # Step 6: Turn left 90 degrees
#     (0.0, 5.0, 90.0, 0.0, False, 0.5, 5, 'Turn left 90 degrees and forward'),
#     # Step 7: Go forward
#     #(0.0, -5.0, 0.0, 0.0, False, 0.5, 5, 'Go forward'),
#     # Step 8: Hover in place
#     (0.0, 0.0, 0.0, 0.0, False, 0.5, 2, 'Hover in place'),
#     # Step 9: Turn left 90 degrees
#     (0.0, 5.0, 90.0, 0.0, False, 0.5, 5, 'Turn left 90 degrees and forward'),
#     # Step 10: Go forward to starting point
#     #(0.0, -5.0, 0.0, 0.0, False, 0.5, 5, 'Go forward to starting point'),
#]

run_trajectory(drone, trajectory)

print('Back home and land')
drone.set_parameter('SIM_GPS_DISABLE', 0)
time.sleep(3)
drone.set_mode("RTL")

print("Done")


