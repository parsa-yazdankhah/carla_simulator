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
import subprocess
from agents.navigation.behavior_agent import BehaviorAgent


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

def get_vehicle_lon_speed(carla_vehicle: carla.Vehicle, reference_vehicle: carla.Vehicle):
        """
         Get the longitudinal speed of a carla vehicle
         :param carla_vehicle: the carla vehicle
         :type carla_vehicle: carla.Vehicle
         :return: speed of a carla vehicle [m/s]
         :rtype: float64
        """
        carla_velocity_vec3 = carla_vehicle.get_velocity()
        vec4 = np.array([carla_velocity_vec3.x,
                         carla_velocity_vec3.y,
                         carla_velocity_vec3.z, 1]).reshape(4, 1)
        carla_trans = np.array(reference_vehicle.get_transform().get_matrix())
        carla_trans.reshape(4, 4)
        carla_trans[0:3, 3] = 0.0
        vel_in_vehicle = np.linalg.inv(carla_trans) @ vec4
        return vel_in_vehicle[0]


def main(output_folder):

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        world = client.get_world()

        # Create a synchronous mode context
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.1  # Simulation step size in seconds
        world.apply_settings(settings)

        # # Set up the data processing thread
        # data_queue = queue.Queue()
        # data_thread = threading.Thread(target=process_data, args=(data_queue, output_folder))
        # data_thread.start()

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

        bp = random.choice(world.get_blueprint_library().filter('*vehicle*'))
        transform = random.choice(world.get_map().get_spawn_points())
        second_vehicle = world.try_spawn_actor(bp, transform)
        second_vehicle.set_autopilot(True)

        agent = BehaviorAgent(ego_vehicle, behavior='aggressive')
        agent.ignore_traffic_lights(True)
        agent.set_destination(second_vehicle.get_location())

        # t0 = time.time()
        # dist0 = ego_vehicle.get_location().distance(second_vehicle.get_location())

        while True:
            if agent.done():
                agent.set_destination(second_vehicle.get_location())
            ego_vehicle.apply_control(agent.run_step())

            ego_vel = get_vehicle_lon_speed(ego_vehicle, ego_vehicle)
            sec_vel = get_vehicle_lon_speed(second_vehicle, ego_vehicle)
            dist = ego_vehicle.get_location().distance(second_vehicle.get_location())
            if (abs(dist)/abs(ego_vel-sec_vel) < 2):
                print("-------- ALARM --------")
            else:
                print("-------- OK --------")


            # dist1 = ego_vehicle.get_location().distance(second_vehicle.get_location())
            # t1 = time.time()
            # rel_vel = (dist1)/(t1-t0)
            # if (dist1/rel_vel < 2):
            #     print("-------- ALARM --------")

            # t0 = time.time()
            # dist0 = ego_vehicle.get_location().distance(second_vehicle.get_location())
            

                # ego_loc = ego_vehicle.get_location()
                # sec_loc = second_vehicle.get_location()
                # ego_vel = ego_vehicle.get_velocity()
                # sec_vel = second_vehicle.get_velocity()

                # if dist < 50 :                
                    # # Put the data into the queue
                    # data = {
                    #     'ego_vehicle_location': (ego_loc.x, ego_loc.y),
                    #     'second_vehicle_location': (sec_loc.x, sec_loc.y),
                    #     'ego_vehicle_velocity': (ego_vel.x, ego_vel.y),
                    #     'second_vehicle_velocity': (sec_vel.x, sec_vel.y),
                    #     'distance': dist,
                    #     'relative speed': (sec_vel.x-ego_vel.x, sec_vel.y-ego_vel.y),
                    # }
                    # data_queue.put(data)
                    # print(data_queue)
                
    except KeyboardInterrupt:
        for npc in world.get_actors().filter('*vehicle*'):
            if npc.id != ego_vehicle.id:
                npc.destroy()


if __name__ == '__main__':
    output_folder = '/home/parsa/Cheetah/carla_simulator/out'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    try:
        main(output_folder)
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye Bye :)")