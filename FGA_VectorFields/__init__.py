bl_info = {
	"name": "FGA Vector Field Tools",
	"author": "Andreas Wiehn (isathar)",
	"version": (0, 9, 5),
	"blender": (2, 70, 0),
	"location": "View3D > Toolbar",
	"description": " Allows creation and manipulation of vector fields using Blender particle simulations, "
					"as well as import/export of the FGA file format used in Unreal Engine 4.",
	"warning": "",
	"tracker_url": "https://github.com/isathar/Blender_UE4_VectorFieldEditor/issues/",
	"category": "Object"}


import bpy
from bpy.types import Panel

from . import vf_editor


# UI Panel
class vectorfieldtools_panel(bpy.types.Panel):
	bl_idname = "view3D.vectorfieldtools_panel"
	bl_label = 'FGA Tools'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "FGA Tools"

	def __init__(self):
		pass

	@classmethod
	def poll(self, context):
		return True

	def draw(self, context):
		layout = self.layout
		
		# Import/Export
		box = layout.box()
		row = box.row()
		if context.active_object != None:
			if 'custom_vectorfield' in context.active_object:
				row.operator('object.export_vectorfieldfile', text='Export')
			else:
				label = box.label("not a volume", 'NONE')
		else:
			label = box.label("no object", 'NONE')
		row = box.row()
		row.operator('object.import_vectorfieldfile', text='Import')
		row = layout.row()
		
		# Create
		box = layout.box()
		label = box.label("  Create New", 'NONE')
		row = box.row()
		row.column().prop(context.window_manager, 'vf_density', text='Resolution')
		row = box.row()
		row.column().prop(context.window_manager, 'vf_scale', text='Scale')
		row = box.row()
		row.prop(context.window_manager, 'vf_disablegravity', text='No gravity')
		row = box.row()
		row.operator('object.create_vectorfield', text='Generate')
		
		
		numObjects = context.window_manager.vf_density[0] * context.window_manager.vf_density[1] * context.window_manager.vf_density[2]
		row = box.row()
		label = row.label("# of vectors: " + str(numObjects), 'NONE')
		row = layout.row()
		
		# Edit
		box = layout.box()
		box.label("  Edit", 'NONE')
		
		box2 = box.box()
		row = box2.row()
		row.label(" Velocity Type:", 'NONE')
		row = box2.row()
		row.prop(context.window_manager, 'pvelocity_veltype', text='')
		if context.window_manager.pvelocity_veltype == "VECT":
			row = box2.row(align=True)
			row.column().prop(context.window_manager, 'pvelocity_dirvector',text='Custom Direction')
		
		row = box2.row()
		row.label(" Blend Method:", 'NONE')
		row = box2.row()
		row.prop(context.window_manager, 'pvelocity_genmode', text='')
		if context.window_manager.pvelocity_genmode == 'AVG':
			row = box2.row(align=True)
			row.prop(context.window_manager, 'pvelocity_avgratio',text='Ratio')
		
		row = box2.row(align=True)
		row.prop(context.window_manager, 'pvelocity_selection',text='Selected Only')
		
		row = box2.row(align=True)
		row.prop(context.window_manager, 'pvelocity_invert',text='Invert Next')
		
		row = box2.row(align=True)
		row.operator('object.calc_vectorfieldvelocities', text='Calculate')
		
		box3 = box.box()
		row = box3.row()
		row.operator('object.vf_normalizevelocities', text='Normalize')
		row = box3.row()
		row.operator('object.vf_invertvelocities', text='Invert All')
		
		row = layout.row()
		
		# selection
		box = layout.box()
		label = box.label("  Select", 'none')
		row = box.row()
		row.prop(context.window_manager, 'pselect_slice',text='Slice Axis')
		
		row = box.row()
		row.operator('object.select_vfslice', text='Select Slice')
		
		row = layout.row()
		
		# Display
		box = layout.box()
		label = box.label("  Display", 'NONE')
		row = box.row()
		if context.window_manager.vf_showingvelocitylines < 1:
			row.operator('view3d.toggle_vectorfieldvelocities', text='Show')
		else:
			row.operator('view3d.toggle_vectorfieldvelocities', text='Hide')
		row = box.row()
		row.operator('view3d.update_vfdispoffsets', text='Update Offsets')
		row = layout.row()
		
		# Tools:
		box = layout.box()
		label = box.label("  Tools", 'NONE')
		# create curve path
		box = box.box()
		label = box.label("    Curve Path", 'NONE')
		row = box.row(align=True)
		if context.active_object != None:
			if context.active_object.type == 'CURVE':
				label = row.label("Strength:", 'NONE')
				row = box.row(align=True)
				row.prop(context.window_manager, 'curveForce_strength', text='')
				row = box.row(align=True)
				label = row.label("Max Distance:", 'NONE')
				row = box.row(align=True)
				row.prop(context.window_manager, 'curveForce_maxDist', text='')
				row = box.row(align=True)
				label = row.label("Falloff Power:", 'NONE')
				row = box.row(align=True)
				row.prop(context.window_manager, 'curveForce_falloffPower', text='')
				row = box.row(align=True)
				row.prop(context.window_manager, 'curveForce_trailout', text='Trail')
				row = box.row(align=True)
				row = box.row(align=True)
				row.operator('object.calc_pathalongspline', text='Create')
			else:
				label = row.label("Select a curve", 'NONE')
		else:
			label = row.label("Select a curve", 'NONE')



# init stuff:
class vector_field(bpy.types.PropertyGroup):
	vvelocity = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0))
	vstartloc = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0))
	v_index = bpy.props.IntVectorProperty(default=(-1,-1,-1))


def initdefaults():
	bpy.types.Object.custom_vectorfield = bpy.props.CollectionProperty(type=vector_field)
	bpy.types.Object.vf_object_density = bpy.props.IntVectorProperty(default=(0,0,0))
	bpy.types.Object.vf_object_scale = bpy.props.FloatVectorProperty(default=(1.0,1.0,1.0))
	
	# generate
	bpy.types.WindowManager.vf_density = bpy.props.IntVectorProperty(default=(16,16,16),subtype='TRANSLATION',min=1,max=128,description="The number of points in the vector field. Limited to 128 in each direction (like UE4 importer)")
	bpy.types.WindowManager.vf_scale = bpy.props.FloatVectorProperty(default=(1.0,1.0,1.0),subtype='TRANSLATION',min=0.5,description="Scale of the vector field's bounds")
	
	bpy.types.WindowManager.vf_disablegravity = bpy.props.BoolProperty(default=False,description="Disable gravity on newly generated/imported vector field")
	#bpy.types.WindowManager.vf_usehairparticles = bpy.props.BoolProperty(default=False,description="Use hair particles. In this mode, velocities are calculated using the locations of hair particle points")
	
	# calculate/edit
	bpy.types.WindowManager.pvelocity_veltype = bpy.props.EnumProperty(
			name="Velocity Type",
			items=(('VECT', "Custom Vector", "Use direction vector as velocities"),
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
				   ('REP', "Replace", "Default - Overwrite old velocities (reset saved to current)"),
				   ),
			default='REP',
			description="Method of combining current and saved velocities",
			)
	
	bpy.types.WindowManager.pvelocity_invert = bpy.props.BoolProperty(default=False,description="Invert current velocities before saving")
	bpy.types.WindowManager.pvelocity_selection = bpy.props.BoolProperty(default=False,description="Replace selected particles' velocities only")
	
	bpy.types.WindowManager.pvelocity_avgratio = bpy.props.FloatProperty(default=0.5,description="The ratio between the current and new velocities")
	
	bpy.types.WindowManager.pvelocity_dirvector = bpy.props.FloatVectorProperty(default=(0.0,0.0,1.0),subtype='TRANSLATION',min=-16.0,max=16.0,description="Vector to set all velocities to")
	
	# slice select
	bpy.types.WindowManager.pselect_slice = bpy.props.EnumProperty(
			name="Slice Axis",
			options={'ENUM_FLAG'},
			items=(('X', "X", "Select all with same X value"),
				   ('Y', "Y", "Select all with same Y value"),
				   ('Z', "Z", "Select all with same Z value"),
				   ),
			default={'X'},
			description="Axes for slice selection",
			)
	
	# curve force
	bpy.types.WindowManager.curveForce_strength = bpy.props.FloatProperty(default=8.0,description="The power of each wind force along the curve")
	bpy.types.WindowManager.curveForce_maxDist = bpy.props.FloatProperty(default=4.0,description="Maximum influence distance for wind forces")
	bpy.types.WindowManager.curveForce_falloffPower = bpy.props.FloatProperty(default=2.0,description="Distance falloff for winf forces")
	bpy.types.WindowManager.curveForce_trailout = bpy.props.BoolProperty(default=False,description="Fade the size and influence of the wind forces along the curve")
	
	# display
	bpy.types.WindowManager.vf_showingvelocitylines = bpy.props.IntProperty(default=-1)
	
	bpy.types.WindowManager.exportvf_allowmanualbounds = bpy.props.BoolProperty(name="Manual Bounds",default=False,description="Allow setting vector field bounds manually")
	bpy.types.WindowManager.exportvf_manualboundsneg = bpy.props.IntVectorProperty(name="Bounds Scale -",min=-10000,max=10000,default=(-100,-100,-100),subtype='TRANSLATION',description="Minimum values for bounds in cm (have to be less than maximum values)")
	bpy.types.WindowManager.exportvf_manualboundspos = bpy.props.IntVectorProperty(name="Bounds Scale +",min=-10000,max=10000,default=(100,100,100),subtype='TRANSLATION',description="Maximum values for bounds in cm (have to be greater than minimum values)")
	bpy.types.WindowManager.exportvf_manualvelocityscale = bpy.props.FloatProperty(name="Velocity Scale",min=1.0,max=10000.0,default=1.0,description="Multiplier for velocities when using manual bounds")
	
	bpy.types.WindowManager.exportvf_scale = bpy.props.FloatProperty(name="Bounds Scale",min=1.0,max=10000.0,default=100.0,description="Scale the size of the volume's bounds by this on export - actual size in UE4 = this * (the vector field's density) * 0.5 cm")
	bpy.types.WindowManager.exportvf_velscale = bpy.props.BoolProperty(name="Scale Velocity",default=True,description="Scale velocity with bounds scale")
	bpy.types.WindowManager.exportvf_locoffset = bpy.props.BoolProperty(name="Export Offset",default=True,description="Exports the location of the vector field's bounding volume as an offset to min/max bounds")
	
	bpy.types.WindowManager.importvf_scalemult = bpy.props.FloatProperty(name="Size Multiplier",min=0.0001,max=10000.0,step=0.0001,default=0.01,description="Multiplier to apply to the scale of the volume's bounds on import")
	bpy.types.WindowManager.importvf_velscale = bpy.props.BoolProperty(name="Scale Velocity",default=True,description="Scale velocity on import")
	bpy.types.WindowManager.importvf_getoffset = bpy.props.BoolProperty(name="Get Offset",default=True,description="Get location offset from file")
	


def clearvars():
	props = ['vf_density','vf_scale','vf_disablegravity','pvelocity_veltype','pvelocity_genmode','pvelocity_invert','pvelocity_selection','pvelocity_avgratio','pvelocity_dirvector','pselect_slice','curveForce_strength','curveForce_maxDist','curveForce_falloffPower','curveForce_trailout','vf_showingvelocitylines','exportvf_allowmanualbounds','exportvf_manualboundsneg','exportvf_manualboundspos','exportvf_manualvelocityscale','exportvf_scale','exportvf_velscale','exportvf_locoffset','importvf_scalemult','importvf_velscale','importvf_getoffset']
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
	bpy.utils.register_class(vf_editor.select_vfslice)
	bpy.utils.register_class(vf_editor.vf_normalizevelocities)
	bpy.utils.register_class(vf_editor.vf_invertvelocities)
	bpy.utils.register_class(vf_editor.update_vfdispoffsets)
	
	bpy.utils.register_class(vf_editor.export_vectorfieldfile)
	bpy.utils.register_class(vf_editor.import_vectorfieldfile)
	
	bpy.utils.register_class(vectorfieldtools_panel)
	
	initdefaults()


def unregister():
	bpy.utils.unregister_class(vectorfieldtools_panel)
	
	bpy.utils.unregister_class(vf_editor.calc_vectorfieldvelocities)
	bpy.utils.unregister_class(vf_editor.create_vectorfield)
	bpy.utils.unregister_class(vf_editor.calc_pathalongspline)
	bpy.utils.unregister_class(vf_editor.toggle_vectorfieldvelocities)
	bpy.utils.unregister_class(vf_editor.select_vfslice)
	bpy.utils.unregister_class(vf_editor.vf_normalizevelocities)
	bpy.utils.unregister_class(vf_editor.vf_invertvelocities)
	bpy.utils.unregister_class(vf_editor.update_vfdispoffsets)
	
	bpy.utils.unregister_class(vf_editor.export_vectorfieldfile)
	bpy.utils.unregister_class(vf_editor.import_vectorfieldfile)
	
	bpy.utils.unregister_class(vector_field)
	
	clearvars()


if __name__ == '__main__':
	register()