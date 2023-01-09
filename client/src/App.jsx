import React from "react";
import { HashRouter as Router, Route, Routes } from "react-router-dom";
import SignUp from "./screens/SignUp";
import SignIn from "./screens/SignIn";

function App() {
	return (
		<Router>
			<Routes>
				<Route path="/signup/" element={<SignUp />} />
				<Route path="/signin/" element={<SignIn />} />
			</Routes>
		</Router>
	);
}

export default App;
