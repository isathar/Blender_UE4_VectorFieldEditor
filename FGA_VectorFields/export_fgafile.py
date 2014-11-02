import bpy

import math
from mathutils import Vector

from bpy.props import StringProperty

from bpy_extras.io_utils import (ExportHelper,
								 path_reference_mode)



class export_vectorfieldfile(bpy.types.Operator, ExportHelper):
	bl_idname = "object.export_vectorfieldfile"
	bl_label = "Export FGA"
	bl_description = 'Export selection as a FGA vector field'

	filename_ext = ".fga"
	filter_glob = StringProperty(default="*.fga", options={'HIDDEN'})
	
	def check_extension(self):
		return self.batch_mode == 'OFF'

	def check(self, context):
		is_def_change = super().check(context)
		return (is_def_change)

	def execute(self, context):
		if not self.filepath:
			raise Exception("filepath not set")
		
		#print(self.filepath)
		
		file = open(self.filepath, "w", encoding="utf8", newline="\n")
		fw = file.write
		
		# Resolution:
		fw("%f,%f,%f," % (context.window_manager.fieldDensity[0],context.window_manager.fieldDensity[1],context.window_manager.fieldDensity[2]))
		# MinimumXYZ:
		fw("\n%f,%f,%f," % (((context.window_manager.fieldDensity[0] * -0.5) * context.window_manager.fieldScale),((context.window_manager.fieldDensity[1] * -0.5) * context.window_manager.fieldScale),((context.window_manager.fieldDensity[2] * -0.5) * context.window_manager.fieldScale)))
		# MaximumXYZ:
		fw("\n%f,%f,%f," % ((context.window_manager.fieldDensity[0] * 0.5) * context.window_manager.fieldScale,(context.window_manager.fieldDensity[1] * 0.5) * context.window_manager.fieldScale,(context.window_manager.fieldDensity[2] * 0.5) * context.window_manager.fieldScale))
		
		for vec in context.object.custom_vectorfield:
			fw("\n%f,%f,%f," % (vec.vvelocity[0],vec.vvelocity[1],vec.vvelocity[2]))
		
		file.close()
		
		return {'FINISHED'}
