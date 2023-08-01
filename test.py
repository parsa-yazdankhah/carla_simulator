#!/usr/bin/env python

# Created by Parsa Yazdankhah (2023, 1 Aug)

import glob 
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random
import time
import threading
import queue


def process_data(queue_data, output_folder):
    while True:
        try:
            # Wait for 1 second for data to be available in the queue
            data = queue_data.get(timeout=1.0)  

            # Create a filename using the timestamp of the data
            timestamp = str(int(time.time() * 1000))  # Milliseconds since epoch
            filename = os.path.join(output_folder, f'data_{timestamp}.txt')

            # Write the data to the file
            with open(filename, 'w') as f:
                f.write(str(data))

        except queue.Empty:
            continue

def save_image(image, output_folder):
    print("save_image running ...")
    if image is not None:
        timestamp = str(int(time.time() * 1000))
        filename = os.path.join(output_folder, f'image_{timestamp}.png')
        image.save_to_disk(filename)

def main(output_folder):
    actor_list = []
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # Spawn a vehicle of random choice into world
        bp = random.choice(blueprint_library.filter('vehicle'))
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)
        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(bp, transform)
        actor_list.append(vehicle)
        vehicle.set_autopilot(True)
        print(f'created {vehicle.type_id}')

        # Spawn a camera attached to the vehicle
        camera_rgb = world.spawn_actor(
            blueprint_library.find('sensor.camera.rgb'),
            carla.Transform(carla.Location(x=1.5, z=2.4)),
            attach_to=vehicle)
        actor_list.append(camera_rgb)
        print(f'created {camera_rgb.type_id}')

        # Create a synchronous mode context
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.1  # Simulation step size in seconds
        world.apply_settings(settings)

        # Set up the data processing thread
        data_queue = queue.Queue()
        data_thread = threading.Thread(target=process_data, args=(data_queue, output_folder))
        data_thread.start()
        # image_thread = threading.Thread(target=process_image, args=(image, output_folder))
        # image_thread.start()

        print("entering while loop")
        time0 = time.time()
        while True:
            # Synchronize the simulation
            world.tick()

            # Get data from the sensors
            vehicle_location = vehicle.get_location()
            vehicle_velocity = vehicle.get_velocity()
            vehicle_acceleration = vehicle.get_acceleration()
            # camera_data = camera_rgb.get_last_data()
            # image = camera_rgb.listen(lambda image: image.frame)

            # Put the data into the queue
            data = {
                'vehicle_location': (vehicle_location.x,vehicle_location.y,vehicle_location.z),
                'vehicle_velocity': (vehicle_velocity.x,vehicle_velocity.y,vehicle_velocity.z),
                'vehicle_acceleration': (vehicle_acceleration.x,vehicle_acceleration.y,vehicle_acceleration.z),
                # 'camera_data': image
            }
            data_queue.put(data)

            # save_image(image, output_folder)

            time1 = time.time()
            if (time1-time0) > 60:
                break
        
        time.sleep(10)

    finally:
        print("entering finally part")
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        data_thread.join()
        print("done.")


if __name__ == '__main__':
    try:
        output_folder = '/home/parsa/Cheetah/carla_simulator/out'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        main(output_folder)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')