bl_info = {
	"name": "FGA Vector Field Tools",
	"author": "Andreas Wiehn (isathar)",
	"version": (0, 9, 0),
	"blender": (2, 70, 0),
	"location": "View3D > Toolbar",
	"description": " Editor and exporter/importer for FGA vector fields used for GPU particles in UE4",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}


import bpy
from bpy.types import Panel

from . import vf_editor
from . import export_fgafile
from . import import_fgafile


# UI Panel
class vectorfieldtools_panel(bpy.types.Panel):
	bl_idname = "object.vectorfieldtools_panel"
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
			if ("VF_Volume" in (context.active_object.name)) and ('custom_vectorfield' in bpy.context.active_object):
				row.operator('object.export_vectorfieldfile', text='Export')
			elif ("VF_Volume" in (context.active_object.name)) and ('custom_vectorfield' in bpy.context.active_object):
				label = box.label("no velocities", 'NONE')
			else:
				label = box.label("not a volume", 'NONE')
		else:
			label = box.label("no object", 'NONE')
		row = box.row()
		row.operator('object.import_vectorfieldfile', text='Import')
		row = layout.row()
		
		# Create
		box = layout.box()
		label = box.label("  Create", 'NONE')
		row = box.row()
		row.column().prop(bpy.context.window_manager, 'fieldDensity', text='Resolution')
		row = box.row()
		row.column().prop(bpy.context.window_manager, 'fieldScale', text='Scale:')
		row = box.row()
		row.operator('object.create_vectorfield', text='Generate')
		row = box.row()
		row.column().prop(bpy.context.window_manager, 'field_disablegravity', text='No gravity')
		
		numObjects = bpy.context.window_manager.fieldDensity[0] * bpy.context.window_manager.fieldDensity[1] * bpy.context.window_manager.fieldDensity[2]
		row = box.row()
		label = row.label("# of vectors: " + str(numObjects), 'NONE')
		row = layout.row()
		
		# Edit
		box = layout.box()
		label = box.label("  Save", 'NONE')
		row = box.row(align=True)
		row.operator('object.calc_vectorfieldvelocities', text='Calculate')
		row = box.row(align=True)
		row.column().prop(bpy.context.window_manager, 'normalize_pvelocity',text='Normalize')
		row = box.row(align=True)
		row.operator('object.invert_velocities', text='Invert')
		row = layout.row()
		
		# Display
		box = layout.box()
		label = box.label("  Display", 'NONE')
		row = box.row()
		if bpy.context.window_manager.showing_vectorfield < 1:
			row.operator('view3d.toggle_vectorfieldvelocities', text='Show')
		else:
			row.operator('view3d.toggle_vectorfieldvelocities', text='Hide')
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
				row.column().prop(bpy.context.window_manager, 'curveForce_strength', text='')
				row = box.row(align=True)
				label = row.label("Max Distance:", 'NONE')
				row = box.row(align=True)
				row.column().prop(bpy.context.window_manager, 'curveForce_maxDist', text='')
				row = box.row(align=True)
				label = row.label("Falloff Power:", 'NONE')
				row = box.row(align=True)
				row.column().prop(bpy.context.window_manager, 'curveForce_falloffPower', text='')
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


def initdefaults():
	bpy.types.Object.custom_vectorfield = bpy.props.CollectionProperty(type=vector_field)
		
	bpy.types.WindowManager.fieldDensity = bpy.props.IntVectorProperty(default=(4,4,4),subtype='TRANSLATION',min=1)
	bpy.types.WindowManager.fieldScale = bpy.props.IntProperty(default=1,min=1)
	
	bpy.types.WindowManager.field_disablegravity = bpy.props.BoolProperty(default=False)
	
	bpy.types.WindowManager.showing_vectorfield = bpy.props.IntProperty(default=-1)
	
	bpy.types.WindowManager.normalize_pvelocity = bpy.props.BoolProperty(default=False)
	
	bpy.types.WindowManager.curveForce_strength = bpy.props.FloatProperty(default=8.0)
	bpy.types.WindowManager.curveForce_maxDist = bpy.props.FloatProperty(default=4.0)
	bpy.types.WindowManager.curveForce_falloffPower = bpy.props.FloatProperty(default=2.0)


def clearvars():
	props = ['fieldDensity','fieldScale','field_disablegravity','showing_vectorfield','normalize_pvelocity','curveForce_strength','curveForce_maxDist','curveForce_falloffPower']
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
	bpy.utils.register_class(vf_editor.invert_velocities)
	
	bpy.utils.register_class(export_fgafile.export_vectorfieldfile)
	bpy.utils.register_class(import_fgafile.import_vectorfieldfile)
	
	bpy.utils.register_class(vectorfieldtools_panel)
	
	initdefaults()


def unregister():
	bpy.utils.unregister_class(vectorfieldtools_panel)
	
	bpy.utils.unregister_class(vf_editor.calc_vectorfieldvelocities)
	bpy.utils.unregister_class(vf_editor.create_vectorfield)
	bpy.utils.unregister_class(vf_editor.calc_pathalongspline)
	bpy.utils.unregister_class(vf_editor.toggle_vectorfieldvelocities)
	bpy.utils.unregister_class(vf_editor.invert_velocities)
	
	bpy.utils.unregister_class(export_fgafile.export_vectorfieldfile)
	bpy.utils.unregister_class(import_fgafile.import_vectorfieldfile)
	
	bpy.utils.unregister_class(vector_field)
	
	clearvars()


if __name__ == '__main__':
	register()