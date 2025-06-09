import { useRef, useEffect } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { Euler } from "three";


const CameraControls = () => {
    const { scene, camera, gl } = useThree();
    const lastMousePos = useRef({ x: 0, y: 0 });
    const isDragging = useRef(false);
    const yaw = useRef(0);
    const pitch = useRef(0);
    const distance = useRef(10);

    // Center the world in front of the camera on mount
    useEffect(() => {

        scene.position.set(0, 0, -distance.current);
        camera.position.set(0, 0, 0);
        camera.lookAt(0, 0, -distance.current);

        // Mouse event handlers
        const onMouseDown = (e) => {
            isDragging.current = true;
            lastMousePos.current = { x: e.clientX, y: e.clientY };
        };

        const onMouseUp = () => {
            isDragging.current = false;
        };

        const onMouseMove = (e) => {
            if (!isDragging.current) return;

            const deltaX = (e.clientX - lastMousePos.current.x) * 0.005;
            const deltaY = (e.clientY - lastMousePos.current.y) * 0.005;

            pitch.current += deltaY;

            // Invert yaw if camera is upside down
            const isUpsideDown = Math.cos(pitch.current) < 0;
            yaw.current += isUpsideDown ? -deltaX : deltaX;

            lastMousePos.current = { x: e.clientX, y: e.clientY };
        };

        // Touch event handlers
        const onTouchStart = (e) => {
            if (e.touches.length === 1) {
                isDragging.current = true;
                lastMousePos.current = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        };

        const onTouchMove = (e) => {
            console.log("HERE")
            if (!isDragging.current || e.touches.length !== 1) return;

            document.title = `Upside down: ${Math.cos(pitch.current) < 0}`;


            const touch = e.touches[0];
            const deltaX = (touch.clientX - lastMousePos.current.x) * 0.005;
            const deltaY = (touch.clientY - lastMousePos.current.y) * 0.005;

            pitch.current += deltaY;

            // Clamp pitch to avoid flipping
            const maxPitch = Math.PI / 2 - 0.001;
            const minPitch = -Math.PI / 2 + 0.001;
            pitch.current = Math.max(minPitch, Math.min(maxPitch, pitch.current));

            // 👇 Invert yaw when pitch is upside down (looking up past the horizon)
            const isUpsideDown = Math.cos(pitch.current) < 0;
            console.log(isUpsideDown);
            yaw.current += isUpsideDown ? -deltaX : deltaX;

            lastMousePos.current = { x: touch.clientX, y: touch.clientY };
        };

        const onTouchEnd = () => {
            isDragging.current = false;
        };

        // Mouse and touch event listeners
        gl.domElement.addEventListener("mousedown", onMouseDown);
        gl.domElement.addEventListener("mousemove", onMouseMove);
        gl.domElement.addEventListener("mouseup", onMouseUp);
        gl.domElement.addEventListener("wheel", onWheel);
        document.addEventListener("touchstart", onTouchStart);
        document.addEventListener("touchmove", onTouchMove);
        document.addEventListener("touchend", onTouchEnd);

        return () => {
            gl.domElement.removeEventListener("mousedown", onMouseDown);
            gl.domElement.removeEventListener("mousemove", onMouseMove);
            gl.domElement.removeEventListener("mouseup", onMouseUp);
            gl.domElement.removeEventListener("wheel", onWheel);
            document.removeEventListener("touchstart", onTouchStart);
            document.removeEventListener("touchmove", onTouchMove);
            document.removeEventListener("touchend", onTouchEnd);
        };
    }, [scene, camera, gl]);

    // Wheel event for zooming
    const onWheel = (e) => {
        distance.current = Math.max(3, Math.min(20, distance.current + e.deltaY * 0.01));
    };

    // Frame update
    useFrame(() => {
        const euler = new Euler(pitch.current, yaw.current, 0, "YXZ");
        scene.rotation.set(euler.x, euler.y, 0);
        camera.position.set(0, 0, 0);
        scene.position.set(0, 0, -distance.current);
        camera.lookAt(0, 0, -distance.current);
    });

    return null;
};


export default CameraControls; 