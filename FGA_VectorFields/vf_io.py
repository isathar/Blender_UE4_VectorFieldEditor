### Import/Export Functions

import bpy
import os.path
from mathutils import Vector

### Import

# create new vector field from imported data
def build_importedVectorField(tempvelList, tempOffset):
	# create blank vf
	from . import vf_editor
	volname = vf_editor.build_vectorfield(bpy.context)
	volmesh = bpy.context.scene.objects[volname]
	# copy imported velocities
	for i in range(len(tempvelList)):
		volmesh.custom_vectorfield[i].vvelocity = tempvelList[i]
	
	if volmesh.parent:
		volmesh.parent.location = volmesh.parent.location + tempOffset
	else:
		volmesh.location = volmesh.location + tempOffset

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
			tempMin = Vector((0.0,0.0,0.0))
			tempOffset = Vector((0.0,0.0,0.0))
			tempscalemult = Vector((0.0,0.0,0.0))
			
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
						tempscalemult = Vector((0.0,0.0,0.0))
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
						tempvelList.append(Vector((flist[0] * importvf_scalemult,flist[1] * importvf_scalemult,flist[2] * importvf_scalemult)))
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

def write_fgafile(self, exportvol):
	usevelscale = self.exportvf_velscale
	useoffset = self.exportvf_locoffset
	
	tempDensity = Vector(exportvol.vf_object_density)
	fgascale = Vector(exportvol.vf_object_scale)
	
	file = open(self.filepath, "w", encoding="utf8", newline="\n")
	fw = file.write
	
	# Resolution:
	fw("%i,%i,%i," % (tempDensity[0],tempDensity[1],tempDensity[2]))
	
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
			offsetvect = Vector((0.0,0.0,0.0))
			if exportvol.parent:
				offsetvect = exportvol.parent.location
			
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
		for vec in exportvol.custom_vectorfield:
			fw("\n%f,%f,%f," % (
				vec.vvelocity[0] * self.exportvf_scale,
				vec.vvelocity[1] * self.exportvf_scale,
				vec.vvelocity[2] * self.exportvf_scale)
			)
	else:
		if self.exportvf_allowmanualbounds:
			for vec in exportvol.custom_vectorfield:
				fw("\n%f,%f,%f," % (
					vec.vvelocity[0] * self.exportvf_manualvelocityscale,
					vec.vvelocity[1] * self.exportvf_manualvelocityscale,
					vec.vvelocity[2] * self.exportvf_manualvelocityscale)
				)
		else:
			for vec in exportvol.custom_vectorfield:
				fw("\n%f,%f,%f," % (
					vec.vvelocity[0],
					vec.vvelocity[1],
					vec.vvelocity[2])
				)
	
	file.close()
