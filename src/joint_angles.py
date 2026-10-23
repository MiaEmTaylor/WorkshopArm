# ------- JOINT ANGLE MATH -------------------------------------------------
# Pure math, no camera, no OpenCV. Takes marker centers, returns angles.
#
# Marker chain: J0 base -> J1 shoulder -> J2 elbow -> J3 wrist.
# Only shoulder and elbow are actuated (servos); wrist has none.
#
# A joint's angle is measured between the segment coming into it and the
# segment going out of it (dot-product method). 0 degrees means the two
# segments point the same way (arm straight through that joint); larger
# values mean more bend. J3 is the last marker in the chain, so there is
# no segment past it to measure a bend against by this method.

from typing import Dict, Optional, Tuple

import numpy as np

Point = Tuple[float, float]


def _angle_between(v_in: Point, v_out: Point) -> Optional[float]:
    v_in = np.asarray(v_in, dtype=float)
    v_out = np.asarray(v_out, dtype=float)
    norm_in = np.linalg.norm(v_in)
    norm_out = np.linalg.norm(v_out)
    if norm_in == 0 or norm_out == 0:
        return None
    cos_theta = np.dot(v_in, v_out) / (norm_in * norm_out)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))


def calculate_joint_angles(centers: Dict[int, Point]) -> Dict[str, Optional[float]]:
    """centers: marker_id (0-3) -> (x, y) pixel center.

    Returns {"shoulder": degrees or None, "elbow": degrees or None}.
    A joint is None whenever any marker its calculation needs is not in
    `centers` - never guessed, never interpolated.
    """
    angles: Dict[str, Optional[float]] = {"shoulder": None, "elbow": None}

    j0, j1, j2, j3 = centers.get(0), centers.get(1), centers.get(2), centers.get(3)

    if j0 is not None and j1 is not None and j2 is not None:
        v_in = (j1[0] - j0[0], j1[1] - j0[1])
        v_out = (j2[0] - j1[0], j2[1] - j1[1])
        angles["shoulder"] = _angle_between(v_in, v_out)

    if j1 is not None and j2 is not None and j3 is not None:
        v_in = (j2[0] - j1[0], j2[1] - j1[1])
        v_out = (j3[0] - j2[0], j3[1] - j2[1])
        angles["elbow"] = _angle_between(v_in, v_out)

    return angles
