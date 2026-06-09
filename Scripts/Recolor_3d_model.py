#
# 3DE4.script.name:  Recolor 3D Model
# 3DE4.script.version:  v2.0
# 3DE4.script.comment:  Applies preset colors to selected 3D models
#
# 3DE4.script.gui.attribute_editor:  3D Model
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#


from dataclasses import dataclass

import tde4


BUTTON_CALLBACK_DATA = {}


@dataclass
class ColorPreset:
    name: str
    model_rgb: tuple
    button_rgb: tuple
    text_rgb: tuple

# You can add more colors here without editing the rest of the code
# Just follow the pattern and RGB color model
COLOR_PRESETS = [
    ColorPreset(
        name="Red",
        model_rgb=(0.6, 0.15, 0.2),
        button_rgb=(0.6, 0.2, 0.2),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="Orange",
        button_rgb=(0.65, 0.30, 0.15),
        model_rgb=(0.65, 0.30, 0.15),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="Yellow",
        model_rgb=(0.5, 0.5, 0.2),
        button_rgb=(0.5, 0.5, 0.2),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="Green",
        model_rgb=(0.25, 0.5, 0.25),
        button_rgb=(0.25, 0.5, 0.25),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="Cyan",
        model_rgb=(0.25, 0.45, 0.65),
        button_rgb=(0.25, 0.45, 0.65),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="Blue",
        model_rgb=(0.15, 0.25, 1.0),
        button_rgb=(0.2, 0.25, 0.65),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="Purple",
        model_rgb=(0.40, 0.15, 0.45),
        button_rgb=(0.40, 0.15, 0.45),
        text_rgb=(1.0, 1.0, 1.0),
    ),
    ColorPreset(
        name="White",
        model_rgb=(0.8, 0.8, 0.8),
        button_rgb=(0.8, 0.8, 0.8),
        text_rgb=(0.2, 0.2, 0.2),
    ),
]


def recolor_3d_model(r, g, b):
    pgroup_list = tde4.getPGroupList(0)

    if not pgroup_list:
        return

    for pgroup_id in pgroup_list:
        model_list = tde4.get3DModelList(pgroup_id, 1)

        for model_id in model_list:
            alpha = tde4.get3DModelColor(
                pgroup_id,
                model_id,
            )[3]

            tde4.set3DModelColor(
                pgroup_id,
                model_id,
                r,
                g,
                b,
                alpha,
            )


def recolor_callback(requester, widget, action):
    color = BUTTON_CALLBACK_DATA.get(widget)

    if color is None:
        return

    recolor_3d_model(*color)


def create_color_buttons(requester_id):
    for index, preset in enumerate(COLOR_PRESETS):

        widget_name = f"color_{index}"

        BUTTON_CALLBACK_DATA[widget_name] = preset.model_rgb

        tde4.addButtonWidget(
            requester_id,
            widget_name,
            preset.name,
        )

        tde4.setWidgetCallbackFunction(
            requester_id,
            widget_name,
            "recolor_callback",
        )

        tde4.setWidgetBGColor(
            requester_id,
            widget_name,
            *preset.button_rgb,
        )

        if preset.text_rgb is not None:
            tde4.setWidgetFGColor(
                requester_id,
                widget_name,
                *preset.text_rgb,
            )

        # 4 buttons per row
        row = index // 4
        column = index % 4

        left = 4 + column * 24
        right = left + 20
        top = 8 + row * 32

        tde4.setWidgetAttachModes(
            requester_id,
            widget_name,
            "ATTACH_POSITION",
            "ATTACH_POSITION",
            "ATTACH_WINDOW",
            "ATTACH_NONE",
        )

        tde4.setWidgetOffsets(
            requester_id,
            widget_name,
            left,
            right,
            top,
            0,
        )


requester_id = tde4.createCustomRequester()

create_color_buttons(requester_id)


def requester_callback(requester):
    pass


tde4.postCustomRequesterAndContinue(
    requester_id,
    "Recolor 3D Model",
    0,
    0,
    "requester_callback",
)
