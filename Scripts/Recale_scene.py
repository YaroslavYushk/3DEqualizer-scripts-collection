#
# 3DE4.script.name: Rescale 3d scene
# 3DE4.script.version:	v1.3.1
# 3DE4.script.comment:	Scales the whole scene based on your reference model
#
# 3DE4.script.gui:	Orientation Controls::Scripts
# 3DE4.script.gui:	Lineup Controls::Scripts
# 3DE4.script.gui.config_menus:	true
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#


import tde4
from vl_sdv import *
from vl_sdv import mat3d, vec3d, rot3d, VL_APPLY_ZXY


def get_model_rotation_scale(model):
    pg = tde4.getCurrentPGroup()
    matrices = []
    rot_scale_matrix = mat3d(tde4.get3DModelRotationScale3D(pg, model)).trans()
    scale_values_from_matrix = vec3d(
        rot_scale_matrix[0].norm2(),
        rot_scale_matrix[1].norm2(),
        rot_scale_matrix[2].norm2())
    scale_matrix = mat3d(
        scale_values_from_matrix[0], 0.0, 0.0,
        0.0, scale_values_from_matrix[1], 0.0,
        0.0, 0.0, scale_values_from_matrix[2])
    rotation_matrix = mat3d(
        rot_scale_matrix[0].unit(),
        rot_scale_matrix[1].unit(),
        rot_scale_matrix[2].unit()
    ).trans()
    matrices.append(rotation_matrix)
    matrices.append(scale_matrix)
    return matrices


def set_model_scale(models, scale):
    pg = tde4.getCurrentPGroup()
    if models:
        for model in models:
            scale_matrix = get_model_rotation_scale(model)[1]
            rotation_matrix = get_model_rotation_scale(model)[0]
            scale_matrix = mat3d(
                float(scale), 0.0, 0.0,
                0.0, float(scale), 0.0,
                0.0, 0.0, float(scale))
            final_matrix = rotation_matrix * scale_matrix
            tde4.set3DModelRotationScale3D(pg, model, final_matrix.list())


def upscale_model(models, upscale):
    pg = tde4.getCurrentPGroup()
    if models:
        for model in models:
            scale_matrix = get_model_rotation_scale(model)[1] * upscale
            rotation_matrix = get_model_rotation_scale(model)[0]
            scale_matrix = mat3d(
                float(scale_matrix[0][0]), 0.0, 0.0,
                0.0, float(scale_matrix[1][1]), 0.0,
                0.0, 0.0, float(scale_matrix[2][2]))
            final_matrix = rotation_matrix * scale_matrix
            tde4.set3DModelRotationScale3D(pg, model, final_matrix.list())


def reposition_model(models, pivot, upscale):
    pg = tde4.getCurrentPGroup()
    cam = tde4.getCurrentCamera()
    frame = tde4.getCurrentFrame(cam)
    for model in models:
        new_coordinates = [
            (pos - piv) * upscale + piv
            for pos, piv in zip(
                tde4.get3DModelPosition3D(pg, model, cam, frame), pivot)
        ]
        tde4.set3DModelPosition3D(pg, model, new_coordinates)


def scale_points(pivot_coord, upscale):
    pg = tde4.getCurrentPGroup()
    points_list = tde4.getPointList(pg, 0)
    for p in points_list:
        smode = tde4.getPointSurveyMode(pg, p)
        if smode in ("SURVEY_EXACT", "SURVEY_APPROX", "SURVEY_LINEUP"):
            p3d_orig = vec3d(tde4.getPointSurveyPosition3D(pg, p))
            p3d = (rot3d(0, 0, 0, VL_APPLY_ZXY)
                   * (mat3d(upscale, 0, 0,
                            0, upscale, 0,
                            0, 0, upscale)
                      * (p3d_orig - pivot_coord))
                   + pivot_coord)
            tde4.setPointSurveyPosition3D(pg, p, p3d.x)
        p3d_orig = vec3d(tde4.getPointCalcPosition3D(pg, p))
        p3d = (rot3d(0, 0, 0, VL_APPLY_ZXY)
               * (mat3d(upscale, 0, 0,
                        0, upscale, 0,
                        0, 0, upscale)
                  * (p3d_orig - pivot_coord))
               + pivot_coord)
        tde4.setPointCalcPosition3D(pg, p, p3d.x)


def scale_camera_path(pivot_coord, upscale):
    pg = tde4.getCurrentPGroup()
    cam = tde4.getCurrentCamera()
    for i_frame in range(tde4.getCameraNoFrames(cam)):
        frame = i_frame + 1
        print('entering %s frame' % frame)
        # Bake rotation from filtered curve to keyframes
        tde4.setPGroupRotation3D(
            pg, cam, frame, tde4.getPGroupRotation3D(pg, cam, frame))
        # Change camera position
        pos_vec_scaled = []
        pos_vec = tde4.getPGroupPosition3D(pg, cam, frame)
        for pv, pc in zip(pos_vec, pivot_coord):
            pos_vec_scaled.append((pv - pc) * upscale + pc)
        tde4.setPGroupPosition3D(pg, cam, frame, pos_vec_scaled)
    # Bake pos and rot curves to filtered curve
    tde4.copyPGroupEditCurvesToFilteredCurves(pg, cam)


def rsclr_get_ref_model(requester, widget, action):
    global PIVOT_COORD
    global REF_MODEL_ID
    global PIVOT_MODE

    pg = tde4.getCurrentPGroup()
    cam = tde4.getCurrentCamera()
    frame = tde4.getCurrentFrame(cam)

    if (cam is None) or (pg is None):
        tde4.postQuestionRequester(
            "Rescale scene", "There is no current Point Group or Camera.", "Ok")
        return
    if tde4.getCameraPath(cam) == '':
        tde4.postQuestionRequester(
            "Rescale scene", "You need to load footage in camera", "Ok")
        return

    models_list = tde4.get3DModelList(pg, 1)
    if not models_list:
        tde4.postQuestionRequester(
            "Rescale scene", "No 3d models selected", "Ok")
        return
    elif len(models_list) > 1:
        tde4.postQuestionRequester(
            "Rescale scene",
            "Looks like more than one 3d model selected",
            "Ok")
        return
    else:
        if tde4.get3DModelSurveyFlag(pg, models_list[0]) == 1:
            tde4.postQuestionRequester(
                "Rescale scene",
                'Model Contains Survey Data" checkbox was unckecked for your model',
                "Ok")
            tde4.set3DModelSurveyFlag(pg, models_list[0], 0)
        REF_MODEL_ID = models_list[0]
        tde4.setWidgetSensitiveFlag(requester, "Ref_model_scale", 1)
        tde4.setWidgetSensitiveFlag(requester, "Manual_ref_model_scale", 1)
        tde4.setWidgetSensitiveFlag(requester, "Pivot_point_choose", 1)

    tde4.setWidgetValue(
        requester, "Ref_model_name", tde4.get3DModelName(pg, REF_MODEL_ID))
    PIVOT_MODE = tde4.getWidgetValue(requester, "Pivot_point_choose")
    if PIVOT_MODE == 2:
        PIVOT_COORD = tde4.get3DModelPosition3D(pg, REF_MODEL_ID, cam, frame)
        pivot_coord_round = [round(r, 4) for r in PIVOT_COORD]
        tde4.setWidgetValue(
            requester,
            "Pivot_point_coordinate",
            ' '.join(map(str, pivot_coord_round)))
    return


def rsclr_scale_ref_model(requester, widget, action):
    global REF_SCALE
    global UPSCALE
    REF_SCALE = tde4.getWidgetValue(requester, "Ref_model_scale")
    tde4.setWidgetValue(
        requester, "Manual_ref_model_scale", str(round(REF_SCALE, 4)))
    set_model_scale([REF_MODEL_ID], REF_SCALE)
    UPSCALE = 1 / REF_SCALE
    return


def rsclr_manual_scale_ref_model(requester, widget, action):
    global REF_SCALE
    global UPSCALE
    REF_SCALE = float(tde4.getWidgetValue(requester, "Manual_ref_model_scale"))
    tde4.setWidgetValue(
        requester, "Ref_model_scale", str(round(REF_SCALE, 4)))
    set_model_scale([REF_MODEL_ID], REF_SCALE)
    UPSCALE = 1 / REF_SCALE
    return


def rsclr_choose_pivot(requester, widget, action):
    global REF_MODEL_ID
    global PIVOT_MODE
    global PIVOT_COORD
    cam = tde4.getCurrentCamera()
    pg = tde4.getCurrentPGroup()
    frame = tde4.getCurrentFrame(cam)

    if (cam is None) or (pg is None):
        tde4.postQuestionRequester(
            "Rescale scene", "There is no current Point Group or Camera.", "Ok")
        return
    if tde4.getCameraPath(cam) == '':
        tde4.postQuestionRequester(
            "Rescale scene", "You need to load footage in camera", "Ok")
        return

    PIVOT_MODE = tde4.getWidgetValue(requester, "Pivot_point_choose")

    if PIVOT_MODE == 1:
        # World origin
        tde4.setWidgetSensitiveFlag(requester, "Pivot_point_coordinate", 0)
        tde4.setWidgetValue(
            requester, "Pivot_point_coordinate", "0.0 0.0 0.0")
        PIVOT_COORD = [0, 0, 0]

    if PIVOT_MODE == 2:
        # Reference model
        tde4.setWidgetSensitiveFlag(requester, "Pivot_point_coordinate", 0)
        if REF_MODEL_ID == '':
            tde4.postQuestionRequester(
                "Rescale scene",
                "Pick reference model first!",
                "Ok")
            tde4.setWidgetValue(requester, "Pivot_point_choose", "1")
            tde4.setWidgetValue(requester, "Pivot_point_coordinate", "0.0 0.0 0.0")
            PIVOT_COORD = [0, 0, 0]
            return
        PIVOT_COORD = tde4.get3DModelPosition3D(
            pg, REF_MODEL_ID, cam, frame)
        pivot_coord_round = [round(r, 4) for r in PIVOT_COORD]
        tde4.setWidgetValue(
            requester,
            "Pivot_point_coordinate",
            ' '.join(map(str, pivot_coord_round)))

    if PIVOT_MODE == 3:
        # Exact coordinate
        tde4.setWidgetSensitiveFlag(requester, "Pivot_point_coordinate", 1)
        PIVOT_COORD = map(float, tde4.getWidgetValue(
            requester, "Pivot_point_coordinate").split())
    return


def rsclr_rescale_scene(requester, widget, action):
    global UPSCALE
    global PIVOT_COORD
    cam = tde4.getCurrentCamera()
    pg = tde4.getCurrentPGroup()

    if (cam is None) or (pg is None):
        tde4.postQuestionRequester(
            "Rescale scene", "There is no current Point Group or Camera.", "Ok")
        return
    if tde4.getCameraPath(cam) == '':
        tde4.postQuestionRequester(
            "Rescale scene", "You need to load footage in camera", "Ok")
        return

    if tde4.getNoPGroups() > 1:
        button = tde4.postQuestionRequester(
            "Rescale scene",
            "This script is not intended for use when object"
            "tracking is done. Use it on your own risk",
            "Continue", "Cancel")
        if button == 2: return

    if tde4.getCameraPosConstraintForceY(cam)[0] == 1:
        cam_pos_Y = tde4.getCameraPosConstraintForceY(cam)[1]
        tde4.setCameraPosConstraintForceY(
            cam, 1, (cam_pos_Y - PIVOT_COORD[1]) * UPSCALE + PIVOT_COORD[1])
    models_list = tde4.get3DModelList(pg)
    if tde4.getPGroupType(pg) == "CAMERA":
        reposition_model(models_list, PIVOT_COORD, UPSCALE)
        upscale_model(models_list, UPSCALE)
        scale_points(PIVOT_COORD, UPSCALE)
        scale_camera_path(PIVOT_COORD, UPSCALE)
        tde4.setWidgetValue(requester, "Ref_model_scale", "1.0")
        tde4.updateGUI()


def _YY_Rescale_sceneUpdate(requester):
    return


#
# UI
#

try:
    requester = _YY_Rescale_scene_requester
except (ValueError, NameError, TypeError):
    requester = tde4.createCustomRequester()

    # Get ref model
    tde4.addButtonWidget(requester, "Get_ref_model", "Get")
    tde4.setWidgetOffsets(requester, "Get_ref_model", 0, 40, 30, 0)
    tde4.setWidgetAttachModes(requester, "Get_ref_model",
                              "ATTACH_NONE", "ATTACH_WINDOW",
                              "ATTACH_WINDOW", "ATTACH_NONE")
    tde4.setWidgetLinks(requester, "Get_ref_model", "", "", "", "")
    tde4.setWidgetSize(requester, "Get_ref_model", 40, 20)
    tde4.setWidgetCallbackFunction(
        requester, "Get_ref_model", "rsclr_get_ref_model")

    # Reference model name
    tde4.addTextFieldWidget(requester, "Ref_model_name", "Reference model", "")
    tde4.setWidgetOffsets(requester, "Ref_model_name", 160, 10, 30, 0)
    tde4.setWidgetAttachModes(requester, "Ref_model_name",
                              "ATTACH_WINDOW", "ATTACH_WIDGET",
                              "ATTACH_WINDOW", "ATTACH_NONE")
    tde4.setWidgetLinks(requester, "Ref_model_name",
                        "", "Get_ref_model", "", "")
    tde4.setWidgetSize(requester, "Ref_model_name", 200, 20)
    tde4.setWidgetCallbackFunction(
        requester, "Ref_model_name", "rsclr_get_ref_model")
    tde4.setWidgetSensitiveFlag(requester, "Ref_model_name", 0)

    # Manual ref model scale
    tde4.addTextFieldWidget(requester, "Manual_ref_model_scale", "", "1.0")
    tde4.setWidgetOffsets(requester, "Manual_ref_model_scale", 0, 40, 10, 0)
    tde4.setWidgetAttachModes(requester, "Manual_ref_model_scale",
                              "ATTACH_NONE", "ATTACH_WINDOW",
                              "ATTACH_WIDGET", "ATTACH_NONE")
    tde4.setWidgetLinks(requester, "Manual_ref_model_scale",
                        "", "", "Ref_model_name", "")
    tde4.setWidgetSize(requester, "Manual_ref_model_scale", 60, 20)
    tde4.setWidgetCallbackFunction(
        requester, "Manual_ref_model_scale", "rsclr_manual_scale_ref_model")
    tde4.setWidgetSensitiveFlag(requester, "Manual_ref_model_scale", 0)

    # Ref model scale
    tde4.addScaleWidget(requester, "Ref_model_scale",
                        "Scale", "DOUBLE", 0.1, 2.0, 1.0)
    tde4.setWidgetOffsets(requester, "Ref_model_scale", 160, 10, 10, 0)
    tde4.setWidgetAttachModes(requester, "Ref_model_scale",
                              "ATTACH_WINDOW", "ATTACH_WIDGET",
                              "ATTACH_WIDGET", "ATTACH_NONE")
    tde4.setWidgetLinks(requester, "Ref_model_scale",
                        "", "Manual_ref_model_scale", "Ref_model_name", "")
    tde4.setWidgetSize(requester, "Ref_model_scale", 200, 20)
    tde4.setWidgetCallbackFunction(
        requester, "Ref_model_scale", "rsclr_scale_ref_model")
    tde4.setWidgetSensitiveFlag(requester, "Ref_model_scale", 0)

    # Pivot point coordinate
    tde4.addTextFieldWidget(
        requester, "Pivot_point_coordinate", "", "0.0 0.0 0.0")
    tde4.setWidgetOffsets(requester, "Pivot_point_coordinate", 160, 40, 14, 0)
    tde4.setWidgetAttachModes(requester, "Pivot_point_coordinate",
                              "ATTACH_WINDOW", "ATTACH_WINDOW",
                              "ATTACH_WIDGET", "ATTACH_NONE")
    tde4.setWidgetSize(requester, "Pivot_point_coordinate", 200, 20)
    tde4.setWidgetCallbackFunction(
        requester, "Pivot_point_coordinate", "rsclr_choose_pivot")
    tde4.setWidgetSensitiveFlag(requester, "Pivot_point_coordinate", 0)

    # Pivot point choise
    tde4.addOptionMenuWidget(requester, "Pivot_point_choose", "Pivot point",
                             "World origin", "Reference model", "Exact coordinate")
    tde4.setWidgetOffsets(requester, "Pivot_point_choose", 160, 40, 30, 0)
    tde4.setWidgetAttachModes(requester, "Pivot_point_choose",
                              "ATTACH_WINDOW", "ATTACH_WINDOW",
                              "ATTACH_WIDGET", "ATTACH_NONE")
    tde4.setWidgetLinks(requester, "Pivot_point_coordinate",
                        "", "", "Pivot_point_choose", "")
    tde4.setWidgetLinks(requester, "Pivot_point_choose",
                        "", "", "Ref_model_scale", "")
    tde4.setWidgetSize(requester, "Pivot_point_choose", 160, 20)
    tde4.setWidgetCallbackFunction(
        requester, "Pivot_point_choose", "rsclr_choose_pivot")
    tde4.setWidgetSensitiveFlag(requester, "Pivot_point_choose", 0)

    # Rescale scene
    tde4.addButtonWidget(requester, "Rescale_scene_button", "Rescale scene")
    tde4.setWidgetOffsets(requester, "Rescale_scene_button", 160, 40, 40, 0)
    tde4.setWidgetAttachModes(requester, "Rescale_scene_button",
                              "ATTACH_WINDOW", "ATTACH_WINDOW",
                              "ATTACH_WIDGET", "ATTACH_NONE")
    tde4.setWidgetLinks(requester, "Rescale_scene_button",
                        "", "", "Pivot_point_coordinate", "")
    tde4.setWidgetSize(requester, "Rescale_scene_button", 180, 30)
    tde4.setWidgetCallbackFunction(
        requester, "Rescale_scene_button", "rsclr_rescale_scene")

    _YY_Rescale_scene_requester = requester

#
# End of UI
#

if tde4.isCustomRequesterPosted(_YY_Rescale_scene_requester) == "REQUESTER_UNPOSTED":
    if tde4.getCurrentScriptCallHint() == "CALL_GUI_CONFIG_MENU":
        tde4.postCustomRequesterAndContinue(
            _YY_Rescale_scene_requester, "Rescale_scene", 0, 0, "_YY_Rescale_sceneUpdate")
    else:
        tde4.postCustomRequesterAndContinue(
            _YY_Rescale_scene_requester, "Rescale scene", 600, 260, "_YY_Rescale_sceneUpdate")
else:
    tde4.postQuestionRequester(
        "Rescale scene",
        "Window/Pane is already posted, close manually first!",
        "Ok")

# Reset widget values after reopening plugin window
tde4.setWidgetValue(requester, "Ref_model_name", "")
tde4.setWidgetValue(requester, "Ref_model_scale", "1.0")
tde4.setWidgetSensitiveFlag(requester, "Ref_model_scale", 0)
tde4.setWidgetValue(requester, "Manual_ref_model_scale", "1.0")
tde4.setWidgetSensitiveFlag(requester, "Manual_ref_model_scale", 0)
tde4.setWidgetValue(requester, "Pivot_point_choose", "1")
tde4.setWidgetSensitiveFlag(requester, "Pivot_point_choose", 0)
tde4.setWidgetValue(requester, "Pivot_point_coordinate", "0.0 0.0 0.0")
tde4.setWidgetSensitiveFlag(requester, "Pivot_point_coordinate", 0)
tde4.setWidgetSensitiveFlag(requester, "Pivot_point_choose", 0)

REF_MODEL_ID = ''
REF_SCALE = 1
UPSCALE = 1
PIVOT_MODE = 1
PIVOT_COORD = [0, 0, 0]
