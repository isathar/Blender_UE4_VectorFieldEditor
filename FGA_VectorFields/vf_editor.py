
import bpy

import math
from mathutils import Vector, Matrix

import bmesh

import bgl

from bpy.props import (StringProperty,FloatProperty,BoolProperty)

from bpy_extras.io_utils import (ImportHelper,ExportHelper,path_reference_mode)

import os.path

# saves velocities for export
class calc_vectorfieldvelocities(bpy.types.Operator):
	bl_idname = 'object.calc_vectorfieldvelocities'
	bl_label = 'Save VF EndLocations'
	bl_description = 'Calculate and save velocities'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.mode == "OBJECT" and context.active_object != None) and 'custom_vectorfield' in context.active_object
	
	def execute(self, context):
		invmult = -1.0 if context.window_manager.pvelocity_invert else 1.0
		
		useselection = context.window_manager.pvelocity_selection
		usedistance = context.window_manager.pvelocity_veltype == "DIST"
		useangularvelocity = context.window_manager.pvelocity_veltype == "ANGVEL"
		me = context.active_object.data
		me.update()
		
		particleslist = []
		mvertslist = []
		
		if context.window_manager.pvelocity_veltype == "VECT":
			tempvect = Vector(context.window_manager.pvelocity_dirvector)
			particleslist = [tempvect for p in context.active_object.particle_systems[0].particles]
			usedistance = False
		else:
			if usedistance:
				particleslist = [p.location for p in context.active_object.particle_systems[0].particles]
			else:
				if useangularvelocity:
					particleslist = [p.angular_velocity for p in context.active_object.particle_systems[0].particles]
				else:
					particleslist = [p.velocity for p in context.active_object.particle_systems[0].particles]
		
		if useselection:
			mvertslist = [v.select for v in me.vertices]
		
		# multiply
		if context.window_manager.pvelocity_genmode == 'MULT':
			if usedistance:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							tempvel = particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)
							context.active_object.custom_vectorfield[i].vvelocity[0] = context.active_object.custom_vectorfield[i].vvelocity[0] * (tempvel[0] * invmult)
							context.active_object.custom_vectorfield[i].vvelocity[1] = context.active_object.custom_vectorfield[i].vvelocity[1] * (tempvel[1] * invmult)
							context.active_object.custom_vectorfield[i].vvelocity[2] = context.active_object.custom_vectorfield[i].vvelocity[2] * (tempvel[2] * invmult)
				else:
					for i in range(len(particleslist)):
						tempvel = particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)
						context.active_object.custom_vectorfield[i].vvelocity[0] = context.active_object.custom_vectorfield[i].vvelocity[0] * (tempvel[0] * invmult)
						context.active_object.custom_vectorfield[i].vvelocity[1] = context.active_object.custom_vectorfield[i].vvelocity[1] * (tempvel[1] * invmult)
						context.active_object.custom_vectorfield[i].vvelocity[2] = context.active_object.custom_vectorfield[i].vvelocity[2] * (tempvel[2] * invmult)
			else:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity[0] = context.active_object.custom_vectorfield[i].vvelocity[0] * (particleslist[i][0] * invmult)
							context.active_object.custom_vectorfield[i].vvelocity[1] = context.active_object.custom_vectorfield[i].vvelocity[1] * (particleslist[i][1] * invmult)
							context.active_object.custom_vectorfield[i].vvelocity[2] = context.active_object.custom_vectorfield[i].vvelocity[2] * (particleslist[i][2] * invmult)
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity[0] = context.active_object.custom_vectorfield[i].vvelocity[0] * (particleslist[i][0] * invmult)
						context.active_object.custom_vectorfield[i].vvelocity[1] = context.active_object.custom_vectorfield[i].vvelocity[1] * (particleslist[i][1] * invmult)
						context.active_object.custom_vectorfield[i].vvelocity[2] = context.active_object.custom_vectorfield[i].vvelocity[2] * (particleslist[i][2] * invmult)
		
		# add
		elif context.window_manager.pvelocity_genmode == 'ADD':
			if usedistance:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity = Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)) * invmult)
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity = Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)) * invmult)
			else:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity = Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i]) * invmult)
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity = Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i]) * invmult)
		
		# average
		elif context.window_manager.pvelocity_genmode == 'AVG':
			if usedistance:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity = (Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)) * invmult)) * 0.5
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity = (Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)) * invmult)) * 0.5
			else:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity = (Vector(context.active_object.custom_vectorfield[i].vvelocity) + (particleslist[i] * invmult)) * 0.5
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity = (Vector(context.active_object.custom_vectorfield[i].vvelocity) + (particleslist[i] * invmult)) * 0.5
			
		# replace
		elif context.window_manager.pvelocity_genmode == 'REP':
			if usedistance:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity = (particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)) * invmult
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity = (particleslist[i] - Vector(context.active_object.custom_vectorfield[i].vstartloc)) * invmult
			else:
				if useselection:
					for i in range(len(particleslist)):
						if mvertslist[i]:
							context.active_object.custom_vectorfield[i].vvelocity = particleslist[i] * invmult
				else:
					for i in range(len(particleslist)):
						context.active_object.custom_vectorfield[i].vvelocity = particleslist[i] * invmult
			
			
		#angular_velocity
		return {'FINISHED'}

class vf_normalizevelocities(bpy.types.Operator):
	bl_idname = 'object.vf_normalizevelocities'
	bl_label = 'Normalize'
	bl_description = 'Normalizes the currently saved velocity list'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object != None and 'custom_vectorfield' in context.active_object
	
	def execute(self, context):
		for v in context.active_object.custom_vectorfield:
			v.vvelocity = Vector(v.vvelocity).normalized()
		
		return {'FINISHED'}

class vf_invertvelocities(bpy.types.Operator):
	bl_idname = 'object.vf_invertvelocities'
	bl_label = 'Invert All'
	bl_description = 'Inverts the currently saved velocity list'

	@classmethod
	def poll(cls, context):
		return context.active_object != None and 'custom_vectorfield' in context.active_object
	
	def execute(self, context):
		for v in context.active_object.custom_vectorfield:
			v.vvelocity = Vector(v.vvelocity) * -1.0
		
		return {'FINISHED'}

# creates a wind tunnel from a curve object
class calc_pathalongspline(bpy.types.Operator):
	bl_idname = 'object.calc_pathalongspline'
	bl_label = 'Path along spline'
	bl_description = 'create wind forces along a spline to direct velocities along it'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.mode == "OBJECT" and context.active_object != None) and context.active_object.type == 'CURVE'
	
	def execute(self, context):
		#print (context.active_object.type)
		curvepoints = []
		
		if len(context.active_object.data.splines[0].bezier_points) > 1:
			curvepoints = [v.co for v in context.active_object.data.splines[0].bezier_points]
		else:
			curvepoints = [v.co for v in context.active_object.data.splines[0].points]
		
		curveobj = context.active_object
		context.active_object.select = False
		
		previousnormal = Vector([0.0,0.0,0.0])
		
		lastStrength = context.window_manager.curveForce_strength
		lastDistance = context.window_manager.curveForce_maxDist
		
		for i in range(len(curvepoints)):
			cpoint = Vector([0.0,0.0,0.0])
			cpoint[0] = curvepoints[i][0]
			cpoint[1] = curvepoints[i][1]
			cpoint[2] = curvepoints[i][2]
			
			bpy.ops.mesh.primitive_plane_add(location=(cpoint))
			
			# make empty
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.delete(type='VERT')
			bpy.ops.object.mode_set(mode='OBJECT')
			
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
				cpoint2 = Vector([0.0,0.0,0.0])
				cpoint2[0] = curvepoints[i + 1][0]
				cpoint2[1] = curvepoints[i + 1][1]
				cpoint2[2] = curvepoints[i + 1][2]
				tempnorm = cpoint - cpoint2
				if i > 0:
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
				previousnormal = tempnorm
			else:
				if curveobj.data.splines[0].use_cyclic_u or curveobj.data.splines[0].use_cyclic_u:
					cpoint2 = Vector([0.0,0.0,0.0])
					cpoint2[0] = curvepoints[0][0]
					cpoint2[1] = curvepoints[0][1]
					cpoint2[2] = curvepoints[0][2]
					tempnorm = cpoint - cpoint2
					if abs(previousnormal.length) > 0.0:
						tempnorm = (tempnorm + previousnormal) / 2.0
					previousnormal = tempnorm
				else:
					cpoint2 = Vector([0.0,0.0,0.0])
					cpoint2[0] = curvepoints[i - 1][0]
					cpoint2[1] = curvepoints[i - 1][1]
					cpoint2[2] = curvepoints[i - 1][2]
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
			
			objs = context.active_object.constraints.new(type='COPY_LOCATION')
			objs.use_offset = True
			objs.target = curveobj
		
		return {'FINISHED'}
		
		
#####################################################
def build_vectorfield(context):
	densityVal = Vector(context.window_manager.vf_density)
	scaleVal = Vector(context.window_manager.vf_scale)
	
	
	volcount = 0
	#baseLoc = ((-1.0 * densityVal) * 0.25) + Vector([0.25,0.25,0.25])
	baseLoc = Vector([0.0,0.0,0.0])
	baseLoc[0] = ((-1.0 * (densityVal[0] * 0.25) + 0.25))
	baseLoc[1] = ((-1.0 * (densityVal[1] * 0.25) + 0.25))
	baseLoc[2] = ((-1.0 * (densityVal[2] * 0.25) + 0.25))
	
	totalvertscount = densityVal[0] * densityVal[1] * densityVal[2]
	xval = int(densityVal[0])
	yval = int(densityVal[1])
	zval = int(densityVal[2])
	
	#import timeit
	#start = timeit.default_timer()
	
	# create the volume
	bpy.ops.mesh.primitive_plane_add(location=(0.0,0.0,0.0))
	
	for v in range(len(context.scene.objects)):
		if ("VF_Volume" in str(context.scene.objects[v].name)):
			volcount += 1
	
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
	
	context.active_object.custom_vectorfield.clear()
	
	print(len(context.active_object.custom_vectorfield))
	zeroVect = Vector([0.0,0.0,0.0])
	
	# create vertices + initialize velocities list
	counter = 0
	for i in range(zval):
		for j in range(yval):
			for k in range(xval):
				tempV = (baseLoc + Vector([(k * 0.5),(j * 0.5),(i * 0.5)]))
				tempV[0] = tempV[0] * scaleVal[0]
				tempV[1] = tempV[1] * scaleVal[1]
				tempV[2] = tempV[2] * scaleVal[2]
				meshverts[counter].co = tempV
				tempvertdata = context.active_object.custom_vectorfield.add()
				tempvertdata.vvelocity = zeroVect
				tempvertdata.vstartloc = tempV
				tempvertdata.v_index[0] = k
				tempvertdata.v_index[1] = j
				tempvertdata.v_index[2] = i
				counter += 1
	
	me.update()
	
	meshverts = []
	
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
	
	context.active_object.scale[0] = (densityVal[0] * 0.25) * scaleVal[0]
	context.active_object.scale[1] = (densityVal[1] * 0.25) * scaleVal[1]
	context.active_object.scale[2] = (densityVal[2] * 0.25) * scaleVal[2]
	
	bpy.ops.object.transform_apply(scale=True)
	
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.delete(type='ONLY_FACE')
	bpy.ops.object.mode_set(mode='OBJECT')
	
	volMesh.parent = context.active_object
	
	#stop = timeit.default_timer()
	#print (stop - start)
	
	return volMesh.name

class create_vectorfield(bpy.types.Operator):
	bl_idname = 'object.create_vectorfield'
	bl_label = 'Create VectorField'
	bl_description = 'Create a new vector field from resolution and scale values'

	@classmethod
	def poll(cls, context):
		return context.mode=="OBJECT"
	
	def execute(self, context):
		build_vectorfield(context)
		
		return {'FINISHED'}


######Selection######

# select a slice of the volume on specified axes
class select_vfslice(bpy.types.Operator):
	bl_idname = "object.select_vfslice"
	bl_label = 'Select Slice'
	bl_description = 'Select a section of the vector field by axis'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object != None and "VF_Volume" in context.active_object.name
	
	def execute(self, context):
		me = context.active_object.data
		bm = ''
		meshverts = []
		
		if context.mode == "EDIT_MESH":
			bm = bmesh.from_edit_mesh(me)
			me.update()
			meshverts = [v for v in bm.verts]
		elif context.mode == "OBJECT":
			me.update()
			meshverts = [v for v in me.vertices]
		
		selectedlist = [i for i in range(len(meshverts)) if meshverts[i].select]
		indiceslist = [v.v_index for v in context.active_object.custom_vectorfield]
		
		# sanity check for large volumes
		selectedmax = 8
		
		for j in range(len(selectedlist)):
			indexvect = context.active_object.custom_vectorfield[selectedlist[j]].v_index
			for i in range(len(meshverts)):
				v = meshverts[i]
				if not v.select:
					curindexvect = indiceslist[i]
					if 'X' in context.window_manager.pselect_slice:
						if curindexvect[0] == indexvect[0]:
							v.select = True
					if 'Y' in context.window_manager.pselect_slice:
						if curindexvect[1] == indexvect[1]:
							v.select = True
					if 'Z' in context.window_manager.pselect_slice:
						if curindexvect[2] == indexvect[2]:
							v.select = True
			if j >= selectedmax:
				break
		
		return {'FINISHED'}


######Display########
class toggle_vectorfieldinfo(bpy.types.Operator):
	bl_idname = "object.toggle_vectorfieldinfo"
	bl_label = 'Show Current VF Info'
	bl_description = 'Display information about the currently selected vector field'
	
	@classmethod
	def poll(cls, context):
		return context.active_object != None and 'custom_vectorfield' in context.active_object
	
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
		return context.mode == "OBJECT" and context.active_object != None and 'custom_vectorfield' in context.active_object
	
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
	if 'custom_vectorfield' not in context.active_object:
		return
	
	bgl.glEnable(bgl.GL_BLEND)
	bgl.glColor3f(0.0,1.0,0.0)
	[draw_line(v.vstartloc, v.vvelocity) for v in context.active_object.custom_vectorfield]
	bgl.glDisable(bgl.GL_BLEND)


class update_vfdispoffsets(bpy.types.Operator):
	bl_idname = "view3d.update_vfdispoffsets"
	bl_label = 'Update Offsets'
	bl_description = 'Update location offsets in saved data to match volume bounds offset'
	
	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT" and context.active_object != None and 'custom_vectorfield' in context.active_object
	
	def execute(self, context):
		me = context.active_object.data
		me.update()
		
		meshverts = [v.co for v in me.vertices]
		volmesh = context.active_object.parent
		
		for i in range(len(meshverts)):
			context.active_object.custom_vectorfield[i].vstartloc = meshverts[i] + volmesh.location
		
		return {'FINISHED'}

#############################

# Import/Export functions:

def build_importedVectorField(tempvelList, tempOffset):
	# create blank vf
	volname = build_vectorfield(bpy.context)
	volmesh = bpy.context.scene.objects[volname]
	# copy imported velocities
	for l in range(len(tempvelList)):
		tempvertdata = volmesh.custom_vectorfield[l]
		tempvertdata.vvelocity = tempvelList[l]
	
	volmesh.parent.location = volmesh.parent.location + tempOffset
	
	for v in volmesh.custom_vectorfield:
		v.vstartloc = Vector(v.vstartloc) + tempOffset

def parse_fgafile(self, context):
	returnmessage = ""
	fgafilepath = self.filepath
	if os.path.exists(fgafilepath):
		if os.path.isfile(fgafilepath):
			file = open(fgafilepath, 'r')
			
			importvf_scalemult = context.window_manager.importvf_scalemult
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
						context.window_manager.vf_density[0] = int(flist[0])
						context.window_manager.vf_density[1] = int(flist[1])
						context.window_manager.vf_density[2] = int(flist[2])
					elif linecount == 1:
						tempMin[0] = flist[0]
						tempMin[1] = flist[1]
						tempMin[2] = flist[2]
					elif linecount == 2:
						tempscalemult = Vector([0.0,0.0,0.0])
						tempscalemult[0] = abs(flist[0] - tempMin[0])
						tempscalemult[1] = abs(flist[1] - tempMin[1])
						tempscalemult[2] = abs(flist[2] - tempMin[2])
						print("scaleMult: " + str(tempscalemult))
						context.window_manager.vf_scale[0] = (tempscalemult[0] / context.window_manager.vf_density[0]) * importvf_scalemult
						context.window_manager.vf_scale[1] = (tempscalemult[1] / context.window_manager.vf_density[1]) * importvf_scalemult
						context.window_manager.vf_scale[2] = (tempscalemult[2] / context.window_manager.vf_density[2]) * importvf_scalemult
						if context.window_manager.importvf_getoffset:
							tempOffset[0] = (((tempMin[0] + (tempscalemult[0] * 0.5)) * importvf_scalemult) * 0.5)
							tempOffset[1] = (((tempMin[1] + (tempscalemult[1] * 0.5)) * importvf_scalemult) * 0.5)
							tempOffset[2] = (((tempMin[2] + (tempscalemult[2] * 0.5)) * importvf_scalemult) * 0.5)
							print("offset:  " + str(tempOffset))
				else:
					if context.window_manager.importvf_velscale:
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


#Import

class import_vectorfieldfile(bpy.types.Operator, ImportHelper):
	bl_idname = "object.import_vectorfieldfile"
	bl_label = "Import FGA"
	bl_description = 'Import FGA file as a vector field'

	filename_ext = ".fga"
	filter_glob = StringProperty(default="*.fga", options={'HIDDEN'})
	
	def draw(self,context):
		layout = self.layout
		
		box = layout.box()
		row = box.row()
		row.prop(context.window_manager, 'importvf_scalemult', text='Import Scale')
		row = box.row()
		row.prop(context.window_manager, 'importvf_velscale', text='Scale Velocity')
		row = box.row()
		row.prop(context.window_manager, 'importvf_getoffset', text='Import Offset')
	
	
	def execute(self, context):
		retmessage = parse_fgafile(self, context)
		print ("FGA Import: " + retmessage + " (" + self.filepath + ")")
		
		return {'FINISHED'}


# Export:

def write_fgafile(self, context):
	usevelscale = context.window_manager.exportvf_velscale
	useoffset = context.window_manager.exportvf_locoffset
	
	tempDensity = Vector(context.active_object.vf_object_density)
	fgascale = Vector(context.active_object.vf_object_scale)
	
	file = open(self.filepath, "w", encoding="utf8", newline="\n")
	fw = file.write
	
	# Resolution:
	fw("%f,%f,%f," % (tempDensity[0],tempDensity[1],tempDensity[2]))
	
	# Minimum/Maximum XYZ:
	if context.window_manager.exportvf_allowmanualbounds:
		fw("\n%f,%f,%f," % (context.window_manager.exportvf_manualboundsneg[0],context.window_manager.exportvf_manualboundsneg[1],context.window_manager.exportvf_manualboundsneg[2]))
		fw("\n%f,%f,%f," % (context.window_manager.exportvf_manualboundspos[0],context.window_manager.exportvf_manualboundspos[1],context.window_manager.exportvf_manualboundspos[2]))
	else:
		if useoffset:
			offsetvect = context.active_object.parent.location * 2.0
			fw("\n%f,%f,%f," % ((((tempDensity[0] * -0.5) * fgascale[0]) + (offsetvect[0])) * context.window_manager.exportvf_scale,(((tempDensity[1] * -0.5) * fgascale[1]) + (offsetvect[1])) * context.window_manager.exportvf_scale,(((tempDensity[2] * -0.5) * fgascale[2]) + (offsetvect[2])) * context.window_manager.exportvf_scale))
			fw("\n%f,%f,%f," % ((((tempDensity[0] * 0.5) * fgascale[0]) + (offsetvect[0])) * context.window_manager.exportvf_scale,(((tempDensity[1] * 0.5) * fgascale[1]) + (offsetvect[1])) * context.window_manager.exportvf_scale,(((tempDensity[2] * 0.5) * fgascale[2]) + (offsetvect[2])) * context.window_manager.exportvf_scale))
		else: # centered
			fw("\n%f,%f,%f," % (((tempDensity[0] * -0.5) * fgascale[0]) * context.window_manager.exportvf_scale,((tempDensity[1] * -0.5) * fgascale[1]) * context.window_manager.exportvf_scale,((tempDensity[2] * -0.5) * fgascale[2]) * context.window_manager.exportvf_scale))
			fw("\n%f,%f,%f," % (((tempDensity[0] * 0.5) * fgascale[0]) * context.window_manager.exportvf_scale,((tempDensity[1] * 0.5) * fgascale[1]) * context.window_manager.exportvf_scale,((tempDensity[2] * 0.5) * fgascale[2]) * context.window_manager.exportvf_scale))
	
	# Velocities
	if usevelscale and not context.window_manager.exportvf_allowmanualbounds:
		for vec in context.active_object.custom_vectorfield:
			fw("\n%f,%f,%f," % (vec.vvelocity[0] * context.window_manager.exportvf_scale,vec.vvelocity[1] * context.window_manager.exportvf_scale,vec.vvelocity[2] * context.window_manager.exportvf_scale))
	else:
		if context.window_manager.exportvf_allowmanualbounds:
			for vec in context.active_object.custom_vectorfield:
				fw("\n%f,%f,%f," % (vec.vvelocity[0] * context.window_manager.exportvf_manualvelocityscale,vec.vvelocity[1] * context.window_manager.exportvf_manualvelocityscale,vec.vvelocity[2] * context.window_manager.exportvf_manualvelocityscale))
		else:
			for vec in context.active_object.custom_vectorfield:
				fw("\n%f,%f,%f," % (vec.vvelocity[0],vec.vvelocity[1],vec.vvelocity[2]))
	
	file.close()
	

class export_vectorfieldfile(bpy.types.Operator, ExportHelper):
	bl_idname = "object.export_vectorfieldfile"
	bl_label = "Export FGA"
	bl_description = 'Export selected volume as a FGA file'

	filename_ext = ".fga"
	filter_glob = StringProperty(default="*.fga", options={'HIDDEN'})
	
	def check_extension(self):
		return self.batch_mode == 'OFF'

	def check(self, context):
		is_def_change = super().check(context)
		return (is_def_change)
	
	def draw(self,context):
		layout = self.layout
		
		box = layout.box()
		box.row().prop(context.window_manager, 'exportvf_allowmanualbounds', text='Manual Bounds')
		if context.window_manager.exportvf_allowmanualbounds:
			box.row().column().prop(context.window_manager, 'exportvf_manualboundsneg', text='Minimum Bounds')
			box.row().column().prop(context.window_manager, 'exportvf_manualboundspos', text='Maximum Bounds')
			box.row().prop(context.window_manager, 'exportvf_manualvelocityscale', text='Velocity Scale:')
		else:
			box.row().prop(context.window_manager, 'exportvf_scale', text='Export Scale:')
			box.row().prop(context.window_manager, 'exportvf_velscale', text='Scale Velocity')
			box.row().prop(context.window_manager, 'exportvf_locoffset', text='Export Offset')
	
	def execute(self, context):
		if not self.filepath:
			raise Exception("filepath not set")
		else:
			write_fgafile(self, context)
		
		return {'FINISHED'}
