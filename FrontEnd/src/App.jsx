import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from "./components/NavBar";
import MainPage from './components/Pages/MainPage';
import GamePage from './components/Pages/GamePage';
import AboutPage from './components/Pages/AboutPage';
import RulesPage from './components/Pages/RulesPage';

function App() {
    return (
        <Router>
            <Navbar />
            <div className="container">
                <Routes>
                    <Route path="/home" element={<MainPage />} />
                    <Route path="/game" element={<GamePage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/rules" element={<RulesPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
