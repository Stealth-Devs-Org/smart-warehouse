import os
import sys
import unittest

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_root)
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the project_root to sys.path
sys.path.append(project_root)

import server.agv.col_avoid as col_avoid
import server.agv.utils as utils

agvs_data = {
    "agv1": {
        "agv_id": "agv1",
        "location": [1, 2],
        "segment": [[1, 2], [1, 3], [1, 4]],
        "status": 1,
        "timestamp": "2023-10-01T12:34:56Z",
    },
    "agv2": {
        "agv_id": "agv2",
        "location": [5, 3],
        "segment": [[5, 3], [4, 3], [3, 3], [2, 3], [1, 3]],
        "status": 1,
        "timestamp": "2023-10-01T12:34:56Z",
    },
    "agv3": {
        "agv_id": "agv3",
        "location": [1, 4],
        "segment": [[1, 4], [2, 4], [3, 4]],
        "status": 1,
        "timestamp": "2023-10-01T12:34:56Z",
    },
    "agv4": {
        "agv_id": "agv4",
        "location": [4, 5],
        "segment": [[4, 5], [4, 6], [4, 7]],
        "status": 1,
        "timestamp": "2023-10-01T12:34:56Z",
    },
}


class TestColAvoid(unittest.TestCase):

    def test_get_agv_locations_array(self):
        set1 = set(tuple(x) for x in col_avoid.get_agv_locations_array(agvs_data))
        set2 = set(tuple(x) for x in [[1, 2], [5, 3], [1, 4], [4, 5]])
        self.assertEqual(set1, set2)

    def test_find_obstacles_in_segment(self):
        set1 = set(
            tuple(x)
            for x in col_avoid.find_obstacles_in_segment(
                agvs_data, "agv1", [[1, 2], [1, 3], [1, 4]]
            )
        )
        set2 = set(
            tuple(x)
            for x in [[0, 3], [0, 4], [0, 5], [1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [2, 5]]
        )
        self.assertEqual(set1, set2)

    def test_stop_agv(self):
        pass

    def test_recalibrate_path(self):
        pass

    def test_collision_avoidance(self):
        pass

    def test_update_agv_location(self):
        pass


class TestUtils(unittest.TestCase):

    def test_get_buffered_positions(self):
        set1 = set(tuple(x) for x in utils.get_buffered_positions(1, [[1, 2], [3, 4]]))
        set2 = set(
            tuple(x)
            for x in [
                [0, 1],
                [0, 2],
                [0, 3],
                [2, 1],
                [2, 2],
                [2, 3],
                [1, 1],
                [1, 2],
                [1, 3],
                [3, 3],
                [3, 4],
                [3, 5],
                [2, 4],
                [2, 5],
                [4, 3],
                [4, 4],
                [4, 5],
            ]
        )
        self.assertEqual(set1, set2)

    def test_calculate_distance(self):
        self.assertEqual(utils.calculate_distance([1, 2], [1, 3]), 1.0)

    def test_calculate_agv_distances(self):
        self.assertEqual(
            utils.calculate_agv_distances(agvs_data),
            {
                ("agv1", "agv2"): 4.123105625617661,
                ("agv1", "agv3"): 2.0,
                ("agv1", "agv4"): 4.242640687119285,
                ("agv2", "agv3"): 4.123105625617661,
                ("agv2", "agv4"): 2.23606797749979,
                ("agv3", "agv4"): 3.1622776601683795,
            },
        )

    def test_get_close_agv_pairs(self):
        self.assertEqual(
            utils.get_close_agv_pairs(agvs_data, 3), [("agv1", "agv3"), ("agv2", "agv4")]
        )


if __name__ == "__main__":
    unittest.main()
