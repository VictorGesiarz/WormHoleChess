import React, { useEffect } from "react";
import { useGLTF } from "@react-three/drei";

const ChessBoard = () => {
  const { scene } = useGLTF("models/WormHoleChess.glb");

  useEffect(() => {
    // Accessing the lights by name
    const light1 = scene.getObjectByName("Light1");
    const light2 = scene.getObjectByName("Light2");

    let LIGHT_INTENSITY = 50;
    if (light1) {
      light1.intensity = LIGHT_INTENSITY;
    }
    if (light2) {
      light2.intensity = LIGHT_INTENSITY;
    }

  }, [scene]);

  return <primitive object={scene} />;
};

export default ChessBoard;
