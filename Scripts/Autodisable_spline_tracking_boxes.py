#
# 3DE4.script.name:  Autodisable spline tracking boxes
# 3DE4.script.version:  v1.0
# 3DE4.script.comment:  Auto-disables spline tracking boxes on newly created points
#
# 3DE4.script.startup:  true
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#

import tde4


def set_point_spline_box(requester, point_id):
    pgroup_id = tde4.getCurrentPGroup()
    if pgroup_id == 0:
        return
    tde4.setPointSplineBoxesFlag(pgroup_id, point_id, 0)
    return


if __name__ == "__main__":
    tde4.setCreateNewPointCallbackFunction("set_point_spline_box")
