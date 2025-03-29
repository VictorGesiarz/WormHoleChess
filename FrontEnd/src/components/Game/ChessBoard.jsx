import React, { useEffect, useState, useRef } from "react";
import { useGLTF } from "@react-three/drei";
import * as THREE from 'three';

import tilePositions from "../../assets/models/tile_positions.json";
import chessBoardModel from "../../assets/models/Board.glb";
import chessPiecesModel from "../../assets/models/Pieces.glb";
import { useWebSocket } from "../../utils/WebSocketProvider";


// Define tile colors 
const boardColors = {
    originalWhite: 0xFFFFFF,
    originalBlack: 0x3F3C3C, 
    white: 0xFFFFFF, 
    black: 0x3F3C3C,
    selectedWhite: 0xCE77FF, 
    selectedBlack: 0xB737FF,
    possibleMoveWhite: 0x77ffce, 
    possibleMoveBlack: 0x5fcca5, 
    checkWhite: 0xff778d,
    checkBlack: 0xcc5f71
}; 

const LIGHT_INTENSITY = 30; 

// Define piece colors
const pieceColors = {
    white: 0xFFFFFF,
    black: 0x050505,
    blue: 0x5C7090,
    red: 0x8C4E56
};


const ChessBoard = ({ initialState }) => {
    const { scene: board } = useGLTF(chessBoardModel);
    const { scene: piecesScene } = useGLTF(chessPiecesModel);
    const { socket } = useWebSocket(); 
    
    const [tiles, setTiles] = useState([]);
    const [pieces, setPieces] = useState([]); 
    const selectedTile = useRef(null); 
    const selectedPiece = useRef(null); 
    const clickInProgress = useRef(false);
    const initialPointerPosition = useRef({ x: 0, y: 0 });
    const isDragging = useRef(false);
    const DRAG_THRESHOLD = 10;  

    const [state, setState] = useState({}); 
    const [possibleMoves, setPossibleMoves] = useState({}); 

    useEffect(() => {
        if (!board) return;
    
        // Adjust light intensity
        const light1 = board.getObjectByName("Light1");
        const light2 = board.getObjectByName("Light2");
    
        if (light1) light1.intensity = LIGHT_INTENSITY;
        if (light2) light2.intensity = LIGHT_INTENSITY;
    
        // Collect and initialize tiles
        const allTiles = [];
        board.traverse((object) => {
            if (object.name.includes("_T") || object.name.includes("_B")) {
                if (object.material.color.getHex() === boardColors.originalWhite) {
                    object.material.color.setHex(boardColors.white);
                } else if (object.material.color.getHex() === boardColors.originalBlack) {
                    object.material.color.setHex(boardColors.black);
                }
                allTiles.push(object);
                object.material = object.material.clone();
                object.userData = { tileOnClick: () => handleTileRightClick(object) };
            }
        });
        setTiles(allTiles);
    }, [board]);
    

    useEffect(() => {
        if (!piecesScene || !initialState) return;
    
        const newPieces = [];
        Object.entries(initialState).forEach(([team, teamPieces]) => {
            Object.entries(teamPieces).forEach(([type, positions]) => {
                positions.forEach(tile => {
                    const tileInfo = tilePositions[tile];
                    if (!tileInfo) {
                        console.error(`No position found for tile: ${tile}`);
                        return;
                    }
    
                    const pieceTemplate = piecesScene.getObjectByName(type);
                    if (!pieceTemplate) {
                        console.error(`No model found for piece: ${type}`);
                        return;
                    }
    
                    // Clone and position the piece
                    const pieceClone = pieceTemplate.clone();
                    pieceClone.position.set(tileInfo.position.x, tileInfo.position.y, tileInfo.position.z);
                    pieceClone.rotation.set(tileInfo.rotation.x, tileInfo.rotation.y, tileInfo.rotation.z);
                    pieceClone.material = pieceClone.material.clone();
                    pieceClone.material.color.setHex(pieceColors[team]);
                    
                    pieceClone.userData = { pieceOnClick: () => handlePieceClick(pieceClone) };
                    
                    newPieces.push(pieceClone);
                });
            });
        });
    
        setPieces(newPieces);
    }, [piecesScene, state]);

    
    useEffect(() => {
        if (!socket) return;
    
        const handleGameMessage = (event) => {
            const data = JSON.parse(event.data); 

            if (data.type === "move_made" || data.type === "game_start") {
                console.log(data.type); 
                setState(data.state); 
                setPossibleMoves(data.possibleMoves); 
            }
            else {
                console.log("Message recieved but wrong type"); 
            }
        };
    
        socket.addEventListener("message", handleGameMessage);
    
        return () => {
            socket.removeEventListener("message", handleGameMessage);
        };
    }, [socket]);
    

    // - - - - - - - - - - - - - - - - - - - - PIECE SELECTION - - - - - - - - - - - - - - - - - - - - 
    const handlePieceClick = (piece) => {

    }
    // - - - - - - - - - - - - - - - - - - - - RIGHT CLICK SELECTION - - - - - - - - - - - - - - - - - - - - 


    // - - - - - - - - - - - - - - - - - - - - RIGHT CLICK SELECTION - - - - - - - - - - - - - - - - - - - - 
    const handleTileRightClick = (tile) => {
        if (clickInProgress.current) return;
        clickInProgress.current = true;

        setTimeout(() => {
            clickInProgress.current = false;
        }, 100);

        // Deselect the current tile if it's already selected
        if (selectedTile.current && selectedTile.current.name === tile.name) {
            deselectTile(tile);
            return null;
        } 
        else {
            // Deselect the previously selected tile
            if (selectedTile.current) {
                deselectTile(selectedTile.current);
            }

            // Select the new tile
            selectTile(tile);
            return tile;
        }
    };

    const selectTile = (tile) => {
        const currentColor = tile.material.color.getHex();
        const selectedColor = currentColor === boardColors.white ? boardColors.selectedWhite : boardColors.selectedBlack;
        tile.material.color.setHex(selectedColor);
    };

    const deselectTile = (tile) => {
        const currentColor = tile.material.color.getHex();
        const originalColor = (currentColor === boardColors.selectedWhite || currentColor === boardColors.selectedBlack) ?
            (currentColor === boardColors.selectedWhite ? boardColors.white : boardColors.black) : currentColor;
        tile.material.color.setHex(originalColor);
    };
    // - - - - - - - - - - - - - - - - - - - - RIGHT CLICK SELECTION - - - - - - - - - - - - - - - - - - - - 


    // - - - - - - - - - - - - - - - - - - - - CLICK AND DRAG HANDLER - - - - - - - - - - - - - - - - - - - - 
    // Handle pointer down (store initial position)
    const handlePointerDown = (event) => {
        if (clickInProgress.current) return;
        clickInProgress.current = true;
        
        initialPointerPosition.current = {
            x: event.clientX,
            y: event.clientY
        };

        const clickedObject = event.intersections[0]?.object;
        if (clickedObject?.userData?.onRightClick) {
            clickedObject.userData.onRightClick();
        }
    };

    // Handle pointer move (check if user is dragging)
    const handlePointerMove = (event) => {
        if (!initialPointerPosition.current) return;

        const deltaX = event.clientX - initialPointerPosition.current.x;
        const deltaY = event.clientY - initialPointerPosition.current.y;

        // If the pointer has moved beyond the threshold, it's considered a drag
        if (Math.sqrt(deltaX * deltaX + deltaY * deltaY) > DRAG_THRESHOLD) {
            isDragging.current = true;
        }
    };

    // Handle pointer up (check if it was a click or drag)
    const handlePointerUp = () => {
        if (isDragging.current) {
            // Prevent selecting tile if it was a drag
            console.log("Drag detected, no selection.");
            return false; 
        } else {
            console.log("Drag not detected."); 
            return true; 
        }
    };
    // - - - - - - - - - - - - - - - - - - - - CLICK AND DRAG HANDLER - - - - - - - - - - - - - - - - - - - - 


    return (
        <group>
            <primitive 
                object={board} 
                onPointerDown={handlePointerDown}
                onPointerMove={handlePointerMove}
                onPointerUp={(event) => {
                    if (event.button === 2 && handlePointerUp) {  // Right Click
                        const clickedObject = event.intersections[0]?.object;
                        if (clickedObject?.userData?.tileOnClick) {
                            clickedObject.userData.tileOnClick();
                        }
                    }
                }}
            />
            {pieces.map((piece, index) => (
                <primitive 
                    key={index} 
                    object={piece} 
                    onPointerDown={handlePointerDown}
                    onPointerMove={handlePointerMove}
                    onPointerUp={(event) => {
                        if (event.button === 1 && handlePointerUp) {  // Left Click
                            const clickedObject = event.intersections[0]?.object;
                            if (clickedObject?.userData?.pieceOnClick) {
                                clickedObject.userData.pieceOnClick();
                            }
                        }
                    }}                
                />
            ))}
        </group>
    );
};

export default ChessBoard;