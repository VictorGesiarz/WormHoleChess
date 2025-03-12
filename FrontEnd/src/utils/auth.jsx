

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


export async function verifyToken(token) {
    if (!token) return false;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify_token`, {
            method: "GET",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
            throw new Error("Invalid token");
        }

        const data = await response.json();
        return data.User; // Return user info if token is valid
    } catch (error) {
        console.error("Token verification failed:", error);
        return false;
    }
}


export const decodeToken = (token) => {
    if (!token) return null;

    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload; // Contains email, user_id, etc.
    } catch (error) {
        console.error("Invalid token", error);
        return null;
    }
};
