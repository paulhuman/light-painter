#     Light Paint, Blender add-on that creates lights based on where the user paints.
#     Copyright (C) 2023 Spencer Magnusson
#     semagnum@gmail.com
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import bpy

from .operators import LP_OT_ConvexHull, LP_OT_Skin

ADDON_NAME = 'Light Paint'

bl_info = {
    "name": ADDON_NAME,
    "author": 'Spencer Magnusson',
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "description": 'Creates lights based on where the user paints',
    "location": 'View 3D > Light Draw',
    "support": 'COMMUNITY',
    "category": '3D View',
    "doc_url": '',
    "tracker_url": '',
}


class LP_PT_LightPaint(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_label = ADDON_NAME
    bl_category = ADDON_NAME
    bl_region_type = 'UI'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        layout.operator(LP_OT_ConvexHull.bl_idname)
        layout.operator(LP_OT_Skin.bl_idname)


classes = [LP_OT_ConvexHull, LP_OT_Skin, LP_PT_LightPaint]
properties = []


def register():
    window_manager = bpy.types.WindowManager

    for cls in classes:
        bpy.utils.register_class(cls)

    for name, prop in properties:
        setattr(window_manager, name, prop)


def unregister():
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)

    window_manager = bpy.types.WindowManager
    for name, _ in properties[::-1]:
        try:
            delattr(window_manager, name)
        except AttributeError:
            pass


if __name__ == '__main__':
    register()
