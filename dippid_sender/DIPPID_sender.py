# Imports
import socket
import time
import numpy as np
import json

# Setup
IP = '127.0.0.1'
PORT = 5700
UPDATE_RATE = 50
SLEEP_TIME = 1.0 / UPDATE_RATE

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Starting DIPPID simulator, sending to {IP}:{PORT}...")
    print("Press Ctrl+C to stop.")

    start_time = time.time()

    try:
        while True:
            t = time.time() - start_time
            print(t)

            # 1. Accelerometer (Visualizer expects -2 to 2, reference vis_solution.py)
            accel_x = add_noise(np.sin(t * 1.5))            # higher frequency, shorter period
            accel_y = add_noise(np.sin(t * 3.0))            # I also added custom noise function, this is because if you look at the DIPPID values from my phone, they are very noisy!
            accel_z = add_noise(np.sin(t * 0.5))            # lower frequency, longer period

            # 2. Gyroscope (Visualizer expects -10 to 10), (check vis_solution.py)
            gyro_x = add_noise(np.sin(t * 5.0) * 8.0)       # Multiplied by 8 to make the graph jump higher
            gyro_y = add_noise(np.cos(t * 2.0) * 5.0)   
            gyro_z = add_noise(np.sin(t * 1.0) * 9.0)

            # 3. Gravity (Visualizer expects -10 to 10)
            grav_x = add_noise(np.sin(t * 0.1))             # Slight wobble, due to very long period
            grav_y = add_noise(np.cos(t * 0.1))             # Slight wobble
            grav_z = add_noise(9.81)                        # Real gravity on the Z axis

            # 4. Button 1  (95%: 0, 5%: 1)
            button_state = int(np.random.choice([0, 1], p=[0.95, 0.05]))  

            # Construct Payload
            payload = {
                "heartbeat": time.time(),
                "accelerometer": {
                    "x": round(float(accel_x), 3),
                    "y": round(float(accel_y), 3),
                    "z": round(float(accel_z), 3)
                },
                "gyroscope": {
                    "x": round(float(gyro_x), 3),
                    "y": round(float(gyro_y), 3),
                    "z": round(float(gyro_z), 3)
                },
                "gravity": {
                    "x": round(float(grav_x), 3),
                    "y": round(float(grav_y), 3),
                    "z": round(float(grav_z), 3)
                },
                "button_1": button_state
            }

            message = json.dumps(payload)
            sock.sendto(message.encode(), (IP, PORT))
            print("Sent packet!")
            time.sleep(SLEEP_TIME)

    except KeyboardInterrupt:
        print("\nSimulation stopped safely.")
    finally:
        sock.close()

# Small function to add proportional noise, but maybe noise shouldnt be proportional
def add_noise(value, noise_factor=0.05, base_noise=0.02): 
    """
    Adds realistic, proportional noise to a sensor value.
    noise_factor: How much the noise scales with the size of the value (5% by default)
    base_noise: The constant static noise that is always there
    """
    # Calculate the maximum possible noise for this specific value
    noise_magnitude = base_noise + (abs(value) * noise_factor)
    
    # Generate a random float between -noise_magnitude and +noise_magnitude
    noise = np.random.uniform(-noise_magnitude, noise_magnitude)
    
    return value + noise

if __name__ == "__main__":
    main()