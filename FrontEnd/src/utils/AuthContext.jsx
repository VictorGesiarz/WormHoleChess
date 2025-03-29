import React, { createContext, useState, useEffect, useContext } from "react";
import { verifyToken } from "../utils/auth";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [isAuthenticated, setIsAuthenticated] = useState(!!token);

    useEffect(() => {
        async function checkAuth() {
            if (token) {
                const user = await verifyToken(token);
                if (user) {
                    setIsAuthenticated(true);
                    localStorage.setItem("token", token);
                } else {
                    logout();
                }
            } else {
                setIsAuthenticated(false);
            }
        }
        checkAuth();
    }, [token]);

    const login = (newToken) => {
        setToken(newToken);
        localStorage.setItem("token", newToken);
        setIsAuthenticated(true);
    };

    const logout = () => {
        setToken(null);
        setIsAuthenticated(false);
        localStorage.removeItem("token");
    };

    return (
        <AuthContext.Provider value={{ token, isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
