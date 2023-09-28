import pytest

from blender_pretest import blender_fixture, run_blender, SINGLE_STROKE, SINGLE_POINT


@blender_fixture
def context():
    import bpy
    return bpy.context


@blender_fixture
def ops():
    import bpy
    return bpy.ops


# Unit tests for validating each light tool can at least run


@run_blender
def test_light_paint_modal(context, ops):
    """Each light tool at least runs with default settings."""
    ops.lightpainter.lamp(str_mouse_path=SINGLE_STROKE, offset=10.0, lamp_type='POINT')
    ops.lightpainter.lamp(str_mouse_path=SINGLE_STROKE, offset=10.0, lamp_type='SPOT')
    ops.lightpainter.lamp(str_mouse_path=SINGLE_STROKE, offset=10.0, lamp_type='AREA')

    ops.lightpainter.mesh(str_mouse_path=SINGLE_STROKE)
    ops.lightpainter.tube_light(str_mouse_path=SINGLE_STROKE)
    ops.lightpainter.sky(str_mouse_path=SINGLE_STROKE)

    next(obj for obj in context.scene.objects if obj.type == 'LIGHT').select_set(True)
    ops.lightpainter.flag(str_mouse_path=SINGLE_STROKE)

    print([obj for obj in context.scene.objects])
    obj_names = {obj.name for obj in context.scene.objects}
    assert 'LightPaint_Flag' in obj_names
    assert 'Point' in obj_names
    assert 'LightPaint_Convex' in obj_names
    assert 'LightPaint_Tube' in obj_names


# Unit test to validate each axis

@run_blender
def test_axis(context, ops):
    """Each axis option moves lamps in the correct direction."""
    light_obj = context.scene.objects['Light']
    light_obj.data.type = 'SPOT'
    actual_location = light_obj.location
    actual_rotation = light_obj.rotation_euler

    HALF_PI = 1.5708
    PI = HALF_PI * 2
    EPSILON = 0.0001

    ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = light_obj

    def matches_vector(expected: tuple[float, float, float], actual) -> bool:
        return all(
            expected - actual <= EPSILON
            for expected, actual in zip(expected, actual)
        )

    ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=1.0, axis='X')
    print(actual_location, actual_rotation)
    assert matches_vector((1.0, 0.0, 0.0), actual_location)
    assert matches_vector((0.0, HALF_PI, 0.0), actual_rotation)

    ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=1.0, axis='Y')
    print(actual_location, actual_rotation)
    assert matches_vector((0.0, 1.0, 0.0), actual_location)
    assert matches_vector((-HALF_PI, 0.0, 0.0), actual_rotation)

    ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=1.0, axis='Z')
    print(actual_location, actual_rotation)
    assert all(expected == actual for expected, actual in zip((0.0, 0.0, 1.0), actual_location))
    assert matches_vector((-HALF_PI, 0.0, 0.0), actual_rotation)

    # test negative offset while we're at it
    ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=-1.0, axis='Z')
    print(actual_location, actual_rotation)
    assert matches_vector((0.0, 0.0, -1.0), actual_location)
    assert matches_vector((PI, 0.0, HALF_PI), actual_rotation)

    ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=1.0, axis='NORMAL')
    print(actual_location, actual_rotation)
    assert matches_vector((1.0, 1.0, 1.0), actual_location)
    assert matches_vector((-0.7854, 0.6155, -0.2618), actual_rotation)

    ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=1.0, axis='REFLECT')
    print(actual_location, actual_rotation)
    assert matches_vector((1.6538, -0.3259, 0.2333), actual_location)
    assert matches_vector((-2.1921, 0.7125, -1.2535), actual_rotation)


@run_blender
def test_rim_lighting_no_camera_fails(ops, context):
    """Validate that the rim lighting requires a camera to work, and correctly fails."""
    light_obj = context.scene.objects['Light']

    ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = light_obj

    with context.temp_override(selected_objects=[context.scene.objects['Camera']]):
        ops.object.delete(use_global=False)

    with pytest.raises(Exception):
        ops.lightpainter.lamp_adjust(str_mouse_path=SINGLE_POINT, offset=1.0, axis='REFLECT')


@run_blender
def test_ray_visibility(ops, context):
    """Validate ray visibility settings are applied correctly."""
    ops.lightpainter.lamp(
        str_mouse_path=SINGLE_STROKE, offset=10.0, lamp_type='POINT',
        visible_camera=False, visible_diffuse=False, visible_specular=False, visible_volume=False
    )

    assert 'Point' in context.scene.objects

    lamp_obj = context.scene.objects['Point']

    assert not lamp_obj.visible_camera
    assert not lamp_obj.visible_diffuse
    assert not lamp_obj.visible_glossy
    assert not lamp_obj.visible_volume_scatter

    lamp_data = lamp_obj.data
    assert lamp_data.diffuse_factor == 0.0
    assert lamp_data.specular_factor == 0.0
    assert lamp_data.volume_factor == 0.0

    # test the same thing for sky textures
    ops.lightpainter.sky(
        str_mouse_path=SINGLE_STROKE, normal_method='AVERAGE',
        visible_camera=False, visible_diffuse=False, visible_specular=False, visible_volume=False
    )

    world_data = context.scene.world.cycles_visibility
    assert not world_data.camera
    assert not world_data.diffuse
    assert not world_data.glossy
    assert not world_data.scatter
