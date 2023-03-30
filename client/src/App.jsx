import React from "react";
import {
	HashRouter as Router,
	Route,
	Routes,
	Navigate,
} from "react-router-dom";

import Container from "@mui/material/Container";

import "./App.css";
import SignUp from "./screens/SignUp";
import SignIn from "./screens/SignIn";
import RecipeList from "./screens/RecipeList";

import Header from "./components/Header";

function App() {
	return (
		<Router>
			<Header />
			<Routes>
				<Route path="/signup/" element={<SignUp />} />
				<Route path="/signin/" element={<SignIn />} />
				<Route
					path="/recipes/"
					element={
						<div className="pic-bg">
							<div className="dim">
								<Container
									maxWidth="lg"
									sx={{ pb: "3vh", minHeight: "100vh" }}>
									<RecipeList />
								</Container>
							</div>
						</div>
					}
				/>
				<Route path="*" element={<Navigate to="/recipes/" replace />} />
			</Routes>
		</Router>
	);
}

export default App;
