import json 
from typing import Dict

from engine.core.layer.LayerTile import LayerTile


class LayerBoard: 
    def __init__(self, file_path: str) -> None:
        self.tiles = self.load_board(file_path)
        self.pieces = []

    def load_board(self, file_path: str) -> Dict[str, Dict[str, LayerTile]]: 
        with open(file_path, 'r') as file:
            data = json.load(file)

        tiles = []
        for tile_name, tile_data in data.items(): 
            data = tile_data['data']
            tile = LayerTile(tile_name)
            tiles[tile_name] = tile

        for tile_name, layers in data.items():
            tile = tiles[tile_name]
            for layer_name, patterns in layers.items():
                patterns_ = []
                for pattern in patterns:
                    pattern_ = []
                    for possible_move in pattern:
                        tile_ = tiles['possible_move']
                        pattern_.append(tile_)
                    patterns_.append(pattern_)
                tile.set_layer(layer_name, patterns_)

        return tiles