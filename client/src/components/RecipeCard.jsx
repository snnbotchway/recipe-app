import * as React from "react";
import { Link } from "react-router-dom";

import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";

export default function RecipeCard({ id, title, price, time, image }) {
	return (
		<Card sx={{ width: 345, height: 470 }}>
			<Link to={`/recipe/view/${id}/`} style={{ textDecoration: "none" }}>
				<CardMedia
					component="img"
					alt="recipe-image"
					height="260"
					image={image}
				/>
			</Link>
			<CardContent>
				<Typography gutterBottom variant="h5" component="div">
					{title}
				</Typography>
				<Typography
					display="block"
					variant="caption"
					color="text.secondary">
					{`Time: ${time} mins`}
				</Typography>
				<Typography variant="caption" color="text.secondary">
					{`Price: $${price}`}
				</Typography>
			</CardContent>
			<CardActions>
				<Link
					to={`/recipe/edit/${id}/`}
					style={{ textDecoration: "none" }}>
					<Button size="small">Edit</Button>
				</Link>

				<Link
					to={`/recipe/view/${id}/`}
					style={{ textDecoration: "none" }}>
					<Button size="small">View Description</Button>
				</Link>
			</CardActions>
		</Card>
	);
}
