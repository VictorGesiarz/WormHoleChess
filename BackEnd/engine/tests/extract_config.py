from engine.core.matrices.MatrixBoard import LayerMatrixBoard


def extract(): 
    b = LayerMatrixBoard((8, 8), 'normal', load_from_file=False)

    print("Nodes:", b.nodes)
    print("Adjacency list:", b.adjacency_list)
    print("Patterns offsets:", b.patterns_offsets)
    print("Pieces offsets:", b.pieces_offsets)
    print("Tiles offsets:", b.tiles_offsets)
    print("Pieces:", b.pieces)

    print(b.check_size())

    b.save_matrices()
        
extract()