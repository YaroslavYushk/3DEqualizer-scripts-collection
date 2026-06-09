#
# 3DE4.script.name:  Point Nudge XYZ
# 3DE4.script.version:  v1.0
# 3DE4.script.comment:  Nudges selected points along XYZ axes with configurable step
#
# 3DE4.script.gui.attribute_editor:  Point
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#


import tde4


# ---- Helpers ---------------------------------------------------------------

def get_step(value):
    units = tde4.getPreferenceValue('CONSTR_UNIT')
    if units == '0':  # m
        return (value * 100)
    elif units == '1':  # cm
        return (value)
    elif units == '2':  # mm
        return (value / 10)
    else:
        return (value)  # I don't care about in, ft or yd


def move_selected_points(dx, dy, dz):

    pg = tde4.getCurrentPGroup()
    if pg is None:
        return

    points = tde4.getPointList(pg, 1)  # selected points only

    if len(points) == 0:
        tde4.postQuestionRequester(
            "Point Nudge XYZ",
            "No points selected.",
            "Ok"
        )
        return

    tde4.pushPointsToUndoStack()

    for p in points:

        if tde4.getPointSurveyMode(pg, p) == 'SURVEY_FREE':
            continue

        pos = tde4.getPointSurveyPosition3D(pg, p)

        new_pos = [
            pos[0] + dx,
            pos[1] + dy,
            pos[2] + dz
        ]

        tde4.setPointSurveyPosition3D(pg, p, new_pos)

    tde4.updateGUI()


# ---- UI --------------------------------------------------------------------

req = tde4.createCustomRequester()

# Row 1
tde4.addButtonWidget(req, "plus_x", "+X")
tde4.addButtonWidget(req, "plus_y", "+Y")
tde4.addButtonWidget(req, "plus_z", "+Z")

# Row 2
tde4.addButtonWidget(req, "minus_x", "-X")
tde4.addButtonWidget(req, "minus_y", "-Y")
tde4.addButtonWidget(req, "minus_z", "-Z")

# Step field
tde4.addTextFieldWidget(req, "step", "", "1.0")

# Row 4
tde4.addButtonWidget(req, "mul10", "*10")
tde4.addButtonWidget(req, "div10", "/10")


# ---- Callback --------------------------------------------------------------

def callback(req, widget, action):

    try:
        value = float(tde4.getWidgetValue(req, "step"))
    except Exception as err:
        tde4.postQuestionRequester(
            "Point Nudge XYZ",
            "Wrong step input",
            "Ok"
        )
        raise err

    step = get_step(value)

    if widget == "plus_x":
        move_selected_points(step, 0.0, 0.0)
    elif widget == "minus_x":
        move_selected_points(-step, 0.0, 0.0)
    elif widget == "plus_y":
        move_selected_points(0.0, step, 0.0)
    elif widget == "minus_y":
        move_selected_points(0.0, -step, 0.0)
    elif widget == "plus_z":
        move_selected_points(0.0, 0.0, step)
    elif widget == "minus_z":
        move_selected_points(0.0, 0.0, -step)

    elif widget == "mul10":
        tde4.setWidgetValue(req, "step", str(value * 10.0))
    elif widget == "div10":
        tde4.setWidgetValue(req, "step", str(value / 10.0))


for w in [
    "plus_x",
    "plus_y",
    "plus_z",
    "minus_x",
    "minus_y",
    "minus_z",
    "mul10",
    "div10"
]:
    tde4.setWidgetCallbackFunction(req, w, "callback")


# ---- Layout ----------------------------------------------------------------

# Row 1

tde4.setWidgetAttachModes(req, "plus_x",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "plus_x", 5, 31, 5, 30)

tde4.setWidgetAttachModes(req, "plus_y",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "plus_y", 35, 61, 5, 30)

tde4.setWidgetAttachModes(req, "plus_z",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "plus_z", 65, 95, 5, 30)

# Row 2

tde4.setWidgetAttachModes(req, "minus_x",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "minus_x", 5, 31, 35, 60)

tde4.setWidgetAttachModes(req, "minus_y",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "minus_y", 35, 61, 35, 60)

tde4.setWidgetAttachModes(req, "minus_z",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "minus_z", 65, 95, 35, 60)

# Step field

tde4.setWidgetAttachModes(req, "step",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "step", 15, 85, 75, 100)

# Row 4

tde4.setWidgetAttachModes(req, "mul10",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "mul10", 15, 46, 110, 135)

tde4.setWidgetAttachModes(req, "div10",
    "ATTACH_POSITION", "ATTACH_POSITION",
    "ATTACH_WINDOW", "ATTACH_NONE")
tde4.setWidgetOffsets(req, "div10", 54, 85, 110, 135)


# ---- Show requester --------------------------------------------------------

tde4.postCustomRequesterAndContinue(
    req,
    "Point Nudge XYZ",
    320,
    170
)
