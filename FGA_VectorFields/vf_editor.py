### Editor Functions

import bpy
import gpu

from mathutils import Vector, Matrix

from gpu_extras.batch import batch_for_shader


### Create

# Creates a new vector field from parameters
def build_vectorfield(context):
	zeroVect = Vector((0.0,0.0,0.0))
	
	densityVal = Vector(context.window_manager.vf_density)
	scaleVal = Vector(context.window_manager.vf_scale)
	baseLoc = -1.0 * (densityVal * 0.5) + Vector((0.5, 0.5, 0.5))
	
	totalvertscount = densityVal[0] * densityVal[1] * densityVal[2]
	
	vf_startlocs = [zeroVect.copy() for v in range(int(totalvertscount))]
	vf_velocities = [zeroVect.copy() for v in range(int(totalvertscount))]
	
	volcount = 0
	for v in range(len(context.scene.objects)):
		if ("VF_Volume" in str(context.scene.objects[v].name)):
			volcount += 1
	
	# create the volume
	me = bpy.data.meshes.new("Vert")
	me.vertices.add(totalvertscount)
	from bpy_extras import object_utils
	object_utils.object_data_add(context, me, operator=None)
	
	volMesh = context.active_object
	volMesh.name = 'VF_Volume_' + str(volcount)
	volMesh.display.show_shadows = False
	volMesh.location = zeroVect
	
	# add the particle system
	bpy.ops.object.particle_system_add()
	degp = bpy.context.evaluated_depsgraph_get()
	particle_systems = volMesh.evaluated_get(degp).particle_systems
	psettings = particle_systems[0].settings
	
	#me = volMesh.data
	#me.update()
	meshverts = [v for v in me.vertices]
	
	volMesh.vf_object_density = densityVal
	volMesh.vf_object_scale = scaleVal
	
	# create vertices + initialize velocities list
	xval = int(densityVal[0])
	yval = int(densityVal[1])
	zval = int(densityVal[2])
	tempV = zeroVect.copy()
	counter = 0
	for i in range(zval):
		for j in range(yval):
			for k in range(xval):
				tempV[0] = (baseLoc[0] + (k)) * scaleVal[0]
				tempV[1] = (baseLoc[1] + (j)) * scaleVal[1]
				tempV[2] = (baseLoc[2] + (i)) * scaleVal[2]
				meshverts[counter].co = tempV
				vf_startlocs[counter][0] = tempV[0]
				vf_startlocs[counter][1] = tempV[1]
				vf_startlocs[counter][2] = tempV[2]
				counter += 1
	
	me.update()
	
	del meshverts[:]
	
	# create the particle system
	psettings.count = totalvertscount
	psettings.emit_from = 'VERT'
	psettings.normal_factor = 0.0
	psettings.use_emit_random = False
	psettings.frame_end = 1
	psettings.lifetime = context.window_manager.vf_particleLifetime
	psettings.grid_resolution = 1
	psettings.use_rotations = True
	psettings.use_dynamic_rotation = True
	psettings.effector_weights.gravity = context.window_manager.vf_gravity
	
	# create the bounding box
	bpy.ops.mesh.primitive_cube_add(location=(0.0,0.0,0.0))
	boundsMesh = context.active_object
	boundsMesh.name = 'VF_Bounds_' + str(volcount)
	boundsMesh.display.show_shadows = False
	
	# match scale to the volume
	boundsMesh.scale[0] = (densityVal[0] * 0.5) * scaleVal[0]
	boundsMesh.scale[1] = (densityVal[1] * 0.5) * scaleVal[1]
	boundsMesh.scale[2] = (densityVal[2] * 0.5) * scaleVal[2]
	bpy.ops.object.transform_apply(scale=True)
	
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.delete(type='ONLY_FACE')
	bpy.ops.object.mode_set(mode='OBJECT')
	
	volMesh.parent = boundsMesh
	
	if len(vf_velocities) == len (vf_startlocs):
		for i in range(len(vf_velocities)):
			tempvertdata = volMesh.custom_vectorfield.add()
			tempvertdata.vcoord = Vector(vf_startlocs[i])
			tempvertdata.vvelocity = Vector(vf_velocities[i])
	else:
		print ("VectorField coords/velocities length mismatch!")
	
	del vf_velocities[:]
	del vf_startlocs[:]
	
	tempconstraint = volMesh.constraints.new(type='COPY_TRANSFORMS')
	tempconstraint.target = volMesh.parent
	
	return volMesh.name


class VFTOOLS_OT_create_vectorfield(bpy.types.Operator):
	bl_idname = 'vftools.create_vectorfield'
	bl_label = 'Create VectorField'
	bl_description = 'Create a new vector field from resolution and scale values'
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		build_vectorfield(context)
		return {'FINISHED'}




# Performs vector math + writes results to data
class calc_vectorfieldvelocities(bpy.types.Operator):
	bl_idname = 'object.calc_vectorfieldvelocities'
	bl_label = 'Save VF EndLocations'
	bl_description = 'Calculate and save velocities'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.mode == "OBJECT" and context.active_object != None) and 'VF_Volume_' in context.active_object.name
	
	def execute(self, context):
		invmult = -1.0 if context.window_manager.pvelocity_invert else 1.0
		
		useselection = context.window_manager.pvelocity_selection
		
		particleslist = []
		
		volmesh = context.active_object
		
		vf_velocities = [Vector(v.vvelocity) for v in volmesh.custom_vectorfield]
		
		
		degp = bpy.context.evaluated_depsgraph_get()
		particle_systems = volmesh.evaluated_get(degp).particle_systems
		
		## Get velocities
		if context.window_manager.pvelocity_veltype == "VECT":
			tempvect = Vector(context.window_manager.pvelocity_dirvector)
			particleslist = [tempvect.copy() for v in vf_velocities]
		elif context.window_manager.pvelocity_veltype == "DIST":
			vf_startlocs = [Vector(v.vcoord) for v in volmesh.custom_vectorfield]
			vf_endLocs = [v.location for v in particle_systems[0].particles]
			particleslist = [(vf_endLocs[i] - vf_startlocs[i]) for i in range(len(vf_endLocs))]
			del vf_startlocs[:]
			del vf_endLocs[:]
		elif context.window_manager.pvelocity_veltype == "ANGVEL":
			particleslist = [p.angular_velocity for p in particle_systems[0].particles]
		elif context.window_manager.pvelocity_veltype == "PNT":
			cursorloc = context.scene.cursor.location
			particleslist = [(Vector(v.vcoord) - cursorloc).normalized() for v in volmesh.custom_vectorfield]
		else:
			particleslist = [p.velocity for p in particle_systems[0].particles]
		
		mvertslist = []
		if useselection:
			me = volmesh.data
			mvertslist = tuple(v.select for v in me.vertices)
		
		
		## Blend with List / calculate
		
		# multiply
		if context.window_manager.pvelocity_genmode == 'MULT':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_velocities[i] = Vector(
							(vf_velocities[i][0] * (particleslist[i][0] * invmult), 
							vf_velocities[i][1] * (particleslist[i][1] * invmult), 
							vf_velocities[i][2] * (particleslist[i][2] * invmult))
						)
			else:
				for i in range(len(particleslist)):
					vf_velocities[i] = Vector(
						(vf_velocities[i][0] * (particleslist[i][0] * invmult), 
						vf_velocities[i][1] * (particleslist[i][1] * invmult), 
						vf_velocities[i][2] * (particleslist[i][2] * invmult))
					)
			
		# add
		elif context.window_manager.pvelocity_genmode == 'ADD':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_velocities[i] = vf_velocities[i] + ((particleslist[i]) * invmult)
			else:
				for i in range(len(particleslist)):
					vf_velocities[i] = vf_velocities[i] + ((particleslist[i]) * invmult)
			
		# average
		elif context.window_manager.pvelocity_genmode == 'AVG':
			avgratio = context.window_manager.pvelocity_avgratio
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_velocities[i] = ((vf_velocities[i] * (1.0 - avgratio)) + ((particleslist[i] * invmult) * avgratio))
			else:
				for i in range(len(particleslist)):
					vf_velocities[i] = ((vf_velocities[i] * (1.0 - avgratio)) + ((particleslist[i] * invmult) * avgratio))
			
		# replace
		elif context.window_manager.pvelocity_genmode == 'REP':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_velocities[i] = particleslist[i] * invmult
			else:
				for i in range(len(particleslist)):
					vf_velocities[i] = particleslist[i] * invmult
			
		# cross product
		elif context.window_manager.pvelocity_genmode == 'CRS':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_velocities[i] = vf_velocities[i].cross(particleslist[i])
			else:
				for i in range(len(particleslist)):
					vf_velocities[i] = vf_velocities[i].cross(particleslist[i])
			
		# reflection
		elif context.window_manager.pvelocity_genmode == 'REF':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_velocities[i] = vf_velocities[i].reflect(particleslist[i])
			else:
				for i in range(len(particleslist)):
					vf_velocities[i] = vf_velocities[i].reflect(particleslist[i])
		
		
		# write new velocities
		for i in range(len(vf_velocities)):
			volmesh.custom_vectorfield[i].vvelocity = vf_velocities[i].copy()
		
		
		del particleslist[:]
		del vf_velocities[:]
		context.window_manager.vf_showingvelocitylines = -1
		return {'FINISHED'}


# Normalizes the list
class vf_normalizevelocities(bpy.types.Operator):
	bl_idname = 'object.vf_normalizevelocities'
	bl_label = 'Normalize'
	bl_description = 'Normalizes the currently saved velocity list'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object != None and 'VF_Volume_' in context.active_object.name
	
	def execute(self, context):
		volmesh = context.active_object
		for i in range(len(volmesh.custom_vectorfield)):
			tempVect = Vector(volmesh.custom_vectorfield[i].vvelocity)
			volmesh.custom_vectorfield[i].vvelocity = tempVect.normalized()
		context.window_manager.vf_showingvelocitylines = -1
		return {'FINISHED'}

# Inverts the list
class vf_invertvelocities(bpy.types.Operator):
	bl_idname = 'object.vf_invertvelocities'
	bl_label = 'Invert All'
	bl_description = 'Inverts the currently saved velocity list'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object != None and 'VF_Volume_' in context.active_object.name
	
	def execute(self, context):
		volmesh = context.active_object
		for i in range(len(volmesh.custom_vectorfield)):
			volmesh.custom_vectorfield[i].vvelocity[0] *= -1.0
			volmesh.custom_vectorfield[i].vvelocity[1] *= -1.0
			volmesh.custom_vectorfield[i].vvelocity[2] *= -1.0
		context.window_manager.vf_showingvelocitylines = -1
		return {'FINISHED'}


# Tools:

# Curve Wind Force:

# creates a wind tunnel from selected curve object
class calc_curvewindforce(bpy.types.Operator):
	bl_idname = 'object.calc_curvewindforce'
	bl_label = 'Curve Wind force'
	bl_description = 'create wind forces along a spline to direct velocities along it'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return (context.mode == "OBJECT" and context.active_object != None) and context.active_object.type == 'CURVE'
	
	def execute(self, context):
		curvepoints = []
		curveobj = context.active_object
		
		bpy.ops.object.empty_add(type='PLAIN_AXES')
		parentobj = context.active_object
		parentobj.name = 'CurveForce'
		
		if len(curveobj.data.splines[0].bezier_points) > 1:
			curvepoints = [v.co for v in curveobj.data.splines[0].bezier_points]
		else:
			curvepoints = [v.co for v in curveobj.data.splines[0].points]
		
		curveobj.parent = parentobj
		context.active_object.select_set(False)
		curveobj.select_set(True)
		
		previousnormal = Vector((0.0,0.0,0.0))
		
		lastStrength = context.window_manager.curveForce_strength
		lastDistance = context.window_manager.curveForce_maxDist
		
		for i in range(len(curvepoints)):
			cpoint = Vector((curvepoints[i][0],curvepoints[i][1],curvepoints[i][2]))
			
			bpy.ops.object.empty_add(type='SINGLE_ARROW',location=(cpoint))
			context.active_object.name = 'ForceObj'
			# turn into forcefield
			bpy.ops.object.forcefield_toggle()
			context.active_object.field.type = 'WIND'
			
			if context.window_manager.curveForce_trailout:
				if i > 0:
					lastStrength = lastStrength * 0.9
					lastDistance = lastDistance * 0.9
			
			context.active_object.field.strength = lastStrength
			context.active_object.field.use_max_distance = True
			context.active_object.field.distance_max = lastDistance
			context.active_object.field.falloff_power = context.window_manager.curveForce_falloffPower
			
			# get the curve's direction between points
			tempnorm = Vector((0,0,0))
			if (i < len(curvepoints) - 1):
				cpoint2 = Vector((curvepoints[i + 1][0],curvepoints[i + 1][1],curvepoints[i + 1][2]))
				tempnorm = cpoint - cpoint2
				if i > 0:
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
				previousnormal = tempnorm
			else:
				if curveobj.data.splines[0].use_cyclic_u or curveobj.data.splines[0].use_cyclic_u:
					cpoint2 = Vector((curvepoints[0][0],curvepoints[0][1],curvepoints[0][2]))
					tempnorm = cpoint - cpoint2
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
					previousnormal = tempnorm
				else:
					cpoint2 = Vector((curvepoints[i - 1][0],curvepoints[i - 1][1],curvepoints[i - 1][2]))
					tempnorm = cpoint2 - cpoint
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
					previousnormal = tempnorm
			
			if abs(tempnorm.length) > 0.0:
				z = Vector((0,0,1))
				angle = tempnorm.angle(z)
				axis = z.cross(tempnorm)
				mat = Matrix.Rotation(angle, 4, axis)
				mat_world = context.active_object.matrix_world @ mat
				context.active_object.matrix_world = mat_world
			
			context.active_object.parent = parentobj
			
		
		return {'FINISHED'}

# creates a wind tunnel from selected curve object
class edit_curvewindforce(bpy.types.Operator):
	bl_idname = 'object.edit_curvewindforce'
	bl_label = 'Curve Wind force'
	bl_description = 'Edit settings on the selected curve wind force object'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.mode == "OBJECT" and context.active_object != None:
			return 'CurveForce' in context.active_object.name
	
	def execute(self, context):
		newStrength = context.window_manager.curveForce_strength
		newDistance = context.window_manager.curveForce_maxDist
		newFalloff = context.window_manager.curveForce_falloffPower
		
		curveforceobj = context.active_object
		
		objlist = [obj for obj in context.scene.objects if obj.parent == curveforceobj]
		
		for obj in objlist:
			if 'ForceObj' in obj.name:
				obj.field.strength = newStrength
				obj.field.distance_max = newDistance
				obj.field.falloff_power = newFalloff
		
		return {'FINISHED'}




### Display

class toggle_vectorfieldinfo(bpy.types.Operator):
	bl_idname = "object.toggle_vectorfieldinfo"
	bl_label = 'Show Current VF Info'
	bl_description = 'Display information about the currently selected vector field'
	
	@classmethod
	def poll(cls, context):
		return context.active_object != None and 'VF_Volume_' in context.active_object.name
	
	def execute(self, context):
		return {'FINISHED'}


# Toggle velocities display as lines
class toggle_vectorfieldvelocities(bpy.types.Operator):
	bl_idname = "view3d.toggle_vectorfieldvelocities"
	bl_label = 'Show velocities'
	bl_description = 'Display velocities as 3D lines'
	
	_handle = None
	
	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT" and context.active_object != None and 'VF_Volume_' in context.active_object.name
	
	def modal(self, context, event):
		if context.area:
			context.area.tag_redraw()
		
		if context.window_manager.vf_showingvelocitylines == -1:
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			context.window_manager.vf_showingvelocitylines = 0
			return {"CANCELLED"}
		return {"PASS_THROUGH"}

	def invoke(self, context, event):
		#print ("test")
		if context.area.type == "VIEW_3D":
			if context.window_manager.vf_showingvelocitylines < 1:
				volmesh = context.active_object
				
				temploc = volmesh.parent.location
				vf_coords = [(Vector(v.vcoord) + temploc) for v in volmesh.custom_vectorfield]
				vf_velocities = [Vector(v.vvelocity) for v in volmesh.custom_vectorfield]
				vf_DrawVelocities = [Vector((0.0,0.0,0.0)) for i in range(len(volmesh.custom_vectorfield) * 2)]
				
				velcounter = 0
				for i in range(len(vf_coords)):
					vf_DrawVelocities[velcounter] = vf_coords[i].copy()
					velcounter += 1
					vf_DrawVelocities[velcounter] = vf_coords[i] + vf_velocities[i]
					velcounter += 1
				
				shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
				batch = batch_for_shader(shader, 'LINES', {"pos": vf_DrawVelocities})
				
				context.window_manager.vf_showingvelocitylines = 1
				color = Vector((context.window_manager.vf_velocitylinescolor[0], context.window_manager.vf_velocitylinescolor[1], context.window_manager.vf_velocitylinescolor[2], 1.0))
				self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_vectorfield,
					(shader, batch, color), 'WINDOW', 'POST_VIEW')
				
				context.window_manager.modal_handler_add(self)
				context.area.tag_redraw()
				return {"RUNNING_MODAL"}
			else:
				context.window_manager.vf_showingvelocitylines = -1
				return {'RUNNING_MODAL'}
		else:
			self.report({"WARNING"}, "View3D not found, can't run operator")
			return {"CANCELLED"}



# draw lines
def draw_vectorfield(shader, batch, color):
	shader.bind()
	shader.uniform_float("color", color)
	batch.draw(shader)

