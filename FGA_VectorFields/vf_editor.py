
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
		context.active_object.custom_vectorfield.clear()
		
		if context.window_manager.use_pvelocity:
			for i in range(len(context.active_object.particle_systems[0].particles)):
				newvelocity = context.active_object.particle_systems[0].particles[i].velocity
				tempvel = context.active_object.custom_vectorfield.add()
				tempvel.vvelocity = newvelocity
			
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
		print (context.active_object.type)
		curvepoints = context.active_object.data.splines[0].bezier_points
		
		if len(curvepoints) < 1:
			curvepoints = context.active_object.data.splines[0].points
		
		curveobj = context.active_object
		
		context.active_object.select = False
		
		for i in range(len(curvepoints)):
			tempLoc = Vector([0,0,0])
			tempLoc[0] = curvepoints[i].co[0]
			tempLoc[1] = curvepoints[i].co[1]
			tempLoc[2] = curvepoints[i].co[2]
			
			bpy.ops.mesh.primitive_plane_add(location=(tempLoc))
			
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
				tempnorm = Vector([0,0,0])
				tempnorm[0] = curvepoints[i].co[0] - curvepoints[i + 1].co[0]
				tempnorm[1] = curvepoints[i].co[1] - curvepoints[i + 1].co[1]
				tempnorm[2] = curvepoints[i].co[2] - curvepoints[i + 1].co[2]
			else:
				if curveobj.data.splines[0].use_cyclic_u or curveobj.data.splines[0].use_cyclic_u:
					tempnorm = Vector([0,0,0])
					tempnorm[0] = curvepoints[i].co[0] - curvepoints[0].co[0]
					tempnorm[1] = curvepoints[i].co[1] - curvepoints[0].co[1]
					tempnorm[2] = curvepoints[i].co[2] - curvepoints[0].co[2]
				else:
					tempnorm = Vector([0,0,0])
					tempnorm[0] = curvepoints[i - 1].co[0] - curvepoints[i].co[0]
					tempnorm[1] = curvepoints[i - 1].co[1] - curvepoints[i].co[1]
					tempnorm[2] = curvepoints[i - 1].co[1] - curvepoints[i].co[2]
			
			# orient forcefield rotation to direction
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
		bpy.ops.group.create(name='VFGroup')
		
		bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
		
		volcount = 0
		for v in range(len(context.scene.objects)):
			if ("VF_Volume" in str(context.scene.objects[v].name)):
				volcount += 1
		
		context.active_object.name = 'VF_Volume_' + str(volcount)
		parentObj = context.active_object
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.delete(type='VERT')
		bpy.ops.object.mode_set(mode='OBJECT')
		
		baseLoc = ((-1.0 * Vector(context.window_manager.fieldDensity)) * 0.25) * context.window_manager.fieldScale
		
		vertsList = []
		
		for i in range(context.window_manager.fieldDensity[2]):
			for j in range(context.window_manager.fieldDensity[1]):
				for k in range(context.window_manager.fieldDensity[0]):
					vertsList = vertsList + [(Vector([baseLoc[0] + ((k * 0.5) * context.window_manager.fieldScale) + (0.25 * context.window_manager.fieldScale),baseLoc[1] + ((j * 0.5) * context.window_manager.fieldScale) + (0.25 * context.window_manager.fieldScale),baseLoc[2] + ((i * 0.5) * context.window_manager.fieldScale) + (0.25 * context.window_manager.fieldScale)]))]
		
		totalvertscount = context.window_manager.fieldDensity[0] * context.window_manager.fieldDensity[1] * context.window_manager.fieldDensity[2]
		
		me = context.active_object.data
		me.update()
		me.vertices.add(totalvertscount)
		
		context.active_object.vf_startlocations.clear()
		
		for l in range(len(me.vertices)):
			me.vertices[l].co = vertsList[l]
			tempvertdata = context.active_object.vf_startlocations.add()
			tempvertdata.vvelocity = vertsList[l]
		
		bpy.ops.object.particle_system_add()
		psettings = context.active_object.particle_systems[0].settings
		psettings.count = totalvertscount
		psettings.emit_from = 'VERT'
		psettings.normal_factor = 0.0
		psettings.use_emit_random = False
		psettings.frame_end = 1
		psettings.lifetime = 32
		psettings.grid_resolution = 1
		
		bpy.ops.group.create(name='VFGroup')
		
		volMesh = context.active_object
		
		bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
		context.active_object.name = 'VF_Bounds_' + str(volcount)
		
		context.active_object.scale = (Vector(context.window_manager.fieldDensity) * 0.25) * context.window_manager.fieldScale
		bpy.ops.object.transform_apply(scale=True)
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.delete(type='ONLY_FACE')
		bpy.ops.object.mode_set(mode='OBJECT')
		
		volMesh.parent = context.active_object
		
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
		elif not ('vf_startlocations' in bpy.context.active_object):
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
	
	for i in range(len(context.active_object.custom_vectorfield)):
		if abs(Vector(context.active_object.custom_vectorfield[i].vvelocity).length) > 0:
			draw_line(context.active_object.vf_startlocations[i].vvelocity, context.active_object.custom_vectorfield[i].vvelocity, dispcol, 2.0, dispscale)
			
	bgl.glDisable(bgl.GL_BLEND)

#############################
