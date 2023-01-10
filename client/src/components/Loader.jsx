import React from "react";
import { motion } from "framer-motion";

const loadingContainer = {
	width: "16rem",
	height: "16rem",
	display: "flex",
	justifyContent: "space-around",
};
const loadingCircle = {
	display: "block",
	width: "3rem",
	height: "3rem",
	backgroundColor: "white",
	borderRadius: "2rem",
};

const loadingContainerVariants = {
	start: {
		transition: {
			staggerChildren: 0.2,
		},
	},
	end: {
		transition: {
			staggerChildren: 0.2,
		},
	},
};

const loadingCircleVariants = {
	start: {
		y: "0%",
	},
	end: {
		y: "60%",
	},
};
const loadingCircleTransition = {
	duration: 0.4,
	yoyo: Infinity,
	ease: "easeInOut",
};

const Loader = () => {
	return (
		<div>
			<motion.div
				style={loadingContainer}
				variants={loadingContainerVariants}
				initial="start"
				animate="end">
				<motion.span
					style={loadingCircle}
					variants={loadingCircleVariants}
					transition={loadingCircleTransition}></motion.span>
				<motion.span
					style={loadingCircle}
					variants={loadingCircleVariants}
					transition={loadingCircleTransition}></motion.span>
				<motion.span
					style={loadingCircle}
					variants={loadingCircleVariants}
					transition={loadingCircleTransition}></motion.span>
			</motion.div>
		</div>
	);
};

export default Loader;
