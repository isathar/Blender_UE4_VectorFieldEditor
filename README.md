Blender - UE4 - FGA Vector Field Editor
=======================================

Allows creation and manipulation of vector fields using Blender particle simulations, as well as import/export of the FGA file format used in Unreal Engine 4.

Velocities are edited by adding forces to the scene that can affect the particles in the volume. 
Changes made are accumulative, so multiple sets of force fields can be used in different passes and combined into the final result using selectable math operations.
(For example, you could generate velocities using a vortex force in the center of the volume, then blend in an upwards velocity to tilt the resulting velocities up)

*This readme is a work in progress (as is the tool)*

------------------------------------------------------------------------------------------------------- 

## **Features:** 

- **Editor:**
  - Saves current particle system velocities and blends them with saved results using one of the following methods:
	- *Replace, Average, Add, Multiply*
  - Particle velocities used in these calculations can be obtained using the following methods:
	- *Velocity, Offset Distance, Angular Velocity, Custom Vector, Point*
  - *WIP:* Curve Force tool uses wind forces to move particles along a line.

- **Importer + Exporter** for FGA files for use in Unreal Engine 4

-------------------------------------------------------------------------------------------------------

## **Installation:**

- Extract to your Blender\#.##\scripts\addons folder
- Enable in the addon manager (named "FGA Vector Field Tools")
- A new section called Vector Fields should be available in the tools panel

---------------------------------------------------------------------------------------------------------

## **Notes:**

- *Performance*
  - Blender may stop responding during the Create and Calculate operations, but shouldn't crash.
  - On vector fields with a density of less than 128^3, operations should take less than a minute, with lower density fields (<64^3) taking up to a few seconds.
  - At maximum density (128^3), creating a new vector field takes about 20 seconds on my mid-range Core i5 based PC, and calculating velocities can take up to 5 minutes.
  - Performance while editing reasonably sized (< 1 million vertices) vector fields is good, while a 128^3 volume can be painfully slow under the right circumstances.
  - Display of velocity lines on large fields (64^3+) is very slow. 
 
- *128x128x128 and System Memory*
  - Editing a 128x128x128 vector field requires a 64-bit system and Blender install, as well as a large amount (> 6-8 GB) of system memory.
    - This is due to the amount of particles that need to have their dynamics cached
    - To avoid running out of memory while editing very dense vector fields, you may want to lower your undo history steps.
    - Using a disk cache for your particles may help, too. 
 
- *Console Warning Messages*
  - While creating a new vector field, the following messages will appear in your console window (if open):
    - `CustomData_copy_data_layer: warning null data for CDOrco type (...)`
    - `CustomData_copy_data_layer: warning null data for CDMVert type (...)`
  - It looks like these appear because there is no face data in the vector field and can probably be ignored. 
 
-*The usual disclaimers apply, i.e. don't blame me if anything breaks :D (it shouldn't... I'm just covering myself)*

------------------------------------------------------------------------------------------------------- 

## **Usage Instructions:** *(Some of this is old information, update in progress)* 


### **Creating a New Vector Field:** 
 
- Set the resolution (X,Y,Z)
  - The maximum resolution you can set is 128x128x128 since it's the limit set in UE4's importer (not to mention the massive amount of memory you would need for more).
- Set the scale for the volume's bounds
- Checking *No Gravity* will disable gravity's influence on the generated particle system (Gravity field weight set to 0)
- Click *Generate*
- The number of vectors in the vector field to be created is shown below this button 
 
 
### **Editing Process:** 

The editor lets you store the velocities of the volume's particles and edit the stored results by blending them using different mathematical expressions and ways to get the velocities. 

This way you can change the velocities in steps, allowing you to, for example, add a tunnel of faster upwards velocities to the saved results of a light noisy water volume.

1. Create some forces in the scene to influence the vector field
2. Go to the volume's *Particle Properties*
  - Customize the Particle system's Physics and Rotation Settings as needed
  - *Bake* (under cache) (this isn't required, but will speed things up when moving between frames)
    - if a bake is already active, click *Free Bake*
3. Select the frame you want to get velocities from
4. Select the *Velocity Type*, *Blend Method*, and optional parameters you want to use.
  - See **Blending Methods** below for a description of how these work
5. Click *Calculate*, repeat as many times as needed
6. *Invert* or *Normalize* the vector field if needed

To help with organization when you're blending multiple force influences and settings, you can move the forces you won't be using during a bake to a different layer by pressing *M* and selecting a layer.


**Blending Methods:**

- ***Velocity Types:***
  - The method used to obtain current particle velocities:
  - *Velocity:*
    - Gets the current velocities from the particle system
  - *Distance:*
    - Use the distance from each particle's starting position and its current position as velocity
  - *Angular Velocity:*
    - Use the current spin of each particle as velocity
    - Good for blending/multiplying with other types
  - *Custom Vector:*
    - Use a user-editable vector for all velocities
    - Good as a starting point and for blending with other types
    - Useful with the Multiply blend method as a 3d scale for each velocity
  - *Point:*
    - Sets current velocities to a direction pointing away from the 3d cursor
- ***Blend Method:***
  - The method used to blend saved results with current particle velocities
  - *Replace:*
    - replaces all saved velocities with the particle system's current velocities
    - good as a starting point
  - *Average:*
    - replaces saved velocities with the weighted average of the saved and current particle velocities
      - Ratio: The weight to assign to the current velocities in the calculation
  - *Add:*
    - replaces saved velocities with the sum of saved and current particle velocities
  - *Multiply:*
    - replaces saved velocities with the product of saved and current velocities

*Optional parameters for calculation:*

- *Selected Only*: save velocities for particles associated with vertices selected in Edit Mode
- *Invert Next*: inverts the current particle velocities before performing calculations with them
  - example: turn *Add* into Subtract

*Separate Calculations:*

  - *Normalize*: normalizes the saved velocities
  - *Invert All*: inverts the saved velocities



*Curve Path Tool:* 
 
- Creates small wind forces along a line to make particles flow (basically a wind tunnel)  
 
- Create a curve object, shape it in the path you want particles to follow
  - *NOTE:* Any kind of curve (point curve, bezier and nurbs) should be supported, including circles + knots
- With the curve object selected, the *Curve Path* panel should be populated with settings you can customize
- Check the *Trails* box if you want the curve's influence to fade as it reaches its end
- Apply any transforms you have on the curve
- Click *Create*
- This object acts like any other forcefield and can be moved
  - Moving the curve will move the forcefields attached to it, moving the force fields will offset them from the curve
- Subdivide the curve a few times to add more influence cylinders (for path smoothing) 



*Importing:* 
 
- Click *Import*, select your vector field file
- Import options:
  - *Import Scale*: Scale to apply to the file's bounds 
    - mostly used to shrink UE4 volumes to a more easily manageable size in Blender
  - *Scale Velocity*: Scale the velocities during import
    - Required for correct velocities when importing a file with *Get Scale* disabled
  - *Get Offset*: Import the offset of the volume's bounds from the file 


*Exporting:*  
 
- If exporting is not possible, the button will be replaced with text explaining what's going on 
 
Method 1 - Use settings from editor (default)
- Select the *VF_Volume_X* object (the floating points)
- Click *Export*
- Regular Export Options:
  - *Export Scale*: a multiplier for the size of the vector field in UE4. 
    - The actual size in UE4 will be: *Bounds Scale* x (the vector field's resolution) cm^3
	- defaults to 100, making a default scaled 16^3 vector field into a 1.6m^3 volume in UE4
  - *Scale Velocity*: scale the velocity with bounds scale during export
- Exporting location offsets:
  - Moving the vector field's bounding volume without applying the offset allows the offset to affect the volume's bounds during export 
 
Method 2: Manual Bounds (advanced)
- Enabling manual bounds will remove the above options and replace them with:
  - Minimum, maximum (x, y, z) Bounds in cm:
    - manually set the values for the vector field's bounding box.
    - min should always be less than max 

  

**Particle System Example Settings:** 
 
*Smoke Flow:*
- Create a cube, resize it to encompass the vector field
  - (or the area you want smoke simulation to happen in)
- name it something like Smoke Domain
- Go to the cube's Physics Properties
  - Enable Smoke
  - Select Domain as the smoke type
- Create a Smoke Flow Force Field
  - Add->Force Field->Smoke Flow for a simple point-based one
- Go to the vector field volume's Physics Properties
  - Enable Smoke
  - Select Flow as the smoke type
  - Set the Flow Source to Particle System, and select it
- Customize settings as needed
- add any forces you want to influence the smoke
- bake to cache (or not)  


*Basic Fluid Volume Simulation:* 
 
- Go to the vector field's Particle Properties
  - change the Physics Type to Fluid
  - customize settings:
    - by default it will be a still, thin fluid
    - Good settings for a noisy, thicker fluid:
      - Brownian: 0.25
      - Drag: 0.8
      - Damp: 0.5
      - Stiffness: 1.5
      - Viscosity: 4.0
      - Buoyancy: 0.1
- add any forces you want to influence the fluid
- bake to cache (or not)  


-------------------------------------------------------------------------------------------------------------- 

## **Changelog:**  

-v1.0.0
- *General:*
  - tools panel category renamed to 'Vector Fields'
  - saved data only includes velocities now (removed position, index)
    - files made with old versions are still compatible
  - cleaned up ui panel to reduce clutter, added section toggles
  - some code cleanup
- *Import/Export:*
  - moved import/export to standard menu
  - made import/export properties local to their functions
- *Editor:*
  - performance tweaks for creating new vector fields + calculating velocities
  - removed slice selection tool (redundant, easily done in edit mode)
  - matched default scaling to grid units * field density
    - distances were at half scale before
    - density variable used for creation is now distance between particles
  - added undo functionality to 'generate' function
  - new velocity mode: Point
- *Curve Force Tool:*
  - changed curve force tool to create an object group to remove scene outliner clutter
  - fixed curve force fields' parenting issue
    - all transformations to the curve force object should now work
  - curve forces now display an arrow pointing in the force's direction  


-v0.9.5
  - *Editor:*
    - added new calculation method: Multiply
    - added different methods for obtaining velocities
    - reorganized the main editor
    - added calculate for selection
    - added invert all button
	- seperated normalize function from calculation - it's a button again
  - *Import/Export:*
    - moved density variable to object space for export script 
      - allows multiple vector fields in the scene during export (still exports one at a time)
    - added ability to use object locations as offsets + import/export them
    - scaling tweaks
	- manual bounds option
  - *General:*
    - added ability to undo slice selection, calculation, curve tool, and normalize
    - select x,y,z slice
    - created index by axis for velocities list for slice selection and upcoming features
    - switched bpy.context to passed context where possible
    - description text for all variables + operators (some may be vague)
    - added bug reporting url to addon manager (Github)
    - readme formatting  

-v0.9.1
  - added different generation modes: Replace, Additive, Average
  - added trail option for curve path (fade influence with curve position)
  - changed the way invert and normalize work
  - slight calculation performance tweak

-v0.9
  - another performance tweak
  - added invert, normalize, disable gravity options  

-v0.8 
  - added import functionality
  - massive speed improvement  

-v0.5 
  - initial upload  
