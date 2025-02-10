# origin_snap
Blender addon for manipulating object origin and location.

Pie Menu `Ctrl + W` with 4 operators:
- Origin to Geometry
- Origin to Selection (Edit Mode only) - calculates midpoint of selected mesh elements (vertex, edge or face) and snaps object origin to it - same as `Cursor to Selected` -> `Origin to 3D Cursor`
- Origin to World Origin - same as `Cursor to World Origin` -> `Origin to 3D Cursor`
- Object to World Origin - same as `Cursor to World Origin` -> `Selection to 3D Cursor`

Known issues
- undo works in multiple steps.
- does not work in Sculpt mode due to keybinding conflict

Tested Blender versions: 4.0.2, 4.2.0 (3805974b6fa8)