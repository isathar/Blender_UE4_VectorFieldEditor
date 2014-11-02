
import bpy

import math
from mathutils import Vector, Matrix

import bmesh

import bgl


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
		
		if context.window_manager.use_pvelocity:
			for i in range(len(context.active_object.particle_systems[0].particles)):
				newvelocity = context.active_object.particle_systems[0].particles[i].velocity
				context.active_object.custom_vectorfield[i].vvelocity = newvelocity
			
		return {'FINISHED'}


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
		
		for i in range(len(curvepoints)):
			cpoint = Vector(curvepoints[i])
			bpy.ops.mesh.primitive_plane_add(location=(cpoint))
			
			# make empty
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.delete(type='VERT')
			bpy.ops.object.mode_set(mode='OBJECT')
			
			# turn into forcefield
			bpy.ops.object.forcefield_toggle()
			context.active_object.field.type = 'WIND'
			context.active_object.field.strength = bpy.context.window_manager.curveForce_strength
			context.active_object.field.use_max_distance = True
			context.active_object.field.distance_max = bpy.context.window_manager.curveForce_maxDist
			context.active_object.field.falloff_power = bpy.context.window_manager.curveForce_falloffPower
			
			# get the curve's direction between points
			tempnorm = Vector([0,0,0])
			if (i < len(curvepoints) - 1):
				tempnorm = cpoint - Vector(curvepoints[i + 1])
			else:
				if curveobj.data.splines[0].use_cyclic_u or curveobj.data.splines[0].use_cyclic_u:
					tempnorm = cpoint - Vector(curvepoints[0])
				else:
					tempnorm = Vector(curvepoints[i - 1]) - cpoint
					
			if abs(tempnorm.length) > 0:
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
		vertsList = []
		volcount = 0
		baseLoc = ((-1.0 * densityVal) * 0.25) * scaleVal
		totalvertscount = densityVal[0] * densityVal[1] * densityVal[2]
		xval = int(densityVal[0])
		yval = int(densityVal[1])
		zval = int(densityVal[2])
		
		#import timeit
		#start = timeit.default_timer()
		
		# create the volume
		bpy.ops.mesh.primitive_plane_add(location=(0.0, 0.0, 0.0))
		
		for v in range(len(context.scene.objects)):
			if ("VF_Volume" in str(context.scene.objects[v].name)):
				volcount += 1
		
		context.active_object.name = 'VF_Volume_' + str(volcount)
		parentObj = context.active_object
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.delete(type='VERT')
		bpy.ops.object.mode_set(mode='OBJECT')
		
		
		# create vertices
		for i in range(zval):
			for j in range(yval):
				for k in range(xval):
					vertsList.append(Vector([baseLoc[0] + ((k * 0.5) * scaleVal) + (0.25 * scaleVal),baseLoc[1] + ((j * 0.5) * scaleVal) + (0.25 * scaleVal),baseLoc[2] + ((i * 0.5) * scaleVal) + (0.25 * scaleVal)]))
		
		me = context.active_object.data
		me.update()
		me.vertices.add(totalvertscount)
		me.update()
		
		# save startlocations for display
		context.active_object.custom_vectorfield.clear()
		
		for l in range(len(me.vertices)):
			me.vertices[l].co = vertsList[l]
			tempvertdata = context.active_object.custom_vectorfield.add()
			tempvertdata.vvelocity = Vector([0.0,0.0,0.0])
			tempvertdata.vstartloc = vertsList[l]
		
		
		# create the particle system
		bpy.ops.object.particle_system_add()
		psettings = context.active_object.particle_systems[0].settings
		psettings.count = totalvertscount
		psettings.emit_from = 'VERT'
		psettings.normal_factor = 0.0
		psettings.use_emit_random = False
		psettings.frame_end = 1
		psettings.lifetime = 32
		psettings.grid_resolution = 1
		
		volMesh = context.active_object
		
		
		# create the bounding box
		bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
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
def draw_line(vertexloc, vertexnorm, color, thickness, dispscale):
	x1 = vertexloc[0]
	y1 = vertexloc[1]
	z1 = vertexloc[2]

	x2 = (vertexnorm[0] * dispscale) + vertexloc[0]
	y2 = (vertexnorm[1] * dispscale) + vertexloc[1]
	z2 = (vertexnorm[2] * dispscale) + vertexloc[2]

	bgl.glLineWidth(thickness)
	bgl.glColor4f(*color)

	# draw line
	bgl.glBegin(bgl.GL_LINES)
	bgl.glVertex3f(x1,y1,z1)
	bgl.glVertex3f(x2,y2,z2)
	bgl.glEnd()


# iterate through list to draw each line
def draw_vectorfield(self, context):
	if ('custom_vectorfield' not in bpy.context.active_object):
		return
	
	dispscale = 0.25
	col = [0.0,1.0,0.0]
	dispcol = (col[0],col[1],col[2],1.0)
	
	bgl.glEnable(bgl.GL_BLEND)
	
	showList = [v for v in context.active_object.custom_vectorfield if abs(Vector(v.vvelocity).length) > 0.0]
	
	for i in range(len(showList)):
		draw_line(showList[i].vstartloc, showList[i].vvelocity, dispcol, 2.0, dispscale)
			
	bgl.glDisable(bgl.GL_BLEND)

#############################
