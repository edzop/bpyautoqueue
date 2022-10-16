import bpy
import os.path
import os
import time
import functools
import glob


def get_cycles_samples():
	return 200

def setup_cycles_fstop():
	bpy.context.scene.camera.data.cycles.aperture_type="FSTOP"
	bpy.context.scene.camera.data.cycles.aperture_blades=5
	bpy.context.scene.camera.data.cycles.aperture_fstop=0.3



def check_node_tree_is_lit(nodes):

#   				 if "Emission" in nodes:
#   					 print("yes")
    for node in nodes:
        if node.type == "EMISSION":
            return True
            
        if node.type=="GROUP":
            sub_tree=node.node_tree.nodes
            if check_node_tree_is_lit(sub_tree):
                return True

        if node.type == "BSDF_PRINCIPLED":
            if node.inputs[18].default_value>0:
                return True

    return False



def check_cycles_emission_material():

    for obj in bpy.data.objects:
    #    print(obj.type + " = " + obj.name)
        if obj.type=="MESH":
            for mat in obj.data.materials:
                if mat!=None:
                    if mat.node_tree!=None:
                        nodes=mat.node_tree.nodes
                        if check_node_tree_is_lit(nodes):
                            return True
                                    
    return False

def setup_cycles_settings():

	bpy.context.scene.render.engine='CYCLES'
	bpy.context.scene.cycles.device='GPU'
	#bpy.context.scene.cycles.device='CPU'
	bpy.context.scene.cycles.max_bounces=8
	bpy.context.scene.cycles.min_bounces=3
	bpy.context.scene.cycles.diffuse_bounces=4
	bpy.context.scene.cycles.glossy_bounces=4
	bpy.context.scene.cycles.transmission_bounces=12
	bpy.context.scene.cycles.transparent_min_bounces=8
	bpy.context.scene.cycles.transparent_max_bounces=8
	bpy.context.scene.cycles.samples=get_cycles_samples()
	bpy.context.scene.cycles.use_transparent_shadows=True
	bpy.context.scene.cycles.no_caustics=False
	bpy.context.scene.cycles.use_square_samples=False

	bpy.context.scene.view_settings.view_transform="Filmic"
	bpy.context.scene.view_settings.look="High Contrast"
	bpy.context.scene.cycles.sample_clamp_indirect=9

#	bpy.context.scene.render.tile_x=64
#	bpy.context.scene.render.tile_y=64
	#bpy.context.scene.cycles.use_cache=False
	bpy.context.scene.render.use_persistent_data=True
	#bpy.context.scene.cycles.use_animated_seed=True
#	bpy.context.scene.render.layers.active.cycles.use_denoising=True


	bpy.context.scene.cycles.use_adaptive_sampling = True
	bpy.context.scene.cycles.adaptive_threshold = 0.05

	bpy.context.scene.cycles.use_denoising = True
	
	setup_aces_cg()

	setup_cycles_fstop()



def setup_aces_cg():

	render_layer_node=None
	colorspace_node=None
	composite_node=None

	scene = bpy.context.scene

	bpy.context.scene.use_nodes = True

	node_tree=scene.node_tree

	if node_tree:
	
		for node in node_tree.nodes:
	
			#print(node.type)
			
			if node.type=="CONVERT_COLORSPACE":
				colorspace_node=node

			if node.type=="COMPOSITE":
				composite_node=node

			if node.type=="R_LAYERS":
				render_layer_node=node

		if colorspace_node==None:
			colorspace_node = node_tree.nodes.new(type='CompositorNodeConvertColorSpace')

		if colorspace_node!=None and render_layer_node!=None and composite_node!=None:

			render_layer_node.location=0,0
			colorspace_node.location = 300,0
			composite_node.location=600,0
			
			colorspace_node.from_color_space = 'Linear'
			colorspace_node.to_color_space = 'Linear ACEScg'

			scene.node_tree.links.new(render_layer_node.outputs["Image"],colorspace_node.inputs["Image"])
			scene.node_tree.links.new(colorspace_node.outputs["Image"],composite_node.inputs["Image"])


def make_emission_material_cycles(material_name,color):

	if material_name in bpy.data.materials:
		mat = bpy.data.materials[material_name]
	else:
		mat = bpy.data.materials.new(material_name)

	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes

	links = mat.node_tree.links

	# clear all nodes to start clean
	for node in nodes:
		nodes.remove(node)

	color_a=(color[0],color[1],color[2],1)

	# create emission node
	node_emission = nodes.new(type='ShaderNodeEmission')
	node_emission.inputs[0].default_value = color_a  # green RGBA
	node_emission.inputs[1].default_value = 300.0 # strength
	node_emission.location = -200,-200


	# create glossy node
	node_glossy= nodes.new(type='ShaderNodeBsdfGlossy')
	node_glossy.inputs[0].default_value = color_a  # green RGBA
	node_glossy.inputs[1].default_value = 0.2 # roughness
	node_glossy.location = -200,0

	# create mix node
	node_mix = nodes.new(type='ShaderNodeMixShader')
	node_mix.location = 0,0

	link = links.new(node_glossy.outputs[0],node_mix.inputs[1])
	link = links.new(node_emission.outputs[0],node_mix.inputs[2])


	# create output node
	node_output = nodes.new(type='ShaderNodeOutputMaterial')
	node_output.location = 200,0

	link = links.new(node_mix.outputs[0], node_output.inputs[0])

	return mat

def animate_emission_cycles(mat,keyframes):
	nodes=mat.node_tree.nodes
	node_emission = nodes.get("Emission")

	for frame_number,strength_value in keyframes:
		print("Frame: %d Strength: %d"%(frame_number,strength_value))
		node_emission.inputs[1].default_value = (strength_value*300)
		node_emission.inputs[1].keyframe_insert("default_value", frame=frame_number)
