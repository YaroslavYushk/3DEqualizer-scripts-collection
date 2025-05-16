#
# 3DE4.script.name: Calc overscan for Nuke
# 3DE4.script.version:	v1.0
# 3DE4.script.comment:	Calculates overscan for using in Nuke ScanlineRender node
#
# 3DE4.script.gui:	Main Window::Tools
#
# Author - Yaroslav Yushkevich
# Bugs, ideas, feedback - https://github.com/YaroslavYushk/
#


import tde4

import calc_overscan_distortion_bbox as calc_bbox
calc_bbox.__dict__["tde4"] = tde4
# Передача tde4 в пространство имён calc_overscan_distortion_bbox
# Потому что скрипт calc_overscan_distortion_bbox использует библиотеку tde4
# но не инициализирует её. Она доступна по умолчанию при вызове из самой
# программы, но недоступна при вызове из других скриптов, что вызывает ошибку


def calcOverscan(bbox_w, bbox_h):
    camera_id = tde4.getCurrentCamera()
    source_w = tde4.getCameraImageWidth(camera_id)
    source_h = tde4.getCameraImageHeight(camera_id)
    # bbox_w = calc_bbox.bbdld_compute_bounding_box(camera_id)[6]
    # bbox_h = calc_bbox.bbdld_compute_bounding_box(camera_id)[7]

    aspect = tde4.getLensPixelAspect(tde4.getCameraLens(camera_id))
    overscan_w = int((bbox_w - source_w) / 2 * aspect)
    overscan_h = int((bbox_h - source_h) / 2)

    if overscan_w < 0: overscan_w = 0
    if overscan_h < 0: overscan_h = 0

    return max(overscan_w, overscan_h)


if __name__ == '__main__':
    requester = tde4.createCustomRequester()
    camera_id = tde4.getCurrentCamera()
    camera_name = tde4.getCameraName(camera_id)

    tde4.addTextAreaWidget(requester, "textarea", "", 100, 0)
    tde4.setWidgetOffsets(requester, "textarea", 0, 0, 0, 0)
    tde4.setWidgetAttachModes(requester, "textarea",
                              "ATTACH_WINDOW", "ATTACH_WINDOW",
                              "ATTACH_WINDOW", "ATTACH_WINDOW")
    tde4.setWidgetLinks(requester, "textarea", "", "", "", "")
    tde4.setWidgetSize(requester, "textarea", 150, 150)

    tde4.appendTextAreaWidgetString(
        requester, "textarea", f"Current camera: {camera_name}\n\n")

    source_w = tde4.getCameraImageWidth(camera_id)
    source_h = tde4.getCameraImageHeight(camera_id)
    tde4.appendTextAreaWidgetString(
        requester, "textarea", f"Original size: {source_w} x {source_h} \n")

    bbox_w, bbox_h = calc_bbox.bbdld_compute_bounding_box(camera_id)[6:8]
    tde4.appendTextAreaWidgetString(
        requester, "textarea",
        f"Undistort bounding box size: {bbox_w} x {bbox_h} \n")

    aspect = tde4.getLensPixelAspect(tde4.getCameraLens(camera_id))
    tde4.appendTextAreaWidgetString(
        requester, "textarea", "Pixel aspect: %s\n\n" % (aspect))

    tde4.appendTextAreaWidgetString(
        requester, "textarea",
        f"Minimal overscan for Nuke ScanlineRender node is: "
        f"{str(calcOverscan(bbox_w, bbox_h))}")
    tde4.postCustomRequester(requester, "Calc Overscan", 600, 230, "Close")
    tde4.deleteCustomRequester(requester)
