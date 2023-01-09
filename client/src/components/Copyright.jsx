import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";

export default function Copyright(props) {
	return (
		<Typography
			variant="body2"
			color="text.secondary"
			align="center"
			{...props}>
			{"Copyright © "}
			<Link
				color="inherit"
				href="https://github.com/snnbotchway/recipe-app-api">
				Recipe App
			</Link>{" "}
			{new Date().getFullYear()}
			{"."}
		</Typography>
	);
}
