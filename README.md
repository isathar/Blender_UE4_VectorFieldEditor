Blender - FGA Vector Field Editor
=======================================

Allows creation and manipulation of vector fields using Blender particle simulations and vector math operations, as well as importing/exporting FGA files used by Unreal Engine 4. 


- Requires Blender 2.8 and up.

- The menu panel can be found in the Panels section in the right part of the workspace. The documentation hasn't been updated to reflect this yet.
  
------------------------------------------------------------------------------------------------------- 
 
**Out-of-date Documentation is available here**: https://github.com/isathar/Blender_UE4_VectorFieldEditor/wiki (or the wiki link on the side) 
- Very out of date, will be updated as soon as time permits.

 
Some example .fga files: http://www.mediafire.com/download/4x174fgf8lmec6g/VF_Examples.zip  
  
 
------------------------------------------------------------------------------------------------------- 
 
## Features  
 
**Vector Field Editor:**
- Saves current particle system velocities and blends them with saved results using one of the following methods:
  - *Replace, Average, Add, Multiply, Cross Product, Vector Reflection*
- Particle velocities used in these calculations can be obtained using the following methods:
  - *Velocity, Offset Distance, Angular Velocity, Custom Vector, Point*
- Curve Force tool that uses wind forces to move particles along a line. 
  
**Importer + Exporter** for FGA files for use in Unreal Engine 4 
 
------------------------------------------------------------------------------------------------------- 
 
## Installation  
 
- Extract to your addons directory
- Enable it in the addon manager (named *FGA Vector Field Tools*)
- A new tab named *Vector Fields* should be visible in the tools panel
 
--------------------------------------------------------------------------------------------------------- 
 
## Notes  
 
###### Performance  
- This addon's performance is heavily dependent on the speed of your CPU and memory.
- Blender may stop responding during the Create and Calculate operations, but shouldn't crash.
- On vector fields with a density of less than 128^3, operations should take less than a minute, with lower density fields (<64^3) taking a few seconds at most.
- At maximum density (128^3), creating a new vector field takes about 20 seconds on my mid-range Core i5 based PC, and calculating velocities can take up to 2 minutes (after recent tweaks).
- Performance while editing reasonably sized (< 1 million vertices) vector fields is good, while a 128^3 volume can be painfully slow under the right (wrong) circumstances.
 
###### 128x128x128 and System Memory  
- Editing a 128x128x128 vector field requires a 64-bit system and Blender version, as well as a large amount (> 6-8 GB) of system memory.
- This is due to the amount of particles that need to have their dynamics cached (and the number of vertices in the volume mesh)
- To avoid running out of memory while editing very high resolution vector fields, you may want to lower your undo history steps.
- Using a disk cache for your particles may help, too. 


------------------------------------------------------------------------------------------------------- 
  
## Changelog:  
  
***1.2.1***:
- probably fixed noneType error messages *(Thank you to kkaja123 for reporting and looking into fixing it!)*
- moved the menu to the panels at the right side of the workspace

***1.2.0***:
- initial update to support Blender 2.8.

***1.1.5***:
- changed sorting of the calculation/velocity dropdown lists
- new calculation method: Vector Reflection
- added constraint to vector field volume, only moving the bounding box now moves the volume  

***1.1.4***:
- fix for display lines not updating when new velocities are calculated
- new calculation method: Cross Product  

***1.1.3***:
- removed the need for the update data/offsets buttons
- slight performance optimizations for display lines  

***1.1.2***:
- new presets can now be added/removed
- export should now work with any part of the vector field selected (or both)  

***1.1.0***:
- added support for selecting a physics preset to edit particle physics settings easily for selected vector field

***1.0.1***:
- renamed curve path tool to Wind Curve Force
- added editor for created curve wind force strength, distance + falloff
- the Ratio property should now work (apparently forgot to use the variable)  

***1.0.0***:
- *General:*
  - tools panel category renamed to *Vector Fields*
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
  - matched default scaling to (grid units x field density)
    - distances were at half scale before
    - density variable used for creation is now distance between particles
  - added undo functionality to *Generate* function
  - new velocity mode: Point
- *Curve Force Tool:*
  - changed curve force tool to create an object group to remove scene outliner clutter
  - fixed curve force fields' parenting issue
    - all transformations to the curve force object should now work
  - curve forces now display an arrow pointing in the force's direction  

***0.9.5***:
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

***0.9.1***:
- added different generation modes: *Replace, Additive, Average*
- added trail option for curve path (fade influence with curve position)
- changed the way invert and normalize work
- slight calculation performance tweak  

***0.9***:
- another performance tweak
- added invert, normalize, disable gravity options  

***0.8***:
- added import functionality
- massive speed improvement  

***0.5***:
- initial upload  
