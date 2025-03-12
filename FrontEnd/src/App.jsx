import React, { useContext } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, AuthContext } from "./utils/AuthContext";

import SideBar from "./components/SideBar";
import LoginPage from "./components/Pages/Authentication/LoginPage";
import RegisterPage from "./components/Pages/Authentication/RegisterPage";
import MainPage from "./components/Pages/MainPage";
import AboutPage from "./components/Pages/AboutPage";
import RulesPage from "./components/Pages/RulesPage";
import LobbyPage from "./components/Pages/LobbyPage";
import GamePage from "./components/Pages/GamePage";


const PrivateRoute = ({ children }) => {
    const { isAuthenticated } = useContext(AuthContext);
    return isAuthenticated ? children : <Navigate to="/login" />;
};

// Layout for pages with Sidebar
const MainLayout = ({ children }) => {
    const { token, logout } = useContext(AuthContext);
    return (
        <div className="container">
            <SideBar token={token} logout={logout} />
            <div className="content">{children}</div>
        </div>
    );
};

// Layout for authentication pages (e.g., login, register)
const AuthLayout = ({ children }) => {
    return <div className="auth-container">{children}</div>;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* Authentication Routes */}
                    <Route path="/login" element={<AuthLayout><LoginPage /></AuthLayout>} />
                    <Route path="/register" element={<AuthLayout><RegisterPage /></AuthLayout>} />

                    {/* Public Pages */}
                    <Route path="/" element={<MainLayout><MainPage /></MainLayout>} />
                    <Route path="/about" element={<MainLayout><AboutPage /></MainLayout>} />
                    <Route path="/rules" element={<MainLayout><RulesPage /></MainLayout>} />

                    {/* Protected Routes */}
                    <Route path="/lobby" element={<PrivateRoute><MainLayout><LobbyPage /></MainLayout></PrivateRoute>} />
                    <Route path="/game/:gameCode" element={<PrivateRoute><MainLayout><GamePage /></MainLayout></PrivateRoute>} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
