import * as React from "react";
import { useEffect } from "react";

import { useNavigate } from "react-router-dom";

import axios from "axios";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import AlertDialog from "../components/AlertDialog";
import Copyright from "../components/Copyright";
import recipeapp from "../recipeapp.png";
import SimpleBackdrop from "../components/SimpleBackdrop";

<Copyright />;

const theme = createTheme();

export default function SignIn() {
	const navigate = useNavigate();

	useEffect(() => {
		const token = localStorage.getItem("token");
		if (token) {
			navigate("/recipes/");
		}
	}, [navigate]);

	const [backdrop, setBackdrop] = React.useState(false);
	const [emailErr, setEmailErr] = React.useState();
	const [passwordErr, setPasswordErr] = React.useState();
	const [error, setError] = React.useState();

	const handleClose = () => {
		setError("");
	};

	const handleSubmit = async (event) => {
		setBackdrop(true);
		event.preventDefault();
		const data = new FormData(event.currentTarget);
		const payload = {
			email: data.get("email"),
			password: data.get("password"),
		};
		// Send a request to the backend API to get the user's token
		try {
			const config = {
				headers: {
					"Content-type": "application/json",
				},
			};
			const response = await axios.post(
				"/api/users/token/",
				payload,
				config,
			);
			const token = `Token ${response.data["token"]}`;
			localStorage.setItem("token", token);
			navigate("/recipes/");
		} catch (error) {
			setEmailErr(error.response.data["email"]);
			setPasswordErr(error.response.data["password"]);
			setError(error.response.data["non_field_errors"]);
		} finally {
			setBackdrop(false);
		}
	};

	return (
		<ThemeProvider theme={theme}>
			{error && (
				<AlertDialog
					title="Error"
					content={error}
					button1="GO BACK"
					handleClose={handleClose}
				/>
			)}
			{backdrop && <SimpleBackdrop />}
			<Grid container component="main" sx={{ height: "100vh" }}>
				<CssBaseline />
				<Grid
					item
					xs={false}
					sm={4}
					md={6}
					sx={{
						backgroundImage:
							"url(https://images.unsplash.com/photo-1555939594-58d7cb561ad1?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1887&q=80)",
						backgroundRepeat: "no-repeat",
						backgroundColor: (t) =>
							t.palette.mode === "light"
								? t.palette.grey[50]
								: t.palette.grey[900],
						backgroundSize: "cover",
						backgroundPosition: "center",
					}}
				/>
				<Grid
					item
					xs={12}
					sm={8}
					md={6}
					component={Paper}
					elevation={6}
					square>
					<Box
						sx={{
							my: 8,
							mx: 4,
							display: "flex",
							flexDirection: "column",
							alignItems: "center",
						}}>
						<img
							style={{ maxHeight: "100px" }}
							src={recipeapp}
							alt="app-logo"
						/>
						<Typography component="h1" variant="h5">
							Sign in
						</Typography>
						<Box
							component="form"
							noValidate
							onSubmit={handleSubmit}
							sx={{ mt: 1 }}>
							<TextField
								margin="normal"
								required
								fullWidth
								id="email"
								label="Email Address"
								name="email"
								autoComplete="email"
								autoFocus
								error={Boolean(emailErr)}
								helperText={emailErr}
							/>
							<TextField
								margin="normal"
								required
								fullWidth
								name="password"
								label="Password"
								type="password"
								id="password"
								autoComplete="current-password"
								error={Boolean(passwordErr)}
								helperText={passwordErr}
							/>
							<Button
								type="submit"
								fullWidth
								variant="contained"
								sx={{ mt: 3, mb: 2 }}>
								Sign In
							</Button>
							<Grid container justifyContent="center">
								<Grid item>
									<Link href="/#/signup/" variant="body2">
										{"Don't have an account? Sign Up."}
									</Link>
								</Grid>
							</Grid>
							<Copyright sx={{ mt: 5 }} />
						</Box>
					</Box>
				</Grid>
			</Grid>
		</ThemeProvider>
	);
}
