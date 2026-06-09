#
# 3DE4.script.name: Point Position Copy
# 3DE4.script.addlabel: Point Position Paste
# 3DE4.script.version:	v1.2
# 3DE4.script.comment: Copies and pastes coordinates of exactly surveyed 3d point
#
# 3DE4.script.gui: Object Browser::Scripts
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#


import tde4


def call_error(text: str):
    tde4.postQuestionRequester("Error", text, "Ok")
    raise RuntimeError(text)


global POSITION_STORED

pgroup_id = tde4.getCurrentPGroup()
camera_id = tde4.getCurrentCamera()

points_list = tde4.getPointList(pgroup_id, 1)
if len(points_list) > 1:
    call_error('You have more than 1 point selected')
elif len(points_list) == 0:
    call_error('You have no points selected')

label = tde4.getLastScriptMenuLabel()

if label == 'Point Position Copy':
    if (tde4.getPointSurveyMode(pgroup_id, points_list[0]) == "SURVEY_EXACT"
            and tde4.getPointSurveyXYZEnabledFlags(pgroup_id, points_list[0]) == [1, 1, 1]):
        POSITION_STORED = tde4.getPointSurveyPosition3D(pgroup_id, points_list[0])
    else:
        POSITION_STORED = tde4.getPointCalcPosition3D(pgroup_id, points_list[0])

elif label == 'Point Position Paste':
    try:
        tde4.setPointSurveyPosition3D(pgroup_id, points_list[0], POSITION_STORED)
        tde4.setPointSurveyMode(pgroup_id, points_list[0], "SURVEY_EXACT")
        tde4.setPointSurveyXYZEnabledFlags(pgroup_id, points_list[0], 1, 1, 1)
    except NameError:
        call_error('You have no position stored')
