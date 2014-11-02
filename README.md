Blender_UE4_VectorFieldEditor
=============================

Adds support for creating vector fields and exporting them in the FGA format.

Installation:
- Extract to your Blender\#.##\scripts\addons folder
- enable in the addon manager (named "Vector Field Tools")


rough instructions: (WIP)


notes: 
- Blender will briefly freeze (or hitch) while generating vector fields
- vector fields generate pretty quickly, (on an older Core i5 CPU) less than a second for 32x32x32 and below, around 20 seconds for a 128x128x128 density field
(compared to my first few attempts, which ate my RAM and froze Blender for 20 minutes on a 16-base vector field)

- Performance while editing seems good, I noticed a slight drop in framerate when displaying a 128-base field, 
 enabling the display of velocity lines on large fields will slow things down.

- Remember, the higher the amount of particles you are simulating, the more memory and processing power will be needed.
	- baking particle transforms for a very dense (64base +) vector field can take a while.


instructions:

	create new:

- set x,y,z resolution
- set scale
- click generate
(number of vectors in field is shown below this button)


	editing

- select the VF_Volume_X object (floating points, not the bounds) to change its particle settings
- add any forces you want influencing the particles to the scene
- NOTE: you can scale the field, move it around, etc since only the saved velocities and editor density/scale are exported
- bake the particle system's frames (not required, but it can speed things up for dense vector fields)
- select the frame you want the exported velocities to be based on
- click "Calculate"


	curve path tool: 
	(creates small wind forces along a line to make particles flow)

- create a curve object, shape it in the path you want particles to follow
- any kind of curve (point curve, bezier and nurbs) should be supported, including circles + knots
- with the object selected, the curve path panel should be populated with settings to change
- click create
- this acts like any other forcefields, so the same instructions to save apply


	export

- the export button is invisible by default and becomes visible once there is something to export
- click Calculate to create the data that is exported
- click export


(not finished:)
	import

- click the import button in the top of the panel, select the file
- the script will now generate a new vector field of the dimensions in the file and populate its velocities list