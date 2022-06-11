import bpy



from . import material_helper


def add_follow_target_constraint(obj,target):
    trackConstraint = obj.constraints.new(type='DAMPED_TRACK')
    trackConstraint.target = target
    trackConstraint.track_axis='TRACK_NEGATIVE_Z'

def add_studio_lights():

    camTarget=None
    camObject=None

    # first find camTarget
    for obj in bpy.data.objects:
        if obj.type=="CAMERA":
            for constraint in obj.constraints:
                if constraint.type == 'DAMPED_TRACK':
                    camTarget=constraint.target
                    camObject=obj
        
    # Create a focus object if not found            
    if camTarget==None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        camTarget = bpy.context.active_object
        camTarget.name="focus"
        
    # Create a camera if not found
    if camObject==None:
        bpy.ops.object.camera_add(enter_editmode=False, 
            align='VIEW', 
            location=(0, 0, 0), 
            rotation=(0, 0, 0))
        camObject = bpy.context.active_object
        camObject.name="DefaultCam"

    isTracked=False    

    # Make sure trackto constraint set
    for constraint in camObject.constraints:
        if constraint.type == 'DAMPED_TRACK':
            constraint.target=camTarget				
            isTracked=True
                    
    if isTracked==False:
        trackConstraint = camObject.constraints.new(type='DAMPED_TRACK')
        trackConstraint.target = camTarget
        trackConstraint.track_axis='TRACK_NEGATIVE_Z'

            
    bpy.ops.mesh.primitive_plane_add(size=2)
    obj_light_top=bpy.context.view_layer.objects.active
    obj_light_top.name="light.top"

    bpy.ops.mesh.primitive_plane_add(size=2)
    obj_light_side=bpy.context.view_layer.objects.active
    obj_light_side.name="light.side"

    bpy.ops.mesh.primitive_plane_add(size=2)
    obj_light_back=bpy.context.view_layer.objects.active
    obj_light_back.name="light.back"

    light_distance=8

    obj_light_back.location.z=1.5
    obj_light_side.location.z=1.5

    obj_light_back.location.y=-(light_distance*2)
    obj_light_side.location.y=-(light_distance*2)
 
    obj_light_back.location.x=light_distance
    obj_light_side.location.x=-light_distance
    obj_light_top.location.z=light_distance

    add_follow_target_constraint(obj_light_back,camTarget)
    add_follow_target_constraint(obj_light_side,camTarget)
    add_follow_target_constraint(obj_light_top,camTarget)

    texlibpath_materials="/home/blender/texlib.blend/Material"

    material_helper.assign_linked_material(obj_light_back,"light.back",texlibpath_materials)
    material_helper.assign_linked_material(obj_light_side,"light.side",texlibpath_materials)
    material_helper.assign_linked_material(obj_light_top,"light.top",texlibpath_materials)



