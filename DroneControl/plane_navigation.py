from pymavlink import mavutil
import time

# Connect to the vehicle
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')  # Adjust the connection string to your setup
master.wait_heartbeat()
print(master)

def set_mode(mode_name):
    mode_id = master.mode_mapping()[mode_name]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)

# 2. Take off in a suitable mode, e.g., STABILIZE, and fly for 15 seconds
set_mode('FBWA')
master.arducopter_arm()
time.sleep(2)

print('Take off and move up forward')
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     1500, 1500, 1800, 1500, 0, 0, 0, 0)
time.sleep(60)

print('Disable GPS')
master.mav.param_set_send(master.target_system, master.target_component,
                          b'SIM_GPS_DISABLE', 1, mavutil.mavlink.MAV_PARAM_TYPE_UINT8)
time.sleep(2)

print('Turn right and move forward')
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     2000, 1500, 1500, 1500, 0, 0, 0, 0)
time.sleep(3)
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     1500, 1500, 1600, 1500, 0, 0, 0, 0)
time.sleep(30)

print('Turn left and move forward')
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     1000, 1500, 1500, 1500, 0, 0, 0, 0)
time.sleep(3)
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     1500, 1500, 1500, 1500, 0, 0, 0, 0)
time.sleep(30)

print('Go down moving forward')
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     1500, 1000, 1800, 1500, 0, 0, 0, 0)
time.sleep(30)
print('Go up')
master.mav.rc_channels_override_send(master.target_system, master.target_component,
                                     1500, 1500, 1800, 1500, 0, 0, 0, 0)
time.sleep(30)

# print('Check YAW')
# master.mav.rc_channels_override_send(master.target_system, master.target_component,
#                                      1500, 1500, 1800, 1000, 0, 0, 0, 0)
# time.sleep(30)

print('Re-enable GPS')
master.mav.param_set_send(master.target_system, master.target_component,
                          b'SIM_GPS_DISABLE', 0, mavutil.mavlink.MAV_PARAM_TYPE_UINT8)
time.sleep(2)

print('Return Home')
set_mode('RTL')

# 8. Disconnect
master.arducopter_disarm()
master.close()


# Useful links:
# RC channels mapping: https://ardupilot.org/plane/docs/common-rcmap.html
# Mavlink docs:
#   - https://www.samba.org/tridge/UAV/pymavlink/apidocs/mavlink.MAVLink.html#rc_channels_override_send
#   - https://www.samba.org/tridge/UAV/pymavlink/apidocs/nameIndex.html
#   - https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
# Video with switch between GPS/No GPS: https://www.youtube.com/watch?v=0VMx2u8MlUU
# Full list of plane parameters in ArduPilot: https://ardupilot.org/plane/docs/parameters.html 