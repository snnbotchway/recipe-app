import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import axios from "axios";

import { createTheme, ThemeProvider } from "@mui/material/styles";
import Typography from "@mui/material/Typography";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";

import RecipeCard from "../components/RecipeCard";
import Loader from "../components/Loader";

const theme = createTheme();

function RecipeList() {
	const [recipes, setRecipes] = useState([]);
	const [loading, setLoading] = useState(true);
	const navigate = useNavigate();

	useEffect(() => {
		const token = localStorage.getItem("token");
		if (!token) {
			navigate("/signin");
		}

		axios
			.get("/api/recipe/recipes/", {
				headers: {
					Authorization: token,
				},
			})
			.then((response) => {
				setRecipes(response.data);
				setLoading(false);
			})
			.catch((error) => {
				console.error(error);
			});
	}, [navigate]);

	return (
		<ThemeProvider theme={theme}>
			<Typography
				style={{ paddingTop: "10vh" }}
				variant="h4"
				gutterBottom
				color="#fff">
				YOUR RECIPES
			</Typography>
			{loading ? (
				<Loader />
			) : (
				<Grid2 marginTop={1} container spacing={3}>
					{recipes.map((recipe) => (
						<Grid2 key={recipe.id} item>
							<RecipeCard
								key={recipe.id}
								id={recipe.id}
								time={recipe.time_minutes}
								price={recipe.price}
								title={recipe.title}
								image={
									Boolean(recipe.images.length)
										? recipe.images[0].image
										: ""
								}
							/>
						</Grid2>
					))}
				</Grid2>
			)}
		</ThemeProvider>
	);
}

export default RecipeList;
