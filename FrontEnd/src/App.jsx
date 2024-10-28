import { React, Component } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";

import Navbar from "./components/Navbar";
import MainPage from "./components/Pages/MainPage";
import GamePage from "./components/Pages/GamePage";
import AboutPage from "./components/Pages/AboutPage";
import RulesPage from "./components/Pages/RulesPage";


class App extends Component {
    constructor() {
        super();
    };

    render() {
        return (
            <div className="App">
                <Router>
                    <Routes>
                        <Route path="./home" element={<MainPage />} />
                        <Route path="./game" element={<GamePage />} />
                        <Route path="./about" element={<AboutPage />} />
                        <Route path="./rules" element={<RulesPage />} />
                    </Routes>
                </Router>

                <Navbar />
                <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
                    <MainPage />
                </div>
            </div>
        );
    };
}

export default App;