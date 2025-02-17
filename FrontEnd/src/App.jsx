import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from "./components/SideBar";
import MainPage from './components/Pages/MainPage';
import GamePage from './components/Pages/GamePage';
import AboutPage from './components/Pages/AboutPage';
import RulesPage from './components/Pages/RulesPage';
import Pruebas from './components/Pages/Pruebas.jsx'; 

function App() {
    return (
        <div className='container'>
            <Router>
                <Navbar />
                <Routes>
                    <Route path="/" element={<MainPage />} />
                    <Route path="/game" element={<GamePage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/rules" element={<RulesPage />} />
                    <Route path="/pruebas" element={<Pruebas />} />
                </Routes>
            </Router>
        </div>
    );
}

export default App;
