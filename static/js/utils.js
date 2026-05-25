// Error message extraction from API responses
export function getErrorMessage(error) {
    if (typeof error.detail === "string") {
        return error.detail;                                                                // if error detail is a string it just gets returned
    } else if (Array.isArray(error.detail)) {
        return error.detail.map((err) => err.msg).join(". ");                               // if its an array of validation errors, we extract msgs and join them
    }
    return "An error occurred. Please try again.";
}

// Show a Bootstrap modal by ID
export function showModal(modalId) {                                                        // helper func that uses bootstraps get or create instance for modal and then shows it
    const modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById(modalId),
    );
    modal.show();
    return modal;
}

// Hide a Bootstrap modal by ID
export function hideModal(modalId) {                                                        // same but for hiding, safe when modal doesnt exist
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) modal.hide();
}