import { useState } from "react";	

const Pruebas = () => {
    const [count, setCount] = useState(null); 

	const increment = () => {
		setCount(prevCount => prevCount + 1); 
	};
	
	const setStart = () => {
		setCount(4); 
	}; 

	return (
        <div className="widget page Pruebas">
			<h1>Count: {count}</h1>
			<button onClick={ setStart }>Set</button>
			<button onClick={ increment }>+</button>
        </div>
    );
};

export default Pruebas;