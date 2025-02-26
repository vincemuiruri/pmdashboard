$(document).ready(function () {
    $("#contractors-form").submit(function (event) {
        event.preventDefault();

        // Perform form validation
        if (!isVerifiedRegister()) {
            return;
        }

        // Get form elements
        const projectId = $("#project_id").val();
        const phaseNumber = $("#phase_number").val();
        const comment = $("#comment").val();
        const imageInput = $("#image")[0].files[0];

        // Check if required fields are filled
        if (!projectId || !phaseNumber || !comment) {
            alert("All fields are required.");
            return;
        }

        // Validate image (if uploaded)
        if (imageInput) {
            const allowedExtensions = ["image/jpeg", "image/png", "image/jpg"];
            const maxSize = 5 * 1024 * 1024; // 5MB

            if (!allowedExtensions.includes(imageInput.type)) {
                alert("Invalid file format. Only JPEG, JPG, and PNG are allowed.");
                return;
            }

            if (imageInput.size > maxSize) {
                alert("Image size must not exceed 5MB.");
                return;
            }
        }

        // Prepare FormData
        const formData = new FormData();
        formData.append("project_id", projectId);
        formData.append("phase_number", phaseNumber);
        formData.append("comment", comment);

        if (imageInput) {
            formData.append("image", imageInput);
        }

        // Send data to backend
        fetch("project/details", {
            body: formData,
            method: "POST",
            headers: {
                "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() // CSRF token for security
            }
        })
        .then(response => response.json())
        .then(data => {
            const status = data.status;
            const message = data.message;

            if (status === 201) {
                alert("Project progress updated successfully!");
                window.location.reload();
            } else {
                alert(message);
            }
        })
        .catch(error => {
            alert("Something went wrong!");
            console.error(error);
        });
    });

    // Helper function to verify form before submission
    function isVerifiedRegister() {
        return true; // Modify this function to add additional checks if needed
    }
});
