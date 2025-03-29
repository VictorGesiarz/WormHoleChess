import { createContext, useContext, useState } from "react";
import { API_WEB_SOCKET_URL } from "./ApiUrls";

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);

    const connectWebSocket = (code) => {
        if (socket) {
            console.warn("WebSocket is already connected.");
            return;
        }

        const ws = new WebSocket(`${API_WEB_SOCKET_URL}/${code}`);

        ws.onopen = () => {
            console.log("WebSocket connection established.");
        };

        ws.onclose = () => {
            console.log("WebSocket closed.");
            setSocket(null);
        };

        setSocket(ws);
    };

    const disconnectWebSocket = () => {
        if (socket) {
            socket.close();
            setSocket(null);
        }
    };

    return (
        <WebSocketContext.Provider value={{ socket, connectWebSocket, disconnectWebSocket }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => useContext(WebSocketContext);
