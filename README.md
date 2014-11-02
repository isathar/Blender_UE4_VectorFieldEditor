Blender_UE4_VectorFieldEditor
=============================

Adds support for creating vector fields and exporting/importing the FGA format.


-------------------------------------------------------------------------------------------------------


Installation:
-------------

- Extract to your Blender\#.##\scripts\addons folder
- enable in the addon manager (named "Vector Field Tools")

---------------------------------------------------------------------------------------------------------


Notes:
------

- Blender will briefly freeze (or hitch) while generating vector fields and saving velocities
- vector fields generate pretty quickly, (on an older Core i5 CPU) less than a second for 32x32x32 and below, around 20 seconds for a 128x128x128 density field
(compared to my first few attempts, which ate through 3 GB RAM and froze Blender for 20 minutes on a 16-base vector field)
	- Here is a list of generation times on my system with different field sizes for reference:
		- 32x32x32: 0.2707s, 64x64x64: 2.2122s, 128x128x128: 18.1358s

- Performance while editing reasonably sized (< 1 million vertices) vector fields seems good.
	- I noticed a slight drop in framerate when displaying a 128-base field, but editing it was incredibly slow
		-		(since any manipulation of over 2 million vertices at once will eat your memory)
	- Editing a 128x128x128 vector field probably requires a 64-bit system and Blender install, as well as a large amount of system memory.
		- 		(I saw my memory use jump to >4GB while moving one around)
		- To avoid running out of memory while editing very dense vector fields, you may want to lower your undo history steps.

- Enabling the display of velocity lines on large fields will slow things down.

- Remember, the higher the amount of particles you are simulating, the more memory and processing power will be needed.
	- baking particle transforms for a very dense (64base +) vector field can take a while.


The usual disclaimers apply, i.e. don't blame me if anything breaks :D (it shouldn't... I'm just covering myself)

-------------------------------------------------------------------------------------------------------


Usage:
------


*Creating:*

- set x,y,z resolution
- set scale
- click generate
(number of vectors in field is shown below this button)


*Editing:*

- select the VF_Volume_X object (floating points, not the bounds) to change its particle settings
- add any forces you want influencing the particles to the scene
- NOTE: you can scale the field, move it around, etc since only the saved velocities and editor density/scale are exported
- bake the particle system's frames (not required, but it can speed things up for dense vector fields)
- select the frame you want the exported velocities to be based on
- click "Calculate"


*Curve Path Tool:*

(creates small wind forces along a line to make particles flow, basically a wind tunnel)

- create a curve object, shape it in the path you want particles to follow
- any kind of curve (point curve, bezier and nurbs) should be supported, including circles + knots
- with the object selected, the curve path panel should be populated with settings to change
- click create
- this acts like any other forcefields, so the same instructions to save apply


*Exporting:*

- the export button is invisible by default and becomes visible once there is something to export
- click Calculate to create the data that is exported
- click export


*Importing:*

- click the import button in the top of the panel, select the file
- the script will now generate a new vector field of the dimensions in the file and populate its velocities list