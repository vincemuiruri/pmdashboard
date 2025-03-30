$(document).ready(function(){
    $("#login-form").submit(function(event){
        event.preventDefault(); // Prevent default form submission

        let userID = document.getElementById("userID").value.trim();
        let password = document.getElementById("password").value.trim();
        
        if (!is_verified(userID, password)) {
            alert("All fields are required");
            return; // Stop execution
        }

        const data = {
            userID: userID,
            password: password
        };

        fetch(`/auth/login`, {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Message:", data.message);
            if (data.status === 200) {
                //alert("Login successful!");
                // Redirect or perform other actions
                window.location.href = data.redirect_url;
            } else {
                //alert("Login failed: " + data.message);
                document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">${data.message}</div>`;
                showModal();

            }
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">${error}</div>`;
            showModal();
        });
    });

    function is_verified(userID, password) {
        return userID !== "" && password !== "";
    }

    $("#register-form").submit(function(event){
        event.preventDefault();

        if(is_verified_register()){
            const formData = new FormData(this);

            fetch("/auth/signup",{
                body: formData,
                method: "POST"
            }).then(response=>{
                return response.json()
            }).then(data=>{
                const status = data.status;
                const message = data.message;

                if(status == 201){
                    document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-success" roler="alert">Account created succesfully!</div>`;
                    showModal();
                }else{
                    document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">${message}</div>`;
                    showModal();
                }
                this.reset();
                // location.reload();
            }).catch(error=>{
                document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">Error: ${error}</div>`;
                showModal();
                console.error(error);
            })
        }
        function validateForm() {
            let isValid = true;
        
            // Get input values
            let project = document.getElementById("project_id").value;
            let phaseNumber = document.getElementById("phase_number").value;
            let phaseName = document.getElementById("phase_name").value;
        
            // Error message elements
            let projectError = document.getElementById("project_error");
            let phaseNumberError = document.getElementById("phase_number_error");
            let phaseNameError = document.getElementById("phase_name_error");
        
            // Reset errors
            projectError.innerText = "";
            phaseNumberError.innerText = "";
            phaseNameError.innerText = "";
        
            // Validate project selection
            if (project === "") {
              projectError.innerText = "Please select a project.";
              isValid = false;
            }
        
            // Validate phase number
            if (phaseNumber === "" || phaseNumber <= 0) {
              phaseNumberError.innerText = "Please enter a valid phase number (greater than 0).";
              isValid = false;
            }
        
            // Validate phase name
            if (phaseName.trim() === "") {
              phaseNameError.innerText = "Project phase name cannot be empty.";
              isValid = false;
            }
        
            // If form is invalid, prevent submission and hide spinner
            if (!isValid) {
              hideSpinner();
            }
        
            return isValid;
          }

    });

    function is_verified_register(){
        const userID = document.getElementById("userID").value;

        if(userID.length > 20){
            document.getElementById("general_modal_body").innerHTML = `<div class="alert alert-danger" roler="alert">Invalid user id</div>`;
            showModal();
            return false;
        }
        return true;
    }
    
});
