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


def main():

    # time.sleep(3)
    # # subprocess.run(["python", "manual_control.py", "--sync"])
    # subprocess.Popen(["python", "manual_control.py", "--sync"])
    # time.sleep(3)

    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()

    # Create a synchronous mode context
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.1  # Simulation step size in seconds
    world.apply_settings(settings)

    for actor in world.get_actors():
        if actor.type_id[:7] == "vehicle":
            ego_vehicle = actor

    bp = random.choice(world.get_blueprint_library().filter('*vehicle*'))
    transform = random.choice(world.get_map().get_spawn_points())
    second_vehicle = world.try_spawn_actor(bp, transform)
    second_vehicle.set_autopilot(True)

    agent = BehaviorAgent(ego_vehicle, behavior='aggressive')
    agent.ignore_traffic_lights(True)
    agent.set_destination(second_vehicle.get_location())

    while True:
        if agent.done():
            agent.set_destination(second_vehicle.get_location())

        ego_vehicle.apply_control(agent.run_step())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye Bye :)")