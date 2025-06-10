import React, { useEffect, useState, useRef } from "react";
import { useGLTF } from "@react-three/drei";
import { useNavigate } from "react-router-dom";
import * as THREE from 'three';

import { API_BASE_URL } from "../../utils/ApiUrls";


// Define tile colors 
const boardColors = {
    originalWhite: 0xFFFFFF,
    originalBlack: 0x3F3C3C,
    white: 0xFFFFFF,
    black: 0x3F3C3C,
    selectedWhite: 0xB39DDB,
    selectedBlack: 0x6C5E84,
    possibleMoveWhite: 0x96D3CE,
    possibleMoveBlack: 0x4C7874,
    // checkWhite: 0xff778d,
    // checkBlack: 0xcc5f71
};

const LIGHT_INTENSITY = 30;

// Define piece colors
const pieceColors = {
    white: 0xFFFFFF,
    black: 0x050505,
    blue: 0x5C7090,
    red: 0x8C4E56,
    dead: 0x808080 // Color for dead pieces
};
// const pieceColors = {
//     white: 0xE7E7E7,
//     black: 0x151515,
//     blue: 0xFFC288,
//     red: 0xB5B5B5,
//     dead: 0x808080 // Color for dead pieces
// };

const ChessBoard = ({
    gameId,
    gameType,
    boardSize,
    state,
    setStates,
    turn,
    setTurn,
    players,
    setHistory,
}) => {
    const boardModelPath = `/assets/models/${boardSize}x${boardSize}_${gameType}.glb`;
    const { scene: board } = useGLTF(boardModelPath);
    const { scene: piecesScene } = useGLTF('/assets/models/Pieces.glb');

    const [otherObjects, setOtherObjects] = useState([]);
    const positions = useRef({});
    const [tiles, setTiles] = useState([]);
    const [pieces, setPieces] = useState([]);

    const selectedTile = useRef(null);
    const selectedPiece = useRef(null);
    const [highlightedTiles, setHighlightedTiles] = useState([]);

    useEffect(() => {
        if (!board) return;

        const extractedLights = [];
        const nonTileObjects = [];
        // Adjust light intensity
        const light1 = board.getObjectByName("Light1");
        const light2 = board.getObjectByName("Light2");

        if (light1) {
            extractedLights.push(light1);
            light1.intensity = LIGHT_INTENSITY;
            light1.color.set(0xffffff);
        }
        if (light2) {
            extractedLights.push(light2);
            light2.intensity = LIGHT_INTENSITY;
            light2.color.set(0xffffff);
        }

        setOtherObjects(extractedLights);

        // Collect and initialize tiles
        const allTiles = [];
        const positionsDict = {};
        board.traverse((object) => {
            if (object.name.startsWith("POSITION_")) {
                const tileName = object.name.replace("POSITION_", "");
                positionsDict[tileName] = {
                    position: object.position.clone(),         // THREE.Vector3
                    quaternion: object.quaternion.clone(),     // THREE.Quaternion
                }
                object.visible = false;
            }
            else if (
                /_T$/.test(object.name) ||
                /_B$/.test(object.name) ||
                /^[a-h][1-8]$/i.test(object.name)
            ) {
                let tileColor = null;

                if (object.material.color.getHex() === boardColors.originalWhite) {
                    object.material.color.setHex(boardColors.white);
                    tileColor = "white";
                } else if (object.material.color.getHex() === boardColors.originalBlack) {
                    object.material.color.setHex(boardColors.black);
                    tileColor = "black";
                }

                allTiles.push(object);
                object.material = object.material.clone();

                object.userData = {
                    tileOnClick: () => handleTileRightClick(object),
                    originalColor: object.material.color.getHex(),
                    tileName: object.name,
                    tileColor: tileColor,
                };
            }
            else {
                nonTileObjects.push(object);
            }
        });
        setTiles(allTiles);

        positions.current = positionsDict;

        setOtherObjects([...extractedLights, ...nonTileObjects]);
    }, [board]);


    useEffect(() => {
        if (!piecesScene || !state) return;
        const newPieces = [];

        state.forEach(([type, team, tile]) => {
            const tileInfo = positions.current[tile];
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
            pieceClone.position.copy(tileInfo.position);
            pieceClone.quaternion.copy(tileInfo.quaternion);

            pieceClone.material = pieceClone.material.clone();
            pieceClone.material.color.setHex(pieceColors[team]);
            pieceClone.userData = {
                pieceOnClick: () => handlePieceClick(pieceClone),
                tileName: tile,
            };

            newPieces.push(pieceClone);
        });

        setPieces(newPieces);

    }, [piecesScene, state]);


    // - - - - - - - - - - - - HANDLE POINTER EVENTS - - - - - - - - - - - - - 
    const handlePieceClick = (piece) => {
        const tileName = piece.userData.tileName;
        if (!tileName) return;

        const tile = tiles.find(t => t.name === tileName);
        if (!tile) return;

        const pieceData = state.find(
            ([type, team, tName]) => tName === tileName && team !== "dead"
        );

        if (!pieceData) return;
        const [pieceType, pieceTeam] = pieceData;

        handleBoardClick(tile, pieceType, pieceTeam);
    };

    const handleTileClick = (tile) => {
        const pieceData = state.find(
            ([type, team, tileName]) => tileName === tile.name && team !== "dead"
        ) || [null, null];

        const [pieceType, pieceTeam] = pieceData;
        handleBoardClick(tile, pieceType, pieceTeam);
    };

    const pointerStart = useRef({ x: 0, y: 0, time: 0 });

    const handlePointerDown = (e) => {
        pointerStart.current = {
            x: e.clientX,
            y: e.clientY,
            time: performance.now()
        };
    };

    const handlePointerUp = (e, target, isPiece = false) => {
        const dx = Math.abs(e.clientX - pointerStart.current.x);
        const dy = Math.abs(e.clientY - pointerStart.current.y);
        const dt = performance.now() - pointerStart.current.time;

        if (dx < 5 && dy < 5 && dt < 500) {
            if (target === null) {
                resetTileColors();
                selectedTile.current = null;
                selectedPiece.current = null;
                setHighlightedTiles([]);
            }

            const [closest] = e.intersections;
            if (!closest || closest.object !== target) return;

            e.stopPropagation();  // prevent bubbling
            if (isPiece) {
                handlePieceClick(target);
            } else {
                handleTileClick(target);
            }
        }
    };

    const resetTileColors = () => {
        highlightedTiles.forEach(tile => {
            tile.material.color.setHex(tile.userData.originalColor);
        });
    };

    // - - - - - - - - - - - - HANDLE TILE SELECTION - - - - - - - - - - - - - 
    const handleTileSelection = (tile, pieceType, pieceTeam) => {


        resetTileColors();
        selectedTile.current = null;
        selectedPiece.current = null;
        setHighlightedTiles([]);
        if (!pieceType || pieceTeam !== players[turn.turn].color) return;

        selectedTile.current = tile;
        selectedPiece.current = pieceType;
        const toTiles = turn.validMoves
            .filter(([from, to]) => from === tile.name)
            .map(([_, to]) => to);

        const toHighlight = tiles.filter(t => toTiles.includes(t.name));
        toHighlight.forEach(t => {
            if (t.userData.originalColor === boardColors.white) {
                t.material.color.setHex(boardColors.possibleMoveWhite);
            } else if (t.userData.originalColor === boardColors.black) {
                t.material.color.setHex(boardColors.possibleMoveBlack);
            }
        });

        if (tile.userData.originalColor === boardColors.white) {
            tile.material.color.setHex(boardColors.selectedWhite);
        } else if (tile.userData.originalColor === boardColors.black) {
            tile.material.color.setHex(boardColors.selectedBlack);
        }

        setHighlightedTiles([tile, ...toHighlight]);
    };


    const handleBoardClick = (clickedTile, pieceType, pieceTeam) => {
        if (!selectedTile.current) {
            handleTileSelection(clickedTile, pieceType, pieceTeam);
            return;
        }

        const fromTileName = selectedTile.current.name;
        const toTileName = clickedTile.name;

        const isValidMove = turn.validMoves.some(
            ([from, to]) => from === fromTileName && to === toTileName
        );

        if (isValidMove) {
            makeMove(fromTileName, toTileName);
        } else {
            handleTileSelection(clickedTile, pieceType, pieceTeam);
        }
    };


    // - - - - - - - - - - - - HANDLE MOVE - - - - - - - - - - - - - 
    const makeMove = async (from, to) => {
        try {
            const response = await fetch(`${API_BASE_URL}/game-local/make-move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gameId,
                    from_tile: from,
                    to_tile: to,
                }),
            });

            if (!response.ok) throw new Error('Move failed');

            const data = await response.json();

            setStates(prevStates => ({
                ...prevStates,
                ...data.state
            }));
            setTurn(data.turn);

            let moveDescription = '';
            if (players.length === 4) {
                moveDescription = `${selectedPiece.current}\n${from}\n${to}`;
            } else {
                moveDescription = `${selectedPiece.current} ${from} - ${to}`;
            }
            const historyEntry = {
                move: moveDescription,
                turn: data.turn,
                killedPlayer: data.killed_player,
                winner: data.winner,
            };

            console.log("GAME STATE:", data.game_finished); 
            console.log("WINNER:", data.winner);

            setHistory(prevHistory => [...prevHistory, historyEntry]);

            resetTileColors();
            selectedTile.current = null;
            selectedPiece.current = null;
            setHighlightedTiles([]);

        } catch (error) {
            console.error("Move error:", error);
        }
    };


    // - - - - - - - - - - - - PAGE CONTENT - - - - - - - - - - - - - 
    return (
        <group>
            <mesh
                scale={[100, 100, 100]}
                onPointerDown={handlePointerDown}
                onPointerUp={(e) => handlePointerUp(e, null, false)} // null target = "air"
            >
                <boxGeometry args={[1, 1, 1]} />
                <meshBasicMaterial
                    color={0x000000}
                    transparent={true}
                    opacity={0}
                    side={THREE.BackSide}
                />
            </mesh>
            {otherObjects.map((light, i) => (
                <primitive key={i} object={light} />
            ))}
            {tiles.map((tile, index) => (
                <primitive
                    key={index}
                    object={tile}
                    onPointerDown={handlePointerDown}
                    onPointerUp={(e) => handlePointerUp(e, tile, false)}
                />
            ))}
            {pieces.map((piece, index) => (
                <primitive
                    key={index}
                    object={piece}
                    onPointerDown={handlePointerDown}
                    onPointerUp={(e) => handlePointerUp(e, piece, true)}
                />
            ))}
        </group>
    );
};

export default ChessBoard;