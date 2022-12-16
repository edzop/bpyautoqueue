import bpy

# ==================================================
# foam material helper functions
# ==================================================

# delete all nodes except output material
def delete_all_nodes_except_output_material(nodes):
	for node in nodes:
		if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
			nodes.remove(node)


def delete_material(material_name):
	for m in bpy.data.materials:
		if m.name==material_name:
			bpy.data.materials.remove(m)

def get_material(material_name):
	for m in bpy.data.materials:
		if m.name==material_name:
			return m

	return None

def assign_linked_material(ob,material_name,path,slot=0):

	# first search for material
	m=get_material(material_name)

	# Import material
	if m is None:
		bpy.ops.wm.link(directory=path,link=True,files=[{'name': "%s"%material_name}], relative_path=False)

		# Try again to find material after import
		m = get_material(material_name)

	if m is not None:
		assign_material(ob,m,slot)
		
def make_metalic_material(name,color):
	mat = bpy.data.materials.new(name)
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes

	shader_node = nodes['Principled BSDF']
	#color=[1,0.3,0.3,1]
	shader_node.inputs[0].default_value=color

	# metalic
	shader_node.inputs[4].default_value=0.67

	# roughness
	shader_node.inputs[7].default_value=0.277

	mat.diffuse_color=shader_node.inputs[0].default_value
	return mat


def make_diffuse_material(name,color):
	delete_material(name)
	new_material = bpy.data.materials.new(name)
	#print(color)
	new_material.diffuse_color = color
	return new_material

def make_glass_material(name,color):
 
	mat = bpy.data.materials.new(name)
		
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes
	
	delete_all_nodes_except_output_material(nodes)
	
	links = mat.node_tree.links

	nodeGlossy = nodes.new(type='ShaderNodeBsdfGlossy')
	nodeGlossy.location=-200,100
	nodeGlossy.inputs[1].default_value=0
	nodeGlossy.inputs[0].default_value=color
	
	node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
	node_transparent.location = -200,-100
	#node_transparent.inputs[2]=1.01

	node_mix = nodes.new(type='ShaderNodeMixShader')
	node_mix.location=0,0
	node_mix.inputs[0].default_value=0.776
	
	
	links.new(nodeGlossy.outputs[0], node_mix.inputs[1])
	links.new(node_transparent.outputs[0], node_mix.inputs[2])
	
	node_output=nodes['Material Output']
	node_output.location=200,0

	links.new(node_mix.outputs[0], node_output.inputs[0])

	return mat


def make_subsurf_material(name,color):
	mat = bpy.data.materials.new(name)
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes

	shader_node = nodes['Principled BSDF']

	shader_node.inputs[0].default_value=color

	# subsurf
	shader_node.inputs[1].default_value=1
	shader_node.inputs[3].default_value=color

	mat.diffuse_color=shader_node.inputs[0].default_value
	return mat


# Use -1 for slot to assign to last material 
# This case would be used when you want multiple materials and not overwrite the 0 slot
def assign_material(ob,mat,slot=0):
	# Assign it to object
	if ob.data.materials:
		if slot!=-1:
			# assign to material slot
			ob.data.materials[slot] = mat
			return
		else:
			# Check if already assigned to last slot
			material_count=len(ob.data.materials)
			if ob.data.materials[material_count-1].name==mat.name:
				return

	# Assign to last slot
	ob.data.materials.append(mat)


def make_liquid_material(name,color):
	mat = bpy.data.materials.new(name)
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes

	shader_node = nodes['Principled BSDF']
	#color=[1,0.3,0.3,1] RGBA
	shader_node.inputs[0].default_value=color

	# transmission
	shader_node.inputs[17].default_value=0.95
	
	# roughness
	shader_node.inputs[9].default_value=0
 
	# subsurf
	shader_node.inputs[1].default_value=1
	shader_node.inputs[3].default_value=color

	mat.diffuse_color=shader_node.inputs[0].default_value
	return mat