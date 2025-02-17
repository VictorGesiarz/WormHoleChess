import bpy
import json
import re  # For regex to clean object names

# Name of the piece to duplicate
piece_name = "Rook"
vertex_group_name = "Group"  # Change if needed

# Dictionary to store positions and rotations
tile_data = {}

# Function to clean the tile name (remove Blender's .001, .002, etc.)
def clean_tile_name(name):
    # Keep only the part before the first "."
    return re.split(r'\.\d+$', name)[0]  

# Get reference piece
ref_piece = bpy.data.objects.get(piece_name)
if not ref_piece:
    print(f"Error: Piece '{piece_name}' not found!")
else:
    # Iterate through all tiles (match names containing _T or _B)
    for tile in bpy.data.objects:
        if "_T" in tile.name or "_B" in tile.name:
            # Clean the tile name
            clean_name = clean_tile_name(tile.name)

            # Duplicate the reference piece
            temp_piece = ref_piece.copy()
            bpy.context.collection.objects.link(temp_piece)

            # Add Copy Location Constraint
            loc_constraint = temp_piece.constraints.new(type="COPY_LOCATION")
            loc_constraint.target = tile
            loc_constraint.subtarget = vertex_group_name  # Assign vertex group

            # Add Copy Rotation Constraint
            rot_constraint = temp_piece.constraints.new(type="COPY_ROTATION")
            rot_constraint.target = tile
            rot_constraint.subtarget = vertex_group_name  # Assign vertex group

            # Force Blender to update transformations
            bpy.context.view_layer.update()

            # Store the computed position and rotation
            tile_data[clean_name] = {
                "position": list(temp_piece.location),
                "rotation": list(temp_piece.rotation_euler)
            }

            # Delete the temporary piece
            bpy.data.objects.remove(temp_piece)

# Save to JSON file
json_path = "tile_positions.json"
with open(json_path, "w") as f:
    json.dump(tile_data, f, indent=4)

print(f"✅ Exported tile positions to {json_path}")
