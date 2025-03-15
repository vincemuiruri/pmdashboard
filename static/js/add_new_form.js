$(document).ready(function () {
    $("#add_new-form").submit(function (event) {
        event.preventDefault();

        // Perform form validation
        if (!isVerifiedRegister()) {
            return;
        }

        // Get form values
        const projectId = $("#project_id").val();
        const phaseName = $("#phase_name").val();
        const phaseNumber = $("#phase_number").val();

        // Check if required fields are filled
        if (!projectId || !phaseName || !phaseNumber) {
            alert("All fields are required.");
            return;
        }

        // Prepare FormData
        const formData = new FormData(this);

        // Send data to backend
        fetch("/project/add", {
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
                alert("Project phase added successfully!");
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

    // Helper function for additional validation logic if needed
    function isVerifiedRegister() {
        return true; // Modify this function if further checks are needed
    }
});
