import bpy

import math
from mathutils import Vector

from bpy.props import StringProperty

from bpy_extras.io_utils import (ImportHelper,
								 path_reference_mode)

import os.path

def build_importedVectorField(self, context, tempvelList):
	densityVal = Vector(context.window_manager.fieldDensity)
	scaleVal = context.window_manager.fieldScale
	vertsList = []
	volcount = 0
	baseLoc = ((-1.0 * densityVal) * 0.25) * scaleVal
	totalvertscount = densityVal[0] * densityVal[1] * densityVal[2]
	xval = int(densityVal[0])
	yval = int(densityVal[1])
	zval = int(densityVal[2])
	
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
		tempvertdata.vvelocity = tempvelList[l]
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



class import_vectorfieldfile(bpy.types.Operator, ImportHelper):
	bl_idname = "object.import_vectorfieldfile"
	bl_label = "Import FGA"
	bl_description = 'Import a FGA file as a vector field'

	filename_ext = ".fga"
	filter_glob = StringProperty(default="*.fga", options={'HIDDEN'})
	
	def execute(self, context):
		print ("Path = " + self.filepath)
		
		if os.path.exists(self.filepath):
			if os.path.isfile(self.filepath):
				file = open(self.filepath, 'r')
				
				print (file)
				linecount = 0
				
				tempvelList = []
				
				for line in file:
					slist = []
					slist = line.split(',')
					if len(slist) > 3:
						slist.remove(slist[3])
					
					flist = [float(s) for s in slist]
					
					if linecount <= 2:
						if linecount == 0:
							context.window_manager.fieldDensity[0] = int(flist[0])
							context.window_manager.fieldDensity[1] = int(flist[1])
							context.window_manager.fieldDensity[2] = int(flist[2])
						elif linecount == 2:
							context.window_manager.fieldScale = (int(flist[0]) * 2) / context.window_manager.fieldDensity[0]
					else:
						tempvelList.append(Vector(flist))
					
					linecount += 1
				
				if linecount < 3:
					print ("Import Failed: File is corrupt")
				else:
					if len(tempvelList) > 0:
						print ("Setting up new object...")
						build_importedVectorField(self, context, tempvelList)
						
				
				print (len(tempvelList))
				
				
				file.close()
			else:
				print ("Import Failed: File not found...")
		else:
			print ("Import Failed: Path not found...")
		
		return {'FINISHED'}

