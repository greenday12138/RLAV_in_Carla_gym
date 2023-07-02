"""Collection of Driving Scenario specs in CARLA
@Author: PP

Start/End locations can be specified as [X, Y, Z, Yaw] arrays, or [X, Y, Z] coordinates
where a default heading orientation along the direction of the road is used, or with node IDs.
Mapping between IDs and coordinates can be found in nodeid_coord_map.py
Specification compatible with CARLA v 0.8.x as well as v 0.9.x +
__author__:PP
"""

TEST_WEATHERS = [0, 2, 5, 7, 9, 10, 11, 12, 13]
TRAIN_WEATHERS = [1, 3, 4, 6, 8]

PAPER_TEST_WEATHERS = [1, 8, 5, 3]  # clear day, clear sunset, daytime rain, daytime after rain
PAPER_TRAIN_WEATHERS = [2, 14]  # cloudy daytime, soft rain at sunset

# the following road id sets define the chosen route on town05
ROADS = set()
DISTURB_ROADS = set()
FORWARD_ROADS = set()
BACKWARD_ROADS = set()
STRAIGHT = {12, 35, 36}
CURVE = {37, 38, 34}
JUNCTION = {2344, 2035}
DOUBLE_DIRECTION = {2358, 2363, 2039, 2052}
FORWARD_DOUBLE_DIRECTION = {2358, 2039}
BACKWARD_DOUBLE_DIRECTION = {2363, 2052}
# JUNCTION_LANE={33,85,141}
# JUNCTION_LANE_MINUS={102,109,150,163,46,67,128}
ROADS.update(STRAIGHT)
ROADS.update(CURVE)
ROADS.update(JUNCTION)
DISTURB_ROADS.update(DOUBLE_DIRECTION)
FORWARD_ROADS.update(FORWARD_DOUBLE_DIRECTION)
BACKWARD_ROADS.update(BACKWARD_DOUBLE_DIRECTION)

# builder functions for single and multi-agent scenarios
def build_scenario(map, start, end, vehicles, pedestrians, max_steps, weathers):
    scenario = {"map": map, "num_vehicles": vehicles, "num_pedestrians": pedestrians, "weather_distribution": weathers,
        "max_steps": max_steps, }
    if isinstance(start, list) and isinstance(end, list):
        scenario.update({"start_pos_loc": start, "end_pos_loc": end})
    elif isinstance(start, int) and isinstance(end, int):
        scenario.update({"start_pos_id": start, "end_pos_id": end})
    return scenario


def build_ma_scenario(map, actors, vehicles=0, pedestrians=0, max_steps=500, weathers=None):
    if weathers is None:
        weathers = [0]
    scenario = {"map": map, "actors": actors, "num_vehicles": vehicles, 
                "num_pedestrians": pedestrians, "weather_distribution": weathers, 
                "max_steps": max_steps, }
    return scenario


class Scenarios(object):

    # Multi Agent Scenarios

    """Stop Sign Urban Intersection scenario with 3 Cars passing through.
    """
    FR2C_TOWN5 = {
        "map": "Town05",
        "actors": {
            "car1": {
                "start": -1.0,
                "end": -1
            },
            "car2": {
                "start": -2.0,
                "end": -1
            }
        },
        "num_vehicles": 20,
        "num_pedestrians": 0,
        "weather_distribution": [0],
        "max_steps": 2000
    }

    SSUI3C_TOWN3 = {
        "map": "Town03",
        "actors": {
            "car1": {
                "start": [170.5, 80, 0.4],
                "end": [144, 59, 0]
            },
            "car2": {
                "start": [188, 59, 0.4],
                "end": [167, 75.7, 0.13],
            },
            "car3": {
                "start": [147.6, 62.6, 0.4],
                "end": [191.2, 62.7, 0],
            }
        },
        "weather_distribution": [0],
        "max_steps": 500
    }
    SSUI1B2C1P_TOWN3 = {
        "map": "Town03",
        "actors": {
            "car1": {
                "start": [170.5, 80, 0.4],
                "end": [144, 59, 0]
            },
            "car2": {
                "start": [188, 59, 0.4],
                "end": [167, 75.7, 0.13],
            },
            "pedestrian1": {
                "start": [158, 75, 0.4],
                "end": [185, 71, 0],
            },
            "bike1": {
                "start": [147.6, 62.6, 0.4],
                "end": [191.2, 62.7, 0],
            },
        },
        "weather_distribution": [0],
        "max_steps": 500
    }

    """Signalized (traffic light) Urban Intersection scenario with 3 Cars passing through.
    CAR1: Starts almost inside the intersection, goes straight
    CAR2: Starts 90 wrt CAR1 close to intersection, turns right to merge
    CAR3: Starts behind CAR1 away from intersection, goes straight
    """
    SUI3C_TOWN3 = {
        "map": "Town03",
        "actors": {
            "car1": {
                "start": [70, -132.8, 8],
                "end": [127, -132, 8]
            },
            "car2": {
                "start": [84.3, -118, 9],
                "end": [120, -132, 8]
            },
            "car3": {
                "start": [43, -133, 4],
                "end": [100, -132, 8],
            }
        },
        "weather_distribution": [0],
        "max_steps": 500
    }
    SUI1B2C1P_TOWN3 = {
        "map": "Town03",
        "actors": {
            "car1": {
                "start": [94, -132.7, 10],
                "end": [106, -132.7, 8],
            },
            "car2": {
                "start": [84, -115, 10],
                "end": [41, -137, 8],
            },
            "pedestrian1": {
                "start": [74, -126, 10, 0.0],
                "end": [92, -125, 8],
            },
            "bike1": {
                "start": [69, -132, 8],
                "end": [104, -132, 8],
            }
        },
        "weather_distribution": [0],
        "max_steps": 200
    }

    # Simple scenario for Town01 that involves driving down a road
    DEFAULT_SCENARIO_TOWN1 = build_ma_scenario(
        map="Town01",
        actors={"vehicle1": {
            "start": 128,
            "end": 133
        }},
        max_steps=2000,
        weathers=[0])

    DEFAULT_SCENARIO_TOWN1_2 = build_ma_scenario(
        map="Town01",
        actors={"vehicle1": {
            "start": 133,
            "end": 65
        }},
        max_steps=2000,
        weathers=[0])

    DEFAULT_SCENARIO_TOWN1_COMBINED = build_ma_scenario(
        map="Town01",
        actors={
            "vehicle1": {
                "start": [217.50997924804688, 198.75999450683594, 0.50, -0.16],
                "end": [299.39996337890625, 199.05999755859375, 0.50, -0.16]
            },
            "vehicle2": {
                "start": 133,
                "end": 65
            }
        },
        max_steps=2000,
        vehicles=10,
        pedestrians=10,
        weathers=[0])

    DEFAULT_SCENARIO_TOWN1_COMBINED_WITH_MANUAL = build_ma_scenario(
        map="Town01",
        actors={
            "vehicle1": {
                "start": [
                    217.50997924804688, 198.75999450683594, 39.430625915527344,
                    -0.16
                ],
                "end": [
                    299.39996337890625, 199.05999755859375, 39.430625915527344,
                    -0.16
                ]
            },
            "vehicle2": {
                "start": 133,
                "end": 65
            },
            "manual": {
                "start": [
                    299.39996337890625, 194.75999450683594, 39.430625915527344,
                    180.0
                ],
                "end": [
                    217.50997924804688, 194.05999755859375, 39.430625915527344,
                    180.0
                ]
            },
        },
        max_steps=2000,
        weathers=[0])

    DEFAULT_SCENARIO_TOWN2 = build_scenario(
        map="Town01",
        start=[47],
        end=[52],
        vehicles=20,
        pedestrians=40,
        max_steps=200,
        weathers=[0])

    DEFAULT_CURVE_TOWN1 = build_scenario(
        map="Town01",
        start=[133],
        end=[150],
        vehicles=20,
        pedestrians=40,
        max_steps=200,
        weathers=[0])

    # Simple scenario for Town02 that involves driving down a road
    LANE_KEEP_TOWN2 = build_scenario(
        map="Town02",
        start=36,
        end=40,
        vehicles=0,
        pedestrians=0,
        max_steps=2000,
        weathers=[0])

    # Simple scenario for Town01 that involves driving down a road
    LANE_KEEP_TOWN1 = build_scenario(
        map="Town01",
        start=36,
        end=40,
        vehicles=0,
        pedestrians=0,
        max_steps=2000,
        weathers=[0])

    CURVE_TOWN1 = build_scenario(
        map="Town01",
        start=[131, 133],
        end=[65, 64],
        vehicles=0,
        pedestrians=0,
        max_steps=2000,
        weathers=[0])

    CURVE_TOWN2 = build_scenario(
        map="Town01",
        start=[16, 27],
        end=[74, 75],
        vehicles=0,
        pedestrians=0,
        max_steps=2000,
        weathers=[0])

    # Scenarios from the CoRL2017 paper
    POSES_TOWN1_STRAIGHT = [
        [[9, 8], [1, 0]], [[142, 148], [141, 147]],
        [[114, 115], [110, 111]], [[7, 6], [3, 2]],
        [[4, 5], [149, 150]]]
    # POSES_TOWN1_STRAIGHT = [
    #    [36, 40], [39, 35], [110, 114], [7, 3], [0, 4],
    #    [68, 50], [61, 59], [47, 64], [147, 90], [33, 87],
    #    [26, 19], [80, 76], [45, 49], [55, 44], [29, 107],
    #    [95, 104], [84, 34], [53, 67], [22, 17], [91, 148],
    #    [20, 107], [78, 70], [95, 102], [68, 44], [45, 69]]

    POSES_TOWN1_ONE_CURVE = [[138, 17], [47, 16], [26, 9], [42, 49], [140, 124],
                             [85, 98], [65, 133], [137, 51], [76, 66], [46, 39],
                             [40, 60], [0, 29], [4, 129], [121, 140], [2, 129],
                             [78, 44], [68, 85], [41, 102], [95, 70], [68, 129],
                             [84, 69], [47, 79], [110, 15], [130, 17], [0, 17]]

    POSES_TOWN1_NAV = [[105, 29], [27, 130], [102, 87], [132, 27], [24, 44],
                       [96, 26], [34, 67], [28, 1], [140, 134], [105, 9],
                       [148, 129], [65, 18], [21, 16], [147, 97], [42, 51],
                       [30, 41], [18, 107], [69, 45], [102, 95], [18, 145],
                       [111, 64], [79, 45], [84, 69], [73, 31], [37, 81]]

    POSES_TOWN2_STRAIGHT = [[38, 34], [4, 2], [12, 10], [62, 55], [43, 47],
                            [64, 66], [78, 76], [59, 57], [61, 18], [35, 39],
                            [12, 8], [0, 18], [75, 68], [54, 60], [45, 49],
                            [46, 42], [53, 46], [80, 29], [65, 63], [0, 81],
                            [54, 63], [51, 42], [16, 19], [17, 26], [77, 68]]

    POSES_TOWN2_ONE_CURVE = [[37, 76], [8, 24], [60, 69], [38, 10], [21, 1],
                             [58, 71], [74, 32], [44, 0], [71, 16], [14, 24],
                             [34, 11], [43, 14], [75, 16], [80, 21], [3, 23],
                             [75, 59], [50, 47], [11, 19], [77, 34], [79, 25],
                             [40, 63], [58, 76], [79, 55], [16, 61], [27, 11]]

    POSES_TOWN2_NAV = [[19, 66], [79, 14], [19, 57], [23, 1], [53, 76], [42, 13],
                       [31, 71], [33, 5], [54, 30], [10, 61], [66, 3], [27, 12],
                       [79, 19], [2, 29], [16, 14], [5, 57], [70, 73], [46, 67],
                       [57, 50], [61, 49], [21, 12], [51, 81], [77, 68], [56, 65],
                       [43, 54]]

    TOWN1_STRAIGHT = [
        build_scenario("Town01", start, end, 0, 0, 300, TEST_WEATHERS)
        for (start, end) in POSES_TOWN1_STRAIGHT
    ]

    TOWN1_ONE_CURVE = [
        build_scenario("Town01", start, end, 0, 0, 600, TEST_WEATHERS)
        for (start, end) in POSES_TOWN1_ONE_CURVE
    ]

    TOWN1_NAVIGATION = [
        build_scenario("Town01", start, end, 0, 0, 900, TEST_WEATHERS)
        for (start, end) in POSES_TOWN1_NAV
    ]

    TOWN1_NAVIGATION_DYNAMIC = [
        build_scenario("Town01", start, end, 20, 50, 900, TEST_WEATHERS)
        for (start, end) in POSES_TOWN1_NAV
    ]

    TOWN2_STRAIGHT = [
        build_scenario("Town02", start, end, 0, 0, 300, TRAIN_WEATHERS)
        for (start, end) in POSES_TOWN2_STRAIGHT
    ]

    TOWN2_STRAIGHT_DYNAMIC = [
        build_scenario("Town02", start, end, 20, 50, 300, TRAIN_WEATHERS)
        for (start, end) in POSES_TOWN2_STRAIGHT
    ]

    TOWN2_ONE_CURVE = [
        build_scenario("Town02", start, end, 0, 0, 600, TRAIN_WEATHERS)
        for (start, end) in POSES_TOWN2_ONE_CURVE
    ]

    TOWN2_NAVIGATION = [
        build_scenario("Town02", start, end, 0, 0, 900, TRAIN_WEATHERS)
        for (start, end) in POSES_TOWN2_NAV
    ]

    TOWN2_NAVIGATION_DYNAMIC = [
        build_scenario("Town02", start, end, 20, 50, 900, TRAIN_WEATHERS)
        for (start, end) in POSES_TOWN2_NAV
    ]

    TOWN1_ALL = (TOWN1_STRAIGHT + TOWN1_ONE_CURVE + TOWN1_NAVIGATION +
                 TOWN1_NAVIGATION_DYNAMIC)

    TOWN2_ALL = (TOWN2_STRAIGHT + TOWN2_ONE_CURVE + TOWN2_NAVIGATION +
                 TOWN2_NAVIGATION_DYNAMIC)

    local_map = locals()

    @classmethod
    def resolve_scenarios_parameter(cls, scenarios_parameter):
        scenario_map = []
        if isinstance(scenarios_parameter, dict):
            scenario_map = scenarios_parameter
        elif isinstance(scenarios_parameter, list):
            for scenario_name in scenarios_parameter:
                scenario_map.append(cls.get_scenario_parameter(scenario_name))
        elif isinstance(scenarios_parameter, str):
            scenario_map = cls.get_scenario_parameter(scenarios_parameter)
        return scenario_map

    @classmethod
    def get_scenario_parameter(cls, scenario_name):
        if scenario_name in cls.local_map:
            return cls.local_map[scenario_name]
        else:
            return scenario_name

# To extend the Scenarios class
# class NewScenarios(Scenarios):
#     NEW = ...
#     local_map = locals()
