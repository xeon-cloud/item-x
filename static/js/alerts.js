let $ = document;

const toastDetails = {
	timer: 5000,
	success: {
		icon: "fa-circle-check"
	},
	error: {
		icon: "fa-circle-xmark"
	},
	warning: {
		icon: "fa-circle-exclamation"
	},
	info: {
		icon: "fa-circle-info"
	}
}

const removeToast = (toast) => {
	toast.classList.add("hide")
	if (toast.timeoutId) clearTimeout(toast.timeoutId); // Clearing the timeout for the toast
	setTimeout(() => toast.remove(), 500) // Removing the toast after 500ms
}

const createToast = (id, text) => {
  const notifications = $.querySelector(".notifications");
	// Getting the icon and text for the toast based on the id passed
	const icon = toastDetails[id]['icon'];
	const toast = $.createElement("li"); // Creating a new 'li' element for the toast
	toast.className = `toast ${id}` // Setting the classes for the toast
	// Setting the inner HTML for the toast
	toast.innerHTML = `<div class="column">
						<i class="fa-solid ${icon}"></i>
						<span>${text}</span>
				</div>
				<i class="fa-solid fa-xmark" onclick="removeToast(this.parentElement)"></i>`
	notifications.appendChild(toast); // Append the toast to the notification ul
	// Setting a timeout to remove the toast after the specified duration
	toast.timeoutId = setTimeout(() => removeToast(toast), toastDetails.timer)
}