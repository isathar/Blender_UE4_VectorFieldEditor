Blender - UE4 - FGA Vector Field Editor
=======================================

Adds support for creating vector fields with a particle system and exporting/importing the FGA format used for GPU particles in Unreal Engine 4.


*This readme is a work in progress*


-------------------------------------------------------------------------------------------------------


Installation:
-------------

- Extract to your Blender\#.##\scripts\addons folder
- Enable in the addon manager (named "FGA Vector Field Tools")

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

- The higher the amount of particles you are simulating, the more memory and processing power will be needed.
	- baking particle transforms for a very dense (>64x64x64) vector field can take a while.


The usual disclaimers apply, i.e. don't blame me if anything breaks :D (it shouldn't... I'm just covering myself)

-------------------------------------------------------------------------------------------------------


Usage:
------


*Creating:*

- Set the resolution (X,Y,Z)
- Set the scale (Size multiplier for the volume's bounds)
- Checking *No Gravity* will disable gravity's influence on the generated particle system (Gravity field weight set to 0)
- Click *Generate*
- *NOTE:* the number of vectors in the vector field is shown below this button


*Importing:*

- Click *Import*, select your vector field file


*Editing:*

- Select the *VF_Volume_X* object (the floating points, not the bounds) to change its particle settings
- Add any forces you want influencing the particles to the scene
- *NOTE:* you can scale the field, move it around, etc. since only the saved velocities and editor density/scale are exported
- Bake the particle system's frames (not required, but it can speed things up for dense vector fields)
- Select the frame you want the exported velocities to be based on
- Click *Calculate* to save the current particle velocities
- Select the generation method from the *Method* dropdown. Info on each method:
	-- *Replace*  	- Default method, sets the velocities of the vector field to the particle system's current velocities
	-- *Additive* 	- Adds the current particle velocities to the vector field's current velocities
	-- *Average*	- Sets the velocities of the vector field to the mean of the particle velocities and currently stored velocities
- Check *Normalize* if you want all velocities to have the same magnitude
	- this makes small forces have a greater impact and clamps all force magnitudes to 1.0
- Check *Invert* to read the inverse of current particle velocities while generating


*Curve Path Tool:*

- Creates small wind forces along a line to make particles flow (basically a wind tunnel)

- Create a curve object, shape it in the path you want particles to follow
- *NOTE:* Any kind of curve (point curve, bezier and nurbs) should be supported, including circles + knots
- With the curve object selected, the *Curve Path* panel should be populated with settings you can customize
- Check the *Trails* box if you want the curve's influence to fade as it reaches its end
- Click *Create*
- This object acts like any other forcefield and can be moved.
	-- Moving the curve will move the forcefields attached to it, moving the force fields will offset them from the curve

- *NOTE:* Scaling and rotating the line after adding the force field will have strange results.
- Subdivide the curve a few times to add more influence cylinders (for path smoothing)
- Currently, this creates a lot of loose objects on the scene.


*Exporting:*

- If exporting is not possible, th button will be replaced with text explaining what's going on.
- Select the *VF_Volume_X* object (the floating points)
- Click *Export*


*Importing:*

- Click the *Import* button in the top of the panel, select the file
- The script will now generate a new vector field of the dimensions in the file and populate its velocities list



--------------------------------------------------------------------------------------------------------------

Changelog:
v0.9.1
	- added different generation modes: Replace, Additive, Average
	- added trail option for curve path (fade influence with curve position)
	- changed the way invert and normalize work
	- slight calculation performance tweak

v0.9
	- another performance tweak
	- added invert, normalize, disable gravity options

v0.8 
	- added import functionality
	- massive speed improvement

v0.5 
	- initial upload

