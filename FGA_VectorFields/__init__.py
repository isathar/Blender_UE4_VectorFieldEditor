bl_info = {
	"name": "FGA Vector Field Tools",
	"author": "Andreas Wiehn (isathar)",
	"version": (1, 0, 0),
	"blender": (2, 70, 0),
	"location": "View3D > Toolbar",
	"description": " Allows creation and manipulation of vector fields using Blender particle simulations, "
					"as well as import/export of the FGA file format used in Unreal Engine 4.",
	"warning": "",
	"tracker_url": "https://github.com/isathar/Blender_UE4_VectorFieldEditor/issues/",
	"category": "Object"}



import bpy
from bpy_extras.io_utils import (ImportHelper,ExportHelper,path_reference_mode)

from . import vf_editor


# UI Panel
class vectorfieldtools_panel(bpy.types.Panel):
	bl_idname = "view3D.vectorfieldtools_panel"
	bl_label = 'FGA Tools'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Vector Fields"

	def __init__(self):
		pass

	@classmethod
	def poll(self, context):
		return True

	def draw(self, context):
		layout = self.layout
		
		layout.row().operator('view3d.update_vfeditorvars', text='Update Data')
		
		# Create
		box = layout.box()
		box.prop(context.window_manager, 'show_createpanel', toggle=True, text="Create")
		if context.window_manager.show_createpanel:
			box.row().column().prop(context.window_manager, 'vf_density', text='Resolution')
			box.row().column().prop(context.window_manager, 'vf_scale', text='Scale')
			box.row().prop(context.window_manager, 'vf_disablegravity', text='No gravity')
			box.row().operator('object.create_vectorfield', text='Generate')
			numObjects = context.window_manager.vf_density[0] * context.window_manager.vf_density[1] * context.window_manager.vf_density[2]
			box.row().label("# of vectors: " + str(numObjects), 'NONE')
		
		# Edit
		box = layout.box()
		box.prop(context.window_manager, 'show_editpanel', toggle=True, text="Edit")
		if context.window_manager.show_editpanel:
			box2 = box.box()
			box2.row().label(" Velocity Type:", 'NONE')
			box2.row().prop(context.window_manager, 'pvelocity_veltype', text='')
			if context.window_manager.pvelocity_veltype == "VECT":
				box2.row(align=True).column().prop(context.window_manager, 'pvelocity_dirvector',text='Custom Direction')
			box2.row().label(" Blend Method:", 'NONE')
			box2.row().prop(context.window_manager, 'pvelocity_genmode', text='')
			if context.window_manager.pvelocity_genmode == 'AVG':
				box2.row().prop(context.window_manager, 'pvelocity_avgratio',text='Ratio')
			box2.row(align=True).prop(context.window_manager, 'pvelocity_selection',text='Selected Only')
			box2.row(align=True).prop(context.window_manager, 'pvelocity_invert',text='Invert Next')
			box2.row(align=True).operator('object.calc_vectorfieldvelocities', text='Calculate')
			box2 = box.box()
			box2.row().operator('object.vf_normalizevelocities', text='Normalize')
			box2.row().operator('object.vf_invertvelocities', text='Invert All')
		
		# Display
		box = layout.box()
		box.prop(context.window_manager, 'show_displaypanel', toggle=True, text="Display")
		if context.window_manager.show_displaypanel:		
			if context.window_manager.vf_showingvelocitylines < 1:
				box.row().operator('view3d.toggle_vectorfieldvelocities', text='Show')
			else:
				box.row().operator('view3d.toggle_vectorfieldvelocities', text='Hide')
			box.row().operator('view3d.update_vfdispoffsets', text='Update Offsets')
		
		# Tools:
		box = layout.box()
		box.prop(context.window_manager, 'show_toolspanel', toggle=True, text="Tools")
		if context.window_manager.show_toolspanel:
			# 	# Curve Path
			box = box.box()
			box.label("Curve Path:", 'NONE')
			if context.active_object != None:
				if context.active_object.type == 'CURVE':
					box.row(align=True).prop(context.window_manager, 'curveForce_strength', text='Strength')
					box.row(align=True).prop(context.window_manager, 'curveForce_maxDist', text='Distance')
					box.row(align=True).prop(context.window_manager, 'curveForce_falloffPower', text='Power')
					box.row(align=True).prop(context.window_manager, 'curveForce_trailout', text='Trail')
					box.row(align=True).operator('object.calc_pathalongspline', text='Create')
				else:
					box.row(align=True).label("Select a curve", 'NONE')
			else:
				box.row(align=True).label("Select a curve", 'NONE')
			
			#	# TBD: add more tools



# Saved Data
class vector_field(bpy.types.PropertyGroup):
	vvelocity = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0))


# Export
class export_vectorfieldfile(bpy.types.Operator, ExportHelper):
	bl_idname = "object.export_vectorfieldfile"
	bl_label = "Export FGA"
	bl_description = 'Export selected volume as a FGA file'
	
	filename_ext = ".fga"
	filter_glob = bpy.props.StringProperty(default="*.fga", options={'HIDDEN'})
	
	exportvf_allowmanualbounds = bpy.props.BoolProperty(
		name="Manual Bounds",default=False,
		description="Allow setting vector field bounds manually"
	)
	exportvf_manualboundsneg = bpy.props.IntVectorProperty(
		name="Bounds Scale -",min=-10000,max=10000,default=(-100,-100,-100),
		subtype='TRANSLATION',
		description="Minimum values for bounds in cm (have to be less than maximum values)"
	)
	exportvf_manualboundspos = bpy.props.IntVectorProperty(
		name="Bounds Scale +",min=-10000,max=10000,default=(100,100,100),
		subtype='TRANSLATION',
		description="Maximum values for bounds in cm (have to be greater than minimum values)"
	)
	exportvf_manualvelocityscale = bpy.props.FloatProperty(
		name="Velocity Scale",min=1.0,max=10000.0,default=1.0,
		description="Multiplier for velocities when using manual bounds"
	)
	exportvf_scale = bpy.props.FloatProperty(
		name="Bounds Scale",min=1.0,max=10000.0,default=100.0,
		description=("Scale the size of the volume's bounds by this on export" + 
			" - actual size in UE4 = this * (the vector field's density) * 0.5 cm")
	)
	exportvf_velscale = bpy.props.BoolProperty(
		name="Scale Velocity",default=True,
		description="Scale velocity with bounds scale"
	)
	exportvf_locoffset = bpy.props.BoolProperty(
		name="Export Offset",default=True,
		description="Exports the location of the vector field's bounding volume as an offset to min/max bounds"
	)
	
	def check_extension(self):
		return self.batch_mode == 'OFF'
	
	def check(self, context):
		is_def_change = super().check(context)
		return (is_def_change)
	
	def draw(self,context):
		layout = self.layout
		box = layout.box()
		box.row().prop(self, 'exportvf_allowmanualbounds', text='Manual Bounds')
		if self.exportvf_allowmanualbounds:
			box.row().column().prop(self, 'exportvf_manualboundsneg', text='Minimum Bounds')
			box.row().column().prop(self, 'exportvf_manualboundspos', text='Maximum Bounds')
			box.row().prop(self, 'exportvf_manualvelocityscale', text='Velocity Scale:')
		else:
			box.row().prop(self, 'exportvf_scale', text='Export Scale:')
			box.row().prop(self, 'exportvf_velscale', text='Scale Velocity')
			box.row().prop(self, 'exportvf_locoffset', text='Export Offset')
	
	def execute(self, context):
		if not self.filepath:
			raise Exception("filepath not set")
		else:
			if context.active_object != None:
				if 'custom_vectorfield' in context.active_object:
					vf_editor.write_fgafile(self, context)
				else:
					raise Exception("no velocities to export")
			else:
				raise Exception("no selection to export")
		
		return {'FINISHED'}


# Import
class import_vectorfieldfile(bpy.types.Operator, ImportHelper):
	bl_idname = "object.import_vectorfieldfile"
	bl_label = "Import FGA"
	bl_description = 'Import FGA file as a vector field'

	filename_ext = ".fga"
	filter_glob = bpy.props.StringProperty(default="*.fga", options={'HIDDEN'})
	
	importvf_scalemult = bpy.props.FloatProperty(
		name="Size Multiplier",min=0.0001,max=10000.0,step=0.0001,default=0.01,
		description="Multiplier to apply to the scale of the volume's bounds on import"
	)
	importvf_velscale = bpy.props.BoolProperty(
		name="Scale Velocity",default=True,
		description="Scale velocity on import"
	)
	importvf_getoffset = bpy.props.BoolProperty(
		name="Get Offset",default=True,
		description="Get location offset from file"
	)
	
	def draw(self,context):
		layout = self.layout
		
		box = layout.box()
		row = box.row()
		
		row.prop(self, 'importvf_scalemult', text='Import Scale')
		row = box.row()
		row.prop(self, 'importvf_velscale', text='Scale Velocity')
		row = box.row()
		row.prop(self, 'importvf_getoffset', text='Import Offset')
	
	
	def execute(self, context):
		retmessage = vf_editor.parse_fgafile(self, context)
		print ("FGA Import: " + retmessage + " (" + self.filepath + ")")
		
		return {'FINISHED'}


def exportmenu_func(self, context):
	self.layout.operator(export_vectorfieldfile.bl_idname,
						text="UE4 Vector Field (.fga)")

def importmenu_func(self, context):
	self.layout.operator(import_vectorfieldfile.bl_idname,
						text="UE4 Vector Field (.fga)")


def initdefaults():
	bpy.types.Object.custom_vectorfield = bpy.props.CollectionProperty(type=vector_field)
	bpy.types.Object.vf_object_density = bpy.props.IntVectorProperty(default=(0,0,0))
	bpy.types.Object.vf_object_scale = bpy.props.FloatVectorProperty(default=(1.0,1.0,1.0))
	
	# generate
	bpy.types.WindowManager.vf_density = bpy.props.IntVectorProperty(
		default=(16,16,16),subtype='TRANSLATION',min=1,max=128,
		description="The number of points in the vector field"
	)
	bpy.types.WindowManager.vf_scale = bpy.props.FloatVectorProperty(
		default=(1.0,1.0,1.0),subtype='TRANSLATION',min=0.25,
		description="Distance between points in the vector field"
	)
	bpy.types.WindowManager.vf_disablegravity = bpy.props.BoolProperty(
		default=False,description="Disable gravity influence on volume's particles"
	)
	# calculate/edit
	bpy.types.WindowManager.pvelocity_veltype = bpy.props.EnumProperty(
		name="Velocity Type",
		items=(('PNT', "Point", "Get a direction vector pointing away from 3D cursor"),
			   ('VECT', "Custom Vector", "Use direction vector as velocities"),
			   ('ANGVEL', "Angular Velocity", "Get particles' current angular velocities (spin)"),
			   ('DIST', "Distance", "Get particles' offsets from their initial locations"),
			   ('PVEL', "Velocity", "Get particles' current velocities"),
			   ),
		default='PVEL',
		description="Method of obtaining velocities from the particle system",
	)
	bpy.types.WindowManager.pvelocity_genmode = bpy.props.EnumProperty(
		name="Calculation Method",
		items=(('MULT', "Multiply", "Multiply current velocities with old velocities"),
			   ('ADD', "Add", "Add new velocities to existing ones"),
			   ('AVG', "Average", "Get the average of old and new velocities"),
			   ('REP', "Replace", "Default - Overwrite old velocities"),
			   ),
		default='REP',
		description="Method of combining current and saved velocities",
	)
	bpy.types.WindowManager.pvelocity_invert = bpy.props.BoolProperty(
		default=False,description="Invert current velocities before saving"
	)
	bpy.types.WindowManager.pvelocity_selection = bpy.props.BoolProperty(
		default=False,description="Replace selected particles' velocities only"
	)
	bpy.types.WindowManager.pvelocity_avgratio = bpy.props.FloatProperty(
		default=0.5,description="The ratio between the current and new velocities"
	)
	bpy.types.WindowManager.pvelocity_dirvector = bpy.props.FloatVectorProperty(
		default=(0.0,0.0,1.0),subtype='TRANSLATION',min=-16.0,max=16.0,
		description="Vector to set all velocities to"
	)
	# curve force
	bpy.types.WindowManager.curveForce_strength = bpy.props.FloatProperty(
		default=8.0,description="The power of each wind force along the curve"
	)
	bpy.types.WindowManager.curveForce_maxDist = bpy.props.FloatProperty(
		default=4.0,description="Maximum influence distance for wind forces"
	)
	bpy.types.WindowManager.curveForce_falloffPower = bpy.props.FloatProperty(
		default=2.0,description="Distance falloff for wind forces"
	)
	bpy.types.WindowManager.curveForce_trailout = bpy.props.BoolProperty(
		default=False,description="Fade the size and influence of the wind forces along the curve"
	)
	
	# display
	bpy.types.WindowManager.vf_showingvelocitylines = bpy.props.IntProperty(default=-1)
	
	# toggle vars for panel
	bpy.types.WindowManager.show_createpanel = bpy.props.BoolProperty(
		default=False,description="Toggle Section"
	)
	bpy.types.WindowManager.show_editpanel = bpy.props.BoolProperty(
		default=False,description="Toggle Section"
	)
	bpy.types.WindowManager.show_displaypanel = bpy.props.BoolProperty(
		default=False,description="Toggle Section"
	)
	bpy.types.WindowManager.show_toolspanel = bpy.props.BoolProperty(
		default=False,description="Toggle Section"
	)
	

def clearvars():
	vf_editor.clear_data()
	
	props = [
		'vf_density','vf_scale','vf_disablegravity','pvelocity_veltype','pvelocity_genmode',
		'pvelocity_invert','pvelocity_selection','pvelocity_avgratio','pvelocity_dirvector',
		'curveForce_strength','curveForce_maxDist','curveForce_falloffPower','curveForce_trailout','curveForce_dispSize'
		'vf_showingvelocitylines',
		'show_createpanel','show_editpanel','show_displaypanel','show_toolspanel'
	]
	
	for p in props:
		if bpy.context.window_manager.get(p) != None:
			del bpy.context.window_manager[p]
		try:
			x = getattr(bpy.types.WindowManager, p)
			del x
		except:
			pass


def register():
	bpy.utils.register_class(vector_field)
	
	bpy.utils.register_class(vf_editor.calc_vectorfieldvelocities)
	bpy.utils.register_class(vf_editor.create_vectorfield)
	bpy.utils.register_class(vf_editor.calc_pathalongspline)
	bpy.utils.register_class(vf_editor.toggle_vectorfieldvelocities)
	bpy.utils.register_class(vf_editor.vf_normalizevelocities)
	bpy.utils.register_class(vf_editor.vf_invertvelocities)
	bpy.utils.register_class(vf_editor.update_vfdispoffsets)
	bpy.utils.register_class(vf_editor.update_vfeditorvars)
	
	bpy.utils.register_class(export_vectorfieldfile)
	bpy.utils.register_class(import_vectorfieldfile)
	
	bpy.utils.register_class(vectorfieldtools_panel)
	
	bpy.types.INFO_MT_file_export.append(exportmenu_func)
	bpy.types.INFO_MT_file_import.append(importmenu_func)
	
	initdefaults()


def unregister():
	bpy.utils.unregister_class(vectorfieldtools_panel)
	
	bpy.utils.unregister_class(vf_editor.calc_vectorfieldvelocities)
	bpy.utils.unregister_class(vf_editor.create_vectorfield)
	bpy.utils.unregister_class(vf_editor.calc_pathalongspline)
	bpy.utils.unregister_class(vf_editor.toggle_vectorfieldvelocities)
	bpy.utils.unregister_class(vf_editor.vf_normalizevelocities)
	bpy.utils.unregister_class(vf_editor.vf_invertvelocities)
	bpy.utils.unregister_class(vf_editor.update_vfdispoffsets)
	bpy.utils.unregister_class(vf_editor.update_vfeditorvars)
	
	bpy.utils.unregister_class(export_vectorfieldfile)
	bpy.utils.unregister_class(import_vectorfieldfile)
	
	bpy.utils.unregister_class(vector_field)
	
	bpy.types.INFO_MT_file_export.remove(exportmenu_func)
	bpy.types.INFO_MT_file_import.remove(importmenu_func)
	
	clearvars()


if __name__ == '__main__':
	register()