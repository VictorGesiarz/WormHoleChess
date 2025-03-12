import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { IoArrowBack } from "react-icons/io5"; 
import "./LoginPage.css";

function RegisterPage() {
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState(""); // Added username field
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        const userData = {
            email,
            username,
            password,
        };

        try {
            const response = await fetch("http://127.0.0.1:8000/auth/user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(userData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Registration failed");
            }

            alert("Registration successful! You can now log in.");
            navigate("/login");
        } catch (error) {
            console.error("Registration error:", error);
            alert(error.message);
        }
    };

    return (
		<div className="widget box">
			{/* Back Arrow */}
			<button className="back-button" onClick={() => navigate("/")}>
				<IoArrowBack size={24} /> Back
			</button>

			<h2>Register</h2>
			<form onSubmit={handleRegister}>
				<input
					className="input"
					type="email"
					placeholder="Email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					required
				/>
				<input
					className="input"
					type="text"
					placeholder="Username"
					value={username}
					onChange={(e) => setUsername(e.target.value)}
					required
				/>
				<input
					className="input"
					type="password"
					placeholder="Password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					required
				/>
				<input
					className="input"
					type="password"
					placeholder="Confirm Password"
					value={confirmPassword}
					onChange={(e) => setConfirmPassword(e.target.value)}
					required
				/>
				<button type="submit" className="button">Register</button>
			</form>
			<p>
				Already have an account? <Link to="/login">Login here</Link>
			</p>
		</div>
    );
}

export default RegisterPage;
