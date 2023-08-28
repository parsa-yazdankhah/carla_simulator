#!/usr/bin/env python

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
import numpy as np


def colision_detector(ego_vehicle: carla.Vehicle, second_vehicle: carla.Vehicle):
    ego_velocity = ego_vehicle.get_velocity()
    ego_velocity_vector = np.array([ego_velocity.x, ego_velocity.y, ego_velocity.z])
    second_velocity = second_vehicle.get_velocity()
    second_velocity_vector = np.array([second_velocity.x, second_velocity.y, second_velocity.z])
    relative_velocity = second_velocity_vector - ego_velocity_vector

    ego_transform = ego_vehicle.get_transform()
    ego_location = np.array([ego_transform.location.x, ego_transform.location.y, ego_transform.location.z, 0])
    second_transform = second_vehicle.get_transform()
    second_location = np.array([second_transform.location.x, second_transform.location.y, second_transform.location.z, 1])
    relative_distance = second_location - ego_location

    refernce_unit_vector = np.array([ego_transform.get_forward_vector().x, ego_transform.get_forward_vector().y, ego_transform.get_forward_vector().z])
    relative_velocity_local = np.dot(relative_velocity, refernce_unit_vector)

    rotation_matrix = ego_transform.get_inverse_matrix()
    relative_distance_local = np.dot(relative_distance, rotation_matrix)
    distance = relative_distance_local[0] - max(ego_vehicle.bounding_box.extent.y, ego_vehicle.bounding_box.extent.x) \
                        - max(second_vehicle.bounding_box.extent.y, second_vehicle.bounding_box.extent.x)
    
    t = np.linalg.norm(ego_velocity_vector) / 9.81

    if relative_velocity_local < 0 and (distance)/abs(relative_velocity_local) < t:
        print(f'time to stop: {t:.4f} sec')
        return True


def main():

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        world = client.get_world()

        # Create a synchronous mode context
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.1  # Simulation step size in seconds
        world.apply_settings(settings)

        ego_vehicle = None
        while ego_vehicle is None:
            print("Waiting for the ego vehicle...")
            time.sleep(1)
            possible_vehicles = world.get_actors().filter('vehicle.*')
            for vehicle in possible_vehicles:
                if vehicle.attributes['role_name'] == 'hero':
                    print("Ego vehicle found")
                    ego_vehicle = vehicle
                    break
        
        bp = random.choice(world.get_blueprint_library().filter('vehicle.dodge.charger_2020'))
        transform = ego_vehicle.get_transform()
        transform.location.x += 70
        transform.location.z += 1
        second_vehicle = world.try_spawn_actor(bp, transform)

        spectator = world.get_spectator()
        ego_vehicle_control = ego_vehicle.get_control()

        ego_vehicle_control.throttle = 1.0
        ego_vehicle_control.brake = 0.0
        ego_vehicle_control.steer = 0.0
        ego_vehicle.apply_control(ego_vehicle_control)

        while True:
            transform = ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(transform.location + carla.Location(z=30),carla.Rotation(pitch=-90)))

            if colision_detector(ego_vehicle, second_vehicle):
                ego_vehicle_control.throttle = 0.0
                ego_vehicle_control.brake = 0.7
                ego_vehicle.apply_control(ego_vehicle_control)
                print("Collision is about to occur !!!")
                break

    finally:
        input("Press Enter to continue")
        vehicles_list = []
        for vehicle in world.get_actors().filter('vehicle.*'):
                if vehicle.attributes['role_name'] != 'hero': 
                    vehicles_list.append(vehicle)
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])
        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye Bye :)")