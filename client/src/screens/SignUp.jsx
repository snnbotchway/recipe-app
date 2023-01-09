import * as React from "react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import axios from "axios";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import CssBaseline from "@mui/material/CssBaseline";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import AlertDialog from "../components/AlertDialog";
import Copyright from "../components/Copyright";
import recipeapp from "../recipeapp.png";
import SimpleBackdrop from "../components/SimpleBackdrop";

<Copyright />;

const theme = createTheme();

export default function SignUp() {
	const navigate = useNavigate();

	useEffect(() => {
		const token = localStorage.getItem("token");
		if (token) {
			navigate("/recipes/");
		}
	}, [navigate]);

	const [successDialog, setSuccessDialog] = React.useState(false);
	const [backdrop, setBackdrop] = React.useState(false);
	const [emailErr, setEmailErr] = React.useState();
	const [passwordErr, setPasswordErr] = React.useState();

	const closeSuccess = () => {
		setSuccessDialog(false);
		navigate("/signin");
	};

	const handleSubmit = async (event) => {
		setBackdrop(true);
		event.preventDefault();
		const data = new FormData(event.currentTarget);
		const payload = {
			email: data.get("email"),
			password: data.get("password"),
			first_name: data.get("firstName"),
			last_name: data.get("lastName"),
		};
		// Send a request to the backend API to create the user
		try {
			const config = {
				headers: {
					"Content-type": "application/json",
				},
			};
			await axios.post("/api/users/create/", payload, config);
			setSuccessDialog(true);
		} catch (error) {
			setEmailErr(error.response.data["email"]);
			setPasswordErr(error.response.data["password"]);
		} finally {
			setBackdrop(false);
		}
	};

	return (
		<ThemeProvider theme={theme}>
			{backdrop && <SimpleBackdrop />}
			{successDialog && (
				<AlertDialog
					title="Success"
					content="Your account was created successfully. Please sign in on the next page."
					button1="OK"
					handleClose={closeSuccess}
				/>
			)}

			<Container component="main" maxWidth="xs">
				<CssBaseline />
				<Box
					sx={{
						marginTop: 8,
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
						Sign up
					</Typography>
					<Box
						component="form"
						noValidate
						onSubmit={handleSubmit}
						sx={{ mt: 3 }}>
						<Grid container spacing={2}>
							<Grid item xs={12} sm={6}>
								<TextField
									autoComplete="given-name"
									name="firstName"
									required
									fullWidth
									id="firstName"
									label="First Name"
									autoFocus
								/>
							</Grid>
							<Grid item xs={12} sm={6}>
								<TextField
									required
									fullWidth
									id="lastName"
									label="Last Name"
									name="lastName"
									autoComplete="family-name"
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									id="email"
									label="Email Address"
									name="email"
									autoComplete="email"
									error={Boolean(emailErr)}
									helperText={emailErr}
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									name="password"
									label="Password"
									type="password"
									id="password"
									autoComplete="new-password"
									error={Boolean(passwordErr)}
									helperText={passwordErr}
								/>
							</Grid>
						</Grid>
						<Button
							type="submit"
							fullWidth
							variant="contained"
							sx={{ mt: 3, mb: 2 }}>
							Sign Up
						</Button>
						<Grid container justifyContent="center">
							<Grid item>
								<Link href="/#/signin/" variant="body2">
									Already have an account? Sign in.
								</Link>
							</Grid>
						</Grid>
					</Box>
				</Box>
				<Copyright sx={{ mt: 5 }} />
			</Container>
		</ThemeProvider>
	);
}
