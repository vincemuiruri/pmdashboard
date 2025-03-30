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
            document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">All fields are required.</div>`;
            showModal();
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

            if (status === 201 || status === 200) {
                document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-success" roler="alert">Project phase added successfully!</div>`;
                showModal();
                this.reset();
            } else {
                document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">${message}</div>`;
                showModal();
            }
        })
        .catch(error => {
            document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">Something went wrong: ${error}</div>`;
            showModal();
            console.error(error);
        });
    });

    // Helper function for additional validation logic if needed
    function isVerifiedRegister() {
        return true; // Modify this function if further checks are needed
    }
});
