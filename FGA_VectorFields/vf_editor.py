### Editor Functions

import bpy
import bgl
import os.path

from mathutils import Vector, Matrix

from . import vf_vdata


### Create

# Creates a new vector field from parameters
def build_vectorfield(context):
	densityVal = Vector(context.window_manager.vf_density)
	scaleVal = Vector(context.window_manager.vf_scale)
	
	volcount = 0
	baseLoc = Vector(
		((-1.0 * (densityVal[0] * 0.5) + 0.5),
			(-1.0 * (densityVal[1] * 0.5) + 0.5),
			(-1.0 * (densityVal[2] * 0.5) + 0.5)
		)
	)
	
	totalvertscount = densityVal[0] * densityVal[1] * densityVal[2]
	xval = int(densityVal[0])
	yval = int(densityVal[1])
	zval = int(densityVal[2])
	
	#import timeit
	#start = timeit.default_timer()
	
	for v in range(len(context.scene.objects)):
		if ("VF_Volume" in str(context.scene.objects[v].name)):
			volcount += 1
	
	# create the volume
	bpy.ops.mesh.primitive_plane_add(location=(0.0,0.0,0.0))
	
	context.active_object.name = 'VF_Volume_' + str(volcount)
	parentObj = context.active_object
	
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.delete(type='VERT')
	bpy.ops.object.mode_set(mode='OBJECT')
	
	bpy.ops.object.particle_system_add()
	psettings = context.active_object.particle_systems[0].settings
	
	me = context.active_object.data
	me.update()
	me.vertices.add(totalvertscount)
	
	meshverts = [v for v in me.vertices]
	
	context.active_object.vf_object_density[0] = xval
	context.active_object.vf_object_density[1] = yval
	context.active_object.vf_object_density[2] = zval
	
	context.active_object.vf_object_scale = scaleVal
	
	vf_vdata.particle_velocitieslist.clear()
	vf_vdata.particle_startlocs.clear()
	
	zeroVect = Vector([0.0,0.0,0.0])
	
	# create vertices + initialize velocities list
	counter = 0
	for i in range(zval):
		for j in range(yval):
			for k in range(xval):
				tempV = Vector(
					((baseLoc[0] + (k)) * scaleVal[0],
						(baseLoc[1] + (j)) * scaleVal[1],
						(baseLoc[2] + (i)) * scaleVal[2]
					)
				)
				meshverts[counter].co = tempV
				vf_vdata.particle_velocitieslist.append(zeroVect)
				vf_vdata.particle_startlocs.append(tempV)
				
				counter += 1
	
	me.update()
	
	del meshverts[:]
	
	# create the particle system
	psettings.count = totalvertscount
	psettings.emit_from = 'VERT'
	psettings.normal_factor = 0.0
	psettings.use_emit_random = False
	psettings.frame_end = 1
	psettings.lifetime = 32
	psettings.grid_resolution = 1
	psettings.use_rotations = True
	psettings.use_dynamic_rotation = True
	if context.window_manager.vf_disablegravity:
		psettings.effector_weights.gravity = 0.0
	
	volMesh = context.active_object
	
	# create the bounding box
	bpy.ops.mesh.primitive_cube_add(location=(0.0,0.0,0.0))
	context.active_object.name = 'VF_Bounds_' + str(volcount)
	
	# match scale to the volume
	context.active_object.scale[0] = (densityVal[0] * 0.5) * scaleVal[0]
	context.active_object.scale[1] = (densityVal[1] * 0.5) * scaleVal[1]
	context.active_object.scale[2] = (densityVal[2] * 0.5) * scaleVal[2]
	bpy.ops.object.transform_apply(scale=True)
	
	# - rewrite at some point so modes aren't messed with:
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.delete(type='ONLY_FACE')
	bpy.ops.object.mode_set(mode='OBJECT')
	
	volMesh.parent = context.active_object
	
	save_velobjectdata(volMesh)
	
	#stop = timeit.default_timer()
	#print (stop - start)
	
	return volMesh.name


class create_vectorfield(bpy.types.Operator):
	bl_idname = 'object.create_vectorfield'
	bl_label = 'Create VectorField'
	bl_description = 'Create a new vector field from resolution and scale values'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode=="OBJECT"
	
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
		
		me = context.active_object.data
		me.update()
		
		particleslist = []
		
		## Get velocities
		if context.window_manager.pvelocity_veltype == "VECT":
			tempvect = Vector(context.window_manager.pvelocity_dirvector)
			particleslist = [tempvect for p in context.active_object.particle_systems[0].particles]
		elif context.window_manager.pvelocity_veltype == "DIST":
			tplist = context.active_object.particle_systems[0].particles
			particleslist = [(tplist[i].location - vf_vdata.particle_startlocs[i]) for i in range(len(tplist))]
		elif context.window_manager.pvelocity_veltype == "ANGVEL":
			particleslist = [p.angular_velocity for p in context.active_object.particle_systems[0].particles]
		elif context.window_manager.pvelocity_veltype == "PNT":
			cursorloc = context.scene.cursor_location
			particleslist = [(v.co - cursorloc).normalized() for v in me.vertices]
		else:
			particleslist = [p.velocity for p in context.active_object.particle_systems[0].particles]
		
		mvertslist = []
		if useselection:
			mvertslist = [v.select for v in me.vertices]
		
		
		## Blend with List / calculate
		
		# multiply
		if context.window_manager.pvelocity_genmode == 'MULT':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_vdata.particle_velocitieslist[i] = Vector(
							(vf_vdata.particle_velocitieslist[i][0] * (particleslist[i][0] * invmult), 
							vf_vdata.particle_velocitieslist[i][1] * (particleslist[i][1] * invmult), 
							vf_vdata.particle_velocitieslist[i][2] * (particleslist[i][2] * invmult))
						)
			else:
				for i in range(len(particleslist)):
					vf_vdata.particle_velocitieslist[i] = Vector(
						(vf_vdata.particle_velocitieslist[i][0] * (particleslist[i][0] * invmult), 
						vf_vdata.particle_velocitieslist[i][1] * (particleslist[i][1] * invmult), 
						vf_vdata.particle_velocitieslist[i][2] * (particleslist[i][2] * invmult))
					)
			
		# add
		elif context.window_manager.pvelocity_genmode == 'ADD':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_vdata.particle_velocitieslist[i] = vf_vdata.particle_velocitieslist[i] + ((particleslist[i]) * invmult)
			else:
				for i in range(len(particleslist)):
					vf_vdata.particle_velocitieslist[i] = vf_vdata.particle_velocitieslist[i] + ((particleslist[i]) * invmult)
			
		# average
		elif context.window_manager.pvelocity_genmode == 'AVG':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_vdata.particle_velocitieslist[i] = (vf_vdata.particle_velocitieslist[i] + (particleslist[i] * invmult)) * 0.5
			else:
				for i in range(len(particleslist)):
					vf_vdata.particle_velocitieslist[i] = (vf_vdata.particle_velocitieslist[i] + (particleslist[i] * invmult)) * 0.5
			
		# replace
		elif context.window_manager.pvelocity_genmode == 'REP':
			if useselection:
				for i in range(len(particleslist)):
					if mvertslist[i]:
						vf_vdata.particle_velocitieslist[i] = particleslist[i] * invmult
			else:
				for i in range(len(particleslist)):
					vf_vdata.particle_velocitieslist[i] = particleslist[i] * invmult
		
		
		save_velobjectdata(context.active_object)
		
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
		for i in range(len(vf_vdata.particle_velocitieslist)):
			vf_vdata.particle_velocitieslist[i] = vf_vdata.particle_velocitieslist[i].normalized()
		
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
		for i in range(len(vf_vdata.particle_velocitieslist)):
			vf_vdata.particle_velocitieslist[i] = vf_vdata.particle_velocitieslist[i] * -1.0
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
		context.active_object.select = False
		curveobj.select = True
		
		previousnormal = Vector([0.0,0.0,0.0])
		
		lastStrength = context.window_manager.curveForce_strength
		lastDistance = context.window_manager.curveForce_maxDist
		
		for i in range(len(curvepoints)):
			cpoint = Vector([curvepoints[i][0],curvepoints[i][1],curvepoints[i][2]])
			
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
			tempnorm = Vector([0,0,0])
			if (i < len(curvepoints) - 1):
				cpoint2 = Vector([curvepoints[i + 1][0],curvepoints[i + 1][1],curvepoints[i + 1][2]])
				tempnorm = cpoint - cpoint2
				if i > 0:
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
				previousnormal = tempnorm
			else:
				if curveobj.data.splines[0].use_cyclic_u or curveobj.data.splines[0].use_cyclic_u:
					cpoint2 = Vector([curvepoints[0][0],curvepoints[0][1],curvepoints[0][2]])
					tempnorm = cpoint - cpoint2
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
					previousnormal = tempnorm
				else:
					cpoint2 = Vector([curvepoints[i - 1][0],curvepoints[i - 1][1],curvepoints[i - 1][2]])
					tempnorm = cpoint2 - cpoint
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
					previousnormal = tempnorm
			
			if abs(tempnorm.length) > 0.0:
				z = Vector((0,0,1))
				angle = tempnorm.angle(z)
				axis = z.cross(tempnorm)
				mat = Matrix.Rotation(angle, 4, axis)
				mat_world = context.active_object.matrix_world * mat
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
		if context.area.type == "VIEW_3D":
			if context.window_manager.vf_showingvelocitylines < 1:
				context.window_manager.vf_showingvelocitylines = 1
				self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_vectorfield,
					(self, context), 'WINDOW', 'POST_VIEW')
				context.window_manager.modal_handler_add(self)
				context.area.tag_redraw()
				return {"RUNNING_MODAL"}
			else:
				context.window_manager.vf_showingvelocitylines = -1
				return {'RUNNING_MODAL'}
		else:
			self.report({"WARNING"}, "View3D not found, can't run operator")
			return {"CANCELLED"}


# draw single gl line
def draw_line(vertexloc, vertexnorm):
	bgl.glBegin(bgl.GL_LINES)
	bgl.glVertex3f(vertexloc[0],vertexloc[1],vertexloc[2])
	bgl.glVertex3f(vertexnorm[0] + vertexloc[0],vertexnorm[1] + vertexloc[1],vertexnorm[2] + vertexloc[2])
	bgl.glEnd()


# iterate through list to draw each line
def draw_vectorfield(self, context):
	bgl.glEnable(bgl.GL_BLEND)
	bgl.glColor3f(0.0,1.0,0.0)
	
	for i in range(len(vf_vdata.particle_velocitieslist)):
		draw_line(vf_vdata.particle_startlocs[i],vf_vdata.particle_velocitieslist[i])
	
	bgl.glDisable(bgl.GL_BLEND)


class update_vfdispoffsets(bpy.types.Operator):
	bl_idname = "view3d.update_vfdispoffsets"
	bl_label = 'Update Offsets'
	bl_description = 'Update location offsets in saved data to match volume bounds offset'
	
	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT" and context.active_object != None and 'VF_Volume_' in context.active_object.name
	
	def execute(self, context):
		me = context.active_object.data
		me.update()
		
		meshverts = [v.co for v in me.vertices]
		volmesh = context.active_object.parent
		
		for i in range(len(meshverts)):
			vf_vdata.particle_startlocs[i] = Vector(meshverts[i] + volmesh.location)
		
		return {'FINISHED'}


class update_vfeditorvars(bpy.types.Operator):
	bl_idname = "view3d.update_vfeditorvars"
	bl_label = 'Update Editor Data'
	bl_description = 'Updates data used by editor. (use if current data is not synced with selected volume)'
	
	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT" and context.active_object != None and 'VF_Volume_' in context.active_object.name
	
	def execute(self, context):
		me = context.active_object.data
		me.update()
		meshverts = [v.co for v in me.vertices]
		
		volmesh = context.active_object.parent
		
		vf_vdata.particle_velocitieslist.clear()
		vf_vdata.particle_startlocs.clear()
		
		for i in range(len(context.active_object.custom_vectorfield)):
			vf_vdata.particle_velocitieslist.append(Vector(context.active_object.custom_vectorfield[i].vvelocity))
			vf_vdata.particle_startlocs.append(Vector(meshverts[i] + volmesh.location))
		
		return {'FINISHED'}

def save_velobjectdata(volmesh):
	if 'custom_vectorfield' not in volmesh:
		volmesh['custom_vectorfield'] = []
	
	volmesh.custom_vectorfield.clear()
	for v in vf_vdata.particle_velocitieslist:
		tempvertdata = volmesh.custom_vectorfield.add()
		tempvertdata.vvelocity = v


### Import

# create new vector field from imported data
def build_importedVectorField(tempvelList, tempOffset):
	# create blank vf
	volname = build_vectorfield(bpy.context)
	volmesh = bpy.context.scene.objects[volname]
	# copy imported velocities
	for i in range(len(tempvelList)):
		volmesh.custom_vectorfield[i].vvelocity = tempvelList[i]
		vf_vdata.particle_velocitieslist[i] = tempvelList[i]
		vf_vdata.particle_startlocs[i] = vf_vdata.particle_startlocs[i] + tempOffset
	
	volmesh.parent.location = volmesh.parent.location + tempOffset

# read data from file
def parse_fgafile(self, context):
	returnmessage = ""
	fgafilepath = self.filepath
	if os.path.exists(fgafilepath):
		if os.path.isfile(fgafilepath):
			file = open(fgafilepath, 'r')
			importvf_scalemult = self.importvf_scalemult
			linecount = 0
			tempvelList = []
			tempMin = Vector([0.0,0.0,0.0])
			tempOffset = Vector([0.0,0.0,0.0])
			tempscalemult = Vector([0.0,0.0,0.0])
			
			for line in file:
				slist = []
				slist = line.split(',')
				if len(slist) > 3:
					slist.remove(slist[3])
				
				flist = [float(s) for s in slist]
				
				if linecount <= 2:
					if linecount == 0:
						# Resolution
						context.window_manager.vf_density[0] = int(flist[0])
						context.window_manager.vf_density[1] = int(flist[1])
						context.window_manager.vf_density[2] = int(flist[2])
					elif linecount == 1:
						# Min bounds
						tempMin[0] = flist[0]
						tempMin[1] = flist[1]
						tempMin[2] = flist[2]
					elif linecount == 2:
						# Max bounds, calc offset + scale
						tempscalemult = Vector([0.0,0.0,0.0])
						tempscalemult[0] = abs(flist[0] - tempMin[0])
						tempscalemult[1] = abs(flist[1] - tempMin[1])
						tempscalemult[2] = abs(flist[2] - tempMin[2])
						context.window_manager.vf_scale[0] = (tempscalemult[0] / context.window_manager.vf_density[0]) * importvf_scalemult
						context.window_manager.vf_scale[1] = (tempscalemult[1] / context.window_manager.vf_density[1]) * importvf_scalemult
						context.window_manager.vf_scale[2] = (tempscalemult[2] / context.window_manager.vf_density[2]) * importvf_scalemult
						if self.importvf_getoffset:
							tempOffset[0] = (((tempMin[0] + (tempscalemult[0] * 0.5)) * importvf_scalemult))
							tempOffset[1] = (((tempMin[1] + (tempscalemult[1] * 0.5)) * importvf_scalemult))
							tempOffset[2] = (((tempMin[2] + (tempscalemult[2] * 0.5)) * importvf_scalemult))
				else:
					# Velocities
					if self.importvf_velscale:
						tempvelList.append(Vector([flist[0] * importvf_scalemult,flist[1] * importvf_scalemult,flist[2] * importvf_scalemult]))
					else:
						tempvelList.append(Vector(flist))
				linecount += 1
			
			if linecount < 3:
				returnmessage = "Import Failed: File is missing data"
			else:
				if len(tempvelList) > 0:
					returnmessage = "Import Successful"
					build_importedVectorField(tempvelList, tempOffset)
			file.close()
		else:
			returnmessage = "Import Failed: File not found"
	else:
		returnmessage = "Import Failed: Path not found"
	
	return returnmessage



### Export

def write_fgafile(self, context):
	usevelscale = self.exportvf_velscale
	useoffset = self.exportvf_locoffset
	
	tempDensity = Vector(context.active_object.vf_object_density)
	fgascale = Vector(context.active_object.vf_object_scale)
	
	file = open(self.filepath, "w", encoding="utf8", newline="\n")
	fw = file.write
	
	# Resolution:
	fw("%f,%f,%f," % (tempDensity[0],tempDensity[1],tempDensity[2]))
	
	# Minimum/Maximum Bounds:
	if self.exportvf_allowmanualbounds:
		fw("\n%f,%f,%f," % (
			self.exportvf_manualboundsneg[0],
			self.exportvf_manualboundsneg[1],
			self.exportvf_manualboundsneg[2])
		)
		fw("\n%f,%f,%f," % (
			self.exportvf_manualboundspos[0],
			self.exportvf_manualboundspos[1],
			self.exportvf_manualboundspos[2])
		)
	else:
		if useoffset:
			offsetvect = context.active_object.parent.location
			fw("\n%f,%f,%f," % (
				(((tempDensity[0] * -0.5) * fgascale[0]) + (offsetvect[0])) * self.exportvf_scale,
				(((tempDensity[1] * -0.5) * fgascale[1]) + (offsetvect[1])) * self.exportvf_scale,
				(((tempDensity[2] * -0.5) * fgascale[2]) + (offsetvect[2])) * self.exportvf_scale)
			)
			fw("\n%f,%f,%f," % (
				(((tempDensity[0] * 0.5) * fgascale[0]) + (offsetvect[0])) * self.exportvf_scale,
				(((tempDensity[1] * 0.5) * fgascale[1]) + (offsetvect[1])) * self.exportvf_scale,
				(((tempDensity[2] * 0.5) * fgascale[2]) + (offsetvect[2])) * self.exportvf_scale)
			)
		else: # centered
			fw("\n%f,%f,%f," % (
				((tempDensity[0] * -0.5) * fgascale[0]) * self.exportvf_scale,
				((tempDensity[1] * -0.5) * fgascale[1]) * self.exportvf_scale,
				((tempDensity[2] * -0.5) * fgascale[2]) * self.exportvf_scale)
			)
			fw("\n%f,%f,%f," % (
				((tempDensity[0] * 0.5) * fgascale[0]) * self.exportvf_scale,
				((tempDensity[1] * 0.5) * fgascale[1]) * self.exportvf_scale,
				((tempDensity[2] * 0.5) * fgascale[2]) * self.exportvf_scale)
			)
	
	# Velocities
	if usevelscale and not self.exportvf_allowmanualbounds:
		for vec in context.active_object.custom_vectorfield:
			fw("\n%f,%f,%f," % (
				vec.vvelocity[0] * self.exportvf_scale,
				vec.vvelocity[1] * self.exportvf_scale,
				vec.vvelocity[2] * self.exportvf_scale)
			)
	else:
		if self.exportvf_allowmanualbounds:
			for vec in context.active_object.custom_vectorfield:
				fw("\n%f,%f,%f," % (
					vec.vvelocity[0] * self.exportvf_manualvelocityscale,
					vec.vvelocity[1] * self.exportvf_manualvelocityscale,
					vec.vvelocity[2] * self.exportvf_manualvelocityscale)
				)
		else:
			for vec in context.active_object.custom_vectorfield:
				fw("\n%f,%f,%f," % (
					vec.vvelocity[0],
					vec.vvelocity[1],
					vec.vvelocity[2])
				)
	
	file.close()


### Cleanup

def clear_data():
	vf_vdata.clearvars()
