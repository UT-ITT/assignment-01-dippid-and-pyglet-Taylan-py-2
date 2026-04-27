from DIPPID import SensorUDP
from vis_solution import Visualizer

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT) # '127.0.0.1'
update_frequency = 10  # Hz

def main():
    visualizer = Visualizer(sensor=sensor, update_freq=update_frequency)   
    visualizer.run()

if __name__ == '__main__':
    main()