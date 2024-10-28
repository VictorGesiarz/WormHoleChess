import { React, Component } from "react";
import { useNavigate } from "react-router-dom";
import "./Navbar.css";


class Navbar extends Component {
    constructor() {
        super();
    };

    navigate = useNavigate(); // Hook to access navigation

    render() {
        return (
            <nav className="navbar">
                <div className="navbar-panel">
                    VG
                </div>
                <ul className="navbar-links">
                    <li><button onClick={this.navigate("/home")}>Home</button></li>
                    <li><button onClick={this.navigate("/about")}>About</button></li>
                    <li><button onClick={this.navigate("/rules")}>Rules</button></li>
                </ul>
            </nav>
        );
    };
};

export default Navbar;