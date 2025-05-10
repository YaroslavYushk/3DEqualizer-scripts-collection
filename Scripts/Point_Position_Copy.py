#
# 3DE4.script.name: Point Position Copy
# 3DE4.script.comment:	Copies coordinates of exactly surveyed 3d point
#
# 3DE4.script.gui:	Object Browser::Scripts
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#


import tde4


def call_error(text: str):
    tde4.postQuestionRequester("Error", text, "Ok")
    raise RuntimeError(text)


pgroup_id = tde4.getCurrentPGroup()
camera_id = tde4.getCurrentCamera()
global POSITION_STORED


points_list = tde4.getPointList(pgroup_id, 1)
if len(points_list) > 1:
    call_error('You have more than 1 point selected')
elif len(points_list) == 0:
    call_error('You have no points selected')

POSITION_STORED = tde4.getPointSurveyPosition3D(pgroup_id, points_list[0])
