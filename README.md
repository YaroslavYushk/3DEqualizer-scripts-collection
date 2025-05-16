# 3DEqualizer-scripts-collection

Collection of scripts for 3DEqualizer written by me

## Rescale scene

This script allows you to scale all your scene based on the size of your reference 3d object

### How to use

1. Add reference geometry to your scene (it can be a human figure or any other object whose size you can determine visually)
2. Open the script panel
3. Select the reference geometry
4. Adjust the Scale slider to modify model's size
5. (Optional) Select the coordinates of the pivot point
6. Press the "Rescale Scene" button

![gif](https://github.com/YaroslavYushk/3DEqualizer-scripts-collection/blob/main/Media/Rescale_scene.gif)

[link](https://github.com/YaroslavYushk/3DEqualizer-scripts-collection/blob/main/Scripts/Recale_scene.py)

## Create human

Creates 3d model of human, 180cm height. Very handy for scale reference of your scene and works great with Rescale Scene script

[link](https://github.com/YaroslavYushk/3DEqualizer-scripts-collection/blob/main/Scripts/Create_human.py)

## Point Position Copy-Paste

As simple as it is. Allows you to copy and paste 3d position of a survey point

[link](https://github.com/YaroslavYushk/3DEqualizer-scripts-collection/blob/main/Scripts/Point_Position_Copy-Paste.py)

## Calc overscan for Nuke

Calculates minimal overscan for ScanlineRender node in Nuke. Uses "calc_overscan_distortion_bbox" script from 3DE (which you have by default) but shows convenient values

[link](https://github.com/YaroslavYushk/3DEqualizer-scripts-collection/blob/main/Scripts/Calc_overscan_for_Nuke.py)
