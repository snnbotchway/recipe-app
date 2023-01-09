import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

export default function AlertDialog({
	title,
	content,
	button1,
	button2 = "",
	handleClose,
}) {
	return (
		<div>
			<Dialog
				open={true}
				onClose={handleClose}
				aria-labelledby="alert-dialog-title"
				aria-describedby="alert-dialog-description">
				<DialogTitle id="alert-dialog-title">{title}</DialogTitle>
				<DialogContent>
					<DialogContentText id="alert-dialog-description">
						{content}
					</DialogContentText>
				</DialogContent>
				<DialogActions>
					{button2 && (
						<Button onClick={handleClose}>{button2}</Button>
					)}
					<Button onClick={handleClose} autoFocus>
						{button1}
					</Button>
				</DialogActions>
			</Dialog>
		</div>
	);
}
