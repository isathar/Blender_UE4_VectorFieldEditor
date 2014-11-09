
import bpy

import math
from mathutils import Vector, Matrix

import bmesh

import bgl


# saves velocities for export
class calc_vectorfieldvelocities(bpy.types.Operator):
	bl_idname = 'object.calc_vectorfieldvelocities'
	bl_label = 'Save VF EndLocations'
	bl_description = 'Calculates velocities to be exported'

	@classmethod
	def poll(cls, context):
		if context.active_object == None:
			return False
		elif not ("VF_Volume" in str(context.active_object.name)):
			return False
		else:
			return True
	
	def execute(self, context):
		invmult = -1.0 if context.window_manager.invert_pvelocity else 1.0
		particleslist = [p for p in context.active_object.particle_systems[0].particles]
		
		# additive
		if bpy.context.window_manager.velocities_genmode == 'ADD':
			for i in range(len(particleslist)):
				if context.window_manager.normalize_pvelocity:
					context.active_object.custom_vectorfield[i].vvelocity = Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i].velocity.normalized()) * invmult)
				else:
					context.active_object.custom_vectorfield[i].vvelocity = Vector(context.active_object.custom_vectorfield[i].vvelocity) + ((particleslist[i].velocity) * invmult)
		# average
		elif bpy.context.window_manager.velocities_genmode == 'AVG':
			for i in range(len(particleslist)):
				if context.window_manager.normalize_pvelocity:
					context.active_object.custom_vectorfield[i].vvelocity = (Vector(context.active_object.custom_vectorfield[i].vvelocity) + (particleslist[i].velocity.normalized() * invmult)) * 0.5
				else:
					context.active_object.custom_vectorfield[i].vvelocity = (Vector(context.active_object.custom_vectorfield[i].vvelocity) + (particleslist[i].velocity * invmult)) * 0.5
		# replace
		else:
			for i in range(len(particleslist)):
				if context.window_manager.normalize_pvelocity:
					context.active_object.custom_vectorfield[i].vvelocity = particleslist[i].velocity.normalized() * invmult
				else:
					context.active_object.custom_vectorfield[i].vvelocity = particleslist[i].velocity * invmult
		return {'FINISHED'}


# creates a wind tunnel from a curve object
class calc_pathalongspline(bpy.types.Operator):
	bl_idname = 'object.calc_pathalongspline'
	bl_label = 'Path along psline'
	bl_description = 'creates wind forces along a spline to direct velocities along it'

	@classmethod
	def poll(cls, context):
		if context.active_object == None:
			return False
		elif context.active_object.type != 'CURVE':
			return False
		else:
			return True
	
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
		
		lastStrength = bpy.context.window_manager.curveForce_strength
		lastDistance = bpy.context.window_manager.curveForce_maxDist
		
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
			
			if bpy.context.window_manager.curveForce_trailout:
				if i > 0:
					lastStrength = lastStrength * 0.9
					lastDistance = lastDistance * 0.9
			
			context.active_object.field.strength = lastStrength
			context.active_object.field.use_max_distance = True
			context.active_object.field.distance_max = lastDistance
			context.active_object.field.falloff_power = bpy.context.window_manager.curveForce_falloffPower
			
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

class create_vectorfield(bpy.types.Operator):
	bl_idname = 'object.create_vectorfield'
	bl_label = 'Create VectorField'
	bl_description = 'Creates a new vector field'

	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		densityVal = Vector(context.window_manager.fieldDensity)
		scaleVal = context.window_manager.fieldScale
		
		volcount = 0
		baseLoc = ((-1.0 * densityVal) * 0.25) + Vector([0.25,0.25,0.25])
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
		
		context.active_object.custom_vectorfield.clear()
		
		# create vertices + initialize velocities list
		counter = 0
		for i in range(zval):
			for j in range(yval):
				for k in range(xval):
					tempV = (baseLoc + Vector([(k * 0.5),(j * 0.5),(i * 0.5)])) * scaleVal
					meshverts[counter].co = tempV
					tempvertdata = context.active_object.custom_vectorfield.add()
					tempvertdata.vvelocity = Vector([0.0,0.0,0.0])
					tempvertdata.vstartloc = tempV
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
		if context.window_manager.field_disablegravity:
			psettings.effector_weights.gravity = 0.0
		
		volMesh = context.active_object
		
		# create the bounding box
		bpy.ops.mesh.primitive_cube_add(location=(0.0,0.0,0.0))
		context.active_object.name = 'VF_Bounds_' + str(volcount)
		
		context.active_object.scale = (densityVal * 0.25) * scaleVal
		bpy.ops.object.transform_apply(scale=True)
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.delete(type='ONLY_FACE')
		bpy.ops.object.mode_set(mode='OBJECT')
		
		volMesh.parent = context.active_object
		
		#stop = timeit.default_timer()
		#print (stop - start)
		
		return {'FINISHED'}


######Display########

# Toggle velocities display as lines
class toggle_vectorfieldvelocities(bpy.types.Operator):
	bl_idname = "view3d.toggle_vectorfieldvelocities"
	bl_label = 'Show velocities'

	_handle = None
	
	@classmethod
	def poll(cls, context):
		if context.active_object == None:
			return False
		elif not ("VF_Volume" in str(context.active_object.name)):
			return False
		elif not ('custom_vectorfield' in bpy.context.active_object):
			return False
		else: 
			return True
	
	def modal(self, context, event):
		if context.area:
			context.area.tag_redraw()

		if bpy.context.window_manager.showing_vectorfield == -1:
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			bpy.context.window_manager.showing_vectorfield = 0
			return {"CANCELLED"}
		return {"PASS_THROUGH"}

	def invoke(self, context, event):
		if context.area.type == "VIEW_3D":
			if bpy.context.window_manager.showing_vectorfield < 1:
				bpy.context.window_manager.showing_vectorfield = 1
				self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_vectorfield,
					(self, context), 'WINDOW', 'POST_VIEW')
				context.window_manager.modal_handler_add(self)
				context.area.tag_redraw()
				return {"RUNNING_MODAL"}
			else:
				bpy.context.window_manager.showing_vectorfield = -1
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
	if ('custom_vectorfield' not in bpy.context.active_object):
		return
	
	bgl.glEnable(bgl.GL_BLEND)
	#bgl.glLineWidth(2.0)
	bgl.glColor3f(0.0,1.0,0.0)
	[draw_line(v.vstartloc, v.vvelocity) for v in context.active_object.custom_vectorfield]
	bgl.glDisable(bgl.GL_BLEND)


#############################
