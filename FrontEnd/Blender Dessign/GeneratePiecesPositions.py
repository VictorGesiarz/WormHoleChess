import bpy

piece_name = "rook_white"
vertex_group_name = "Group"
collection_name = "PLACEMENT_FOLDER"

# Get or create the collection to hold all pieces
if collection_name in bpy.data.collections:
    target_collection = bpy.data.collections[collection_name]
else:
    target_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(target_collection)

# Get the reference piece
ref_piece = bpy.data.objects.get(piece_name)

if not ref_piece:
    print(f"❌ Piece '{piece_name}' not found!")
else:
    for tile in bpy.data.objects:
        if "_T" in tile.name or "_B" in tile.name:

            # Duplicate and rename
            temp_piece = ref_piece.copy()
            temp_piece.data = ref_piece.data.copy()
            temp_piece.name = f"POSITION_{tile.name}"

            # Add to the target collection
            target_collection.objects.link(temp_piece)

            # Add constraints
            loc = temp_piece.constraints.new(type="COPY_LOCATION")
            loc.target = tile
            loc.subtarget = vertex_group_name

            rot = temp_piece.constraints.new(type="COPY_ROTATION")
            rot.target = tile
            rot.subtarget = vertex_group_name

            # Apply constraints visually
            bpy.context.view_layer.objects.active = temp_piece
            bpy.ops.object.select_all(action='DESELECT')
            temp_piece.select_set(True)

            bpy.ops.object.visual_transform_apply()

            # Remove constraints
            temp_piece.constraints.clear()

print("✅ All POSITION_ pieces created and grouped under:", collection_name)
