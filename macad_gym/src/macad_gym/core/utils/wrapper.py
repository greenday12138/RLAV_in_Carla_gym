import math
import carla
import numpy as np
from enum import Enum
from macad_gym.core.controllers.route_planner import RoadOption
from macad_gym.core.utils.misc import get_speed,get_yaw_diff,test_waypoint,get_sign

# Carla planner commands
COMMANDS_ENUM = {
    0.0: "REACH_GOAL",
    5.0: "GO_STRAIGHT",
    4.0: "TURN_RIGHT",
    3.0: "TURN_LEFT",
    2.0: "LANE_FOLLOW",
}

# Mapping from string repr to one-hot encoding index to feed to the model
COMMAND_ORDINAL = {
    "REACH_GOAL": 0,
    "GO_STRAIGHT": 1,
    "TURN_RIGHT": 2,
    "TURN_LEFT": 3,
    "LANE_FOLLOW": 4,
}

ROAD_OPTION_TO_COMMANDS_MAPPING = {
    RoadOption.VOID: "REACH_GOAL",
    RoadOption.STRAIGHT: "GO_STRAIGHT",
    RoadOption.RIGHT: "TURN_RIGHT",
    RoadOption.LEFT: "TURN_LEFT",
    RoadOption.LANEFOLLOW: "LANE_FOLLOW",
}

# Threshold to determine that the goal has been reached based on distance
DISTANCE_TO_GOAL_THRESHOLD = 0.5

# Threshold to determine that the goal has been reached based on orientation
ORIENTATION_TO_GOAL_THRESHOLD = math.pi / 4.0

# Number of retries if the server doesn't respond
RETRIES_ON_ERROR = 2

# Dummy Z coordinate to use when we only care about (x, y)
GROUND_Z = 22

DISCRETE_ACTIONS = {
    # coast
    0: [0.0, 0.0],
    # turn left
    1: [0.0, -0.5],
    # turn right
    2: [0.0, 0.5],
    # forward
    3: [1.0, 0.0],
    # brake
    4: [-0.5, 0.0],
    # forward left
    5: [0.5, -0.05],
    # forward right
    6: [0.5, 0.05],
    # brake left
    7: [-0.5, -0.5],
    # brake right
    8: [-0.5, 0.5],
}

WEATHERS = {
    0: carla.WeatherParameters.ClearNoon,
    1: carla.WeatherParameters.CloudyNoon,
    2: carla.WeatherParameters.WetNoon,
    3: carla.WeatherParameters.WetCloudyNoon,
    4: carla.WeatherParameters.MidRainyNoon,
    5: carla.WeatherParameters.HardRainNoon,
    6: carla.WeatherParameters.SoftRainNoon,
    7: carla.WeatherParameters.ClearSunset,
    8: carla.WeatherParameters.CloudySunset,
    9: carla.WeatherParameters.WetSunset,
    10: carla.WeatherParameters.WetCloudySunset,
    11: carla.WeatherParameters.MidRainSunset,
    12: carla.WeatherParameters.HardRainSunset,
    13: carla.WeatherParameters.SoftRainSunset,
}


class WaypointWrapper:
    """The location left, right, center is allocated according to the lane of ego vehicle"""
    def __init__(self,opt=None) -> None:
        self.left_front_wps=None
        self.left_rear_wps=None
        self.center_front_wps=None
        self.center_rear_wps=None
        self.right_front_wps=None
        self.right_rear_wps=None

        if opt is not None:
            if 'left_front_wps' in opt:
                self.left_front_wps=opt['left_front_wps']
            if 'left_rear_wps' in opt:
                self.left_rear_wps=opt['left_rear_wps']
            if 'center_front_wps' in opt:
                self.center_front_wps=opt['center_front_wps']
            if 'center_rear_wps' in opt:
                self.center_rear_wps=opt['center_rear_wps']
            if 'right_front_wps' in opt:
                self.right_front_wps=opt['right_front_wps']
            if 'right_rear_wps' in opt:
                self.right_rear_wps=opt['right_rear_wps']


class VehicleWrapper:
    """The location left, right, center is allocated according to the lane of ego vehicle"""
    def __init__(self,opt=None) -> None:
        self.left_front_veh=None
        self.left_rear_veh=None
        self.center_front_veh=None
        self.center_rear_veh=None
        self.right_front_veh=None
        self.right_rear_veh=None
        """distance sequence:
        distance_to_front_vehicles:[left_front_veh,center_front_veh,right_front_veh]
        distance_to_rear_vehicles:[left_rear_veh,center_rear_veh,right_rear_veh]"""
        self.distance_to_front_vehicles=None
        self.distance_to_rear_vehicles=None

        if opt is not None:
            if 'left_front_veh' in opt:
                self.left_front_veh=opt['left_front_veh']
            if 'left_rear_veh' in opt:
                self.left_rear_veh=opt['left_rear_veh']
            if 'center_front_veh' in opt:
                self.center_front_veh=opt['center_front_veh']
            if 'center_rear_veh' in opt:
                self.center_rear_veh=opt['center_rear_veh']
            if 'right_front_veh' in opt:
                self.right_front_veh=opt['right_front_veh']
            if 'right_rear_veh' in opt:
                self.right_rear_veh=opt['right_rear_veh']
            if 'dis_to_front_vehs' in opt:
                self.distance_to_front_vehicles=opt['dis_to_front_vehs']
            if 'dis_to_rear_vehs' in opt:
                self.distance_to_rear_vehicles=opt['dis_to_rear_vehs']

class Truncated(Enum):
    """Different truncate situations"""
    FALSE=-1
    OTHER=0
    CHANGE_LANE_IN_LANE_FOLLOW=1
    COLLISION=2
    SPEED_LOW=3
    OUT_OF_ROAD=4
    OPPOSITE_DIRECTION=5
    TRAFFIC_LIGHT_BREAK=6
    CHANGE_TO_WRONG_LANE=7

class SpeedState(Enum):
    """Different ego vehicle speed state
        START: Initializing state, speed up the vehicle to speed_threshole, use basic agent controller
        RUNNING: After initializing, ego speed between speed_min and speed_limit, use RL controller
        REBOOT: After initializaing, ego speed reaches below speed min, use basic agent controller to speed up ego vehicle to speed_threshold
    """
    START = 0
    RUNNING = 1
    RUNNING_RL = 2
    RUNNING_PID = 3

class Action(Enum):
    """Parametrized Action for P-DQN"""
    LANE_FOLLOW=0
    LANE_CHANGE_LEFT=-1
    LANE_CHANGE_RIGHT=1
    STOP=2

class ControlInfo:
    """Wrapper for vehicle(model3) control info"""
    def __init__(self,throttle=0.0,brake=0.0,steer=0.0,gear=1) -> None:
        self.throttle=throttle
        self.steer=steer
        self.brake=brake
        self.gear=gear
        self.reverse=False
        self.manual_gear_shift=False

def process_lane_wp(wps_list, ego_vehicle_z, ego_forward_vector, my_sample_ratio, lane_offset):
    wps = []
    idx = 0

    # for wp in wps_list:
    #     delta_z = wp.transform.location.z - ego_vehicle_z
    #     yaw_diff = math.degrees(get_yaw_diff(wp.transform.get_forward_vector(), ego_forward_vector))
    #     yaw_diff = yaw_diff / 90
    #     if idx % my_sample_ratio == my_sample_ratio-1:
    #         wps.append([delta_z/2, yaw_diff, lane_offset])
    #     idx = idx + 1
    # return np.array(wps)
    for i in range(10):
        wp = wps_list[i]
        delta_z = wp.transform.location.z - ego_vehicle_z
        yaw_diff = math.degrees(get_yaw_diff(wp.transform.get_forward_vector(), ego_forward_vector))
        yaw_diff = yaw_diff / 90
        wps.append([delta_z/3, yaw_diff, lane_offset])
    return np.array(wps)


def process_veh(ego_vehicle, vehs_info, left_wall, right_wall,vehicle_proximity):
    vehicle_inlane=[vehs_info.left_front_veh,vehs_info.center_front_veh,vehs_info.right_front_veh,
            vehs_info.left_rear_veh,vehs_info.center_rear_veh,vehs_info.right_rear_veh]
    ego_speed = get_speed(ego_vehicle, False)
    ego_location = ego_vehicle.get_location()
    ego_bounding_x = ego_vehicle.bounding_box.extent.x
    ego_bounding_y = ego_vehicle.bounding_box.extent.y
    all_v_info = []
    print('vehicle_inlane: ', vehicle_inlane)
    for i in range(6):
        if i == 0 or i == 3:
            lane = -1
        elif i == 1 or i == 4:
            lane = 0
        else:
            lane = 1
        veh = vehicle_inlane[i]
        wall = False
        if left_wall and (i == 0 or i == 3):
            wall = True
        if right_wall and (i == 2 or i == 5):
            wall = True
        if wall:
            if i < 3:
                v_info = [0.001, 0, lane]
            else:
                v_info = [-0.001, 0, lane]
        else:
            if veh is None:
                if i < 3:
                    v_info = [1, 0, lane]
                else:
                    v_info = [-1, 0, lane]
            else:
                veh_speed = get_speed(veh, False)
                rel_speed = ego_speed - veh_speed

                distance = ego_location.distance(veh.get_location())
                vehicle_len = max(abs(ego_bounding_x), abs(ego_bounding_y)) + \
                    max(abs(veh.bounding_box.extent.x), abs(veh.bounding_box.extent.y))
                distance -= vehicle_len

                if distance < 0:
                    if i < 3:
                        v_info = [0.001, rel_speed, lane]
                    else:
                        v_info = [-0.001, -rel_speed, lane]
                else:
                    if i < 3:
                        v_info = [distance / vehicle_proximity, rel_speed, lane]
                    else:
                        v_info = [-distance / vehicle_proximity, -rel_speed, lane]
        all_v_info.append(v_info)
    # print(all_v_info)
    return np.array(all_v_info)

def process_steer(a_index, steer):
    # left: steering is negative[-1, -0.1], right: steering is positive[0.1, 1], the thereshold here is sifnificant and it correlates with pdqn
    processed_steer = steer
    if a_index == 0:
        processed_steer = steer * 0.5 - 0.5
    elif a_index == 2:
        processed_steer = steer * 0.5 + 0.5
    return processed_steer

def recover_steer(a_index, steer):
    # recovery [-1, 1] from left change and right change
    recovered_steer=steer
    if a_index==0:
        recovered_steer=(steer+0.5)/0.5
    elif a_index ==2:
        recovered_steer=(steer-0.5)/0.5
    recovered_steer=np.clip(recovered_steer,-1,1)
    return recovered_steer

def fill_action_param(action, steer, throttle_brake, action_param, modify_change_steer):
    if not modify_change_steer:
        action_param[0][action*2] = steer
        action_param[0][action*2+1] = throttle_brake
    else:
        if action == 0:
            steer=recover_steer(action,steer)
        elif action == 2:
            steer=recover_steer(action,steer)
        action_param[0][action*2] = steer
        action_param[0][action*2+1] = throttle_brake
    return action_param