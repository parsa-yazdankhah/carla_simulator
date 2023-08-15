# CARLA Simulator
To run the simulator, follow the instructions below:
1. Open a terminal in the source folder of simulator path
2. run `./CarlaUE4.sh` 
- Some options to improve performance are as follows:

   `./CarlaUE4.sh -prefernvidia -renderOffScreen -quality-level=Low`

3. Open a new terminal in the source of python script path
4. run `conda activate [carla_environment]`
- For example, if you have installed carla python package in an environment called *carla*, you should run `conda activate carla`
5. for running a script you should run `python test.py` in terminal
- Examples can be found in source folder under */PythonAPI/examples*

## Test Scenarios
To simulate some predefined scenarios of autonomous vehicles, you should follow the following instructions.
1. Firstly, you should start the simulator's physics engine (same as before):

   `./CarlaUE4.sh -prefernvidia -renderOffScreen -quality-level=Low`

2. Then you should run `python manual_control.py` which has a very comprehensive world set up.
- remember that if you want to run the said script in *synchronous* mode, you should add **--sync** arguments, too.

   `python manual_control.py --sync`

3. Afterwards, run the desired scenario script file in another terminal.
- Scenario 1: Follow an arbitrary car
  
   `python test_scenario_1.py`

4. If you want some more traffic around, you can easily generate it by running `python generate_traffic.py -n [number_of_vehicles]`