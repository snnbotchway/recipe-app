import React from "react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import axios from "axios";

import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Toolbar from "@mui/material/Toolbar";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import recipeapp from "../recipeapp.png";

const settings = ["Profile", "Logout"];

function Header() {
	const [profileImage, setProfileImage] = useState(null);
	const [token, setToken] = useState(null);
	const [anchorElUser, setAnchorElUser] = useState(null);
	const [showHeader, setShowHeader] = useState(false);
	const navigate = useNavigate();

	const handleOpenUserMenu = (event) => {
		setAnchorElUser(event.currentTarget);
	};

	const handleCloseUserMenu = (setting) => {
		setAnchorElUser(null);
		if (setting === "Logout") {
			localStorage.removeItem("token");
			navigate("/signin");
		}
		if (setting === "Profile") {
			navigate("/profile");
		}
	};

	useEffect(() => {
		setToken(localStorage.getItem("token"));
		if (token) {
			setShowHeader(true);

			axios
				.get("/api/users/me/", {
					headers: {
						Authorization: token,
					},
				})
				.then((response) => {
					const profile = response.data;
					setProfileImage(profile.image);
				})
				.catch((error) => {
					console.error(error);
				});
		} else {
			setShowHeader(false);
		}
	}, [token, navigate, profileImage]);

	return showHeader ? (
		<AppBar position="static" style={{ backgroundColor: "#252525" }}>
			<Container maxWidth="lg">
				<Toolbar disableGutters>
					<img
						sx={{
							display: ["none", "flex"],
						}}
						style={{ maxHeight: "4vh" }}
						src={recipeapp}
						alt="app-logo"
					/>
					<Typography
						variant="h6"
						noWrap
						component="a"
						href="/"
						sx={{
							m: 2,
							display: "flex",
							fontFamily: ["Open Sans", "sans-serif"],
							fontWeight: 700,
							color: "inherit",
							textDecoration: "none",
						}}>
						Recipe App
					</Typography>

					<Box sx={{ flexGrow: 0, ml: "auto" }}>
						<Tooltip title="Open settings">
							<IconButton
								onClick={handleOpenUserMenu}
								sx={{ p: 0 }}>
								<Avatar src={profileImage} alt="S" />
							</IconButton>
						</Tooltip>
						<Menu
							sx={{ mt: "45px" }}
							id="menu-appbar"
							anchorEl={anchorElUser}
							anchorOrigin={{
								vertical: "top",
								horizontal: "right",
							}}
							keepMounted
							transformOrigin={{
								vertical: "top",
								horizontal: "right",
							}}
							open={Boolean(anchorElUser)}
							onClose={handleCloseUserMenu}>
							{settings.map((setting) => (
								<MenuItem
									key={setting}
									onClick={() =>
										handleCloseUserMenu(setting)
									}>
									<Typography textAlign="center">
										{setting}
									</Typography>
								</MenuItem>
							))}
						</Menu>
					</Box>
				</Toolbar>
			</Container>
		</AppBar>
	) : null;
}
export default Header;
