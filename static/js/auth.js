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
                alert("Login successful!");
                // Redirect or perform other actions
                window.location.href = "/dashboard";
            } else {
                alert("Login failed: " + data.message);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Something went wrong. Please try again.");
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
                    alert("Account created succesfully!");
                }else{
                    alert(message);
                }
            }).catch(error=>{
                alert("Something went wrong!");
                console.error(error);
            })
        }


    });

    function is_verified_register(){
        const userID = document.getElementById("userID").value;

        if(userID.length > 20){
            alert("Invalid userID");
            return false;
        }
        return true;
    }
});
