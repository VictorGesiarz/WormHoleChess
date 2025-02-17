import React, { useEffect, useState, useRef } from "react";
import { useGLTF } from "@react-three/drei";
import * as THREE from 'three';

import chessBoardModle from "../../assets/models/WormHoleChess_with_pieces.glb";

const ChessBoard = () => {
    const { scene } = useGLTF(chessBoardModle);
    const [tiles, setTiles] = useState([]);
    const [selectedTile, setSelectedTile] = useState(null);
    const clickInProgress = useRef(false);

    // Define colors
    const ORIGINAL_WHITE = 0xFFFFFF; // Original white
    const ORIGINAL_BLACK = 0x3F3C3C; // Original black
    const WHITE = ORIGINAL_WHITE; // White
    const BLACK = ORIGINAL_BLACK; // Black
    const SELECTED_WHITE = 0xCE77FF; // Selected white
    const SELECTED_BLACK = 0xB737FF; // Selected black

    useEffect(() => {
        // Adjust light intensity
        const light1 = scene.getObjectByName("Light1");
        const light2 = scene.getObjectByName("Light2");
        console.log(light1)
        const LIGHT_INTENSITY = 30;
        if (light1) {
            light1.intensity = LIGHT_INTENSITY;
            console.log(light1.intensity)
        }
        if (light2) light2.intensity = LIGHT_INTENSITY;

        // Collect all tiles
        const allTiles = [];
        scene.traverse((object) => {
            if (object.name.includes("_T") || object.name.includes("_B")) {
                if (object.material.color.getHex() === ORIGINAL_WHITE) {
                    object.material.color.setHex(WHITE);
                }
                else if (object.material.color.getHex() === ORIGINAL_BLACK) {
                    object.material.color.setHex(BLACK);
                }
                allTiles.push(object);
                object.material = object.material.clone();
                object.userData = { onClick: () => handleTileClick(object) };
            }
        });
        setTiles(allTiles);
    }, [scene]);

    const handleTileClick = (tile) => {
        if (clickInProgress.current) return; // Prevent multiple calls
        clickInProgress.current = true;

        setTiles((prevTiles) => {
            console.log(prevTiles);
            return prevTiles;
        });

        setSelectedTile((prevSelectedTile) => {
            console.log(prevSelectedTile);

            // Deselect the current tile if it's already selected
            if (prevSelectedTile && prevSelectedTile.name === tile.name) {
                deselectTile(tile);
                return null;
            } else {
                // Deselect the previously selected tile
                if (prevSelectedTile) {
                    deselectTile(prevSelectedTile);
                }

                // Select the new tile
                selectTile(tile);
                return tile;
            }
        });

        setTimeout(() => {
            clickInProgress.current = false;
        }, 100);
    };

    const selectTile = (tile) => {
        const currentColor = tile.material.color.getHex();
        const selectedColor = currentColor === WHITE ? SELECTED_WHITE : SELECTED_BLACK;
        tile.material.color.setHex(selectedColor);
    };

    const deselectTile = (tile) => {
        const currentColor = tile.material.color.getHex();
        const originalColor = (currentColor === SELECTED_WHITE || currentColor === SELECTED_BLACK) ?
            (currentColor === SELECTED_WHITE ? WHITE : BLACK) : currentColor;
        tile.material.color.setHex(originalColor);
    };

    return (
        <primitive
            object={scene}
            onPointerDown={(event) => {
                const clickedObject = event.intersections[0]?.object;
                if (clickedObject?.userData?.onClick) {
                    clickedObject.userData.onClick();
                }
            }}
        />
    );
};

export default ChessBoard;