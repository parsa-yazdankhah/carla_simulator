# CARLA Simulator
To run the simulator, follow the instructions below:
1. Open a terminal in the source folder of simulator path
2. run `./CarlaUE4.sh` 
- Some options to improve performance are as follows:

   `./CarlaUE4.sh -prefernvidia -renderOffScreen -quality-level=Low`

3. Open a new terminal in the source of python script path
4. run `conda activate [carla_environment]`
- For example, if you have installed carla python package in an environment called *carla*, you should run `conda activate carla`
5. run `python test.py`
- Examples can be found in source folder under */PythonAPI/examples*
