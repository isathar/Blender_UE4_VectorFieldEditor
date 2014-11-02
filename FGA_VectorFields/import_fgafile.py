import bpy

import math
from mathutils import Vector

from bpy.props import StringProperty

from bpy_extras.io_utils import (ImportHelper,
								 path_reference_mode)

import os.path


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
				
				if len(file) > 3:
					for line in file:
						slist = line.split(',')
						slist.remove(slist[3])
						flist = []
						for s in slist:
							flist.append(float(s))
						
						print (flist)
				else:
					print ("Attempted to read incomplete/corrupt file")
				#print (file.read())
				
				
				file.close()
			else:
				print ("File not found...")
		else:
			print ("Filepath not found...")
		
		return {'FINISHED'}