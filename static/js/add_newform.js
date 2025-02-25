$(document).ready(function(){
    $("#add_new-form").submit(function(event){
        event.preventDefault();
        
    });
    $("#add_new-form").submit(function(event){
        event.preventDefault();

        if(is_verified_register()){
            const formData = new FormData(this);

            fetch("project/add",{
                body: formData,
                method: "POST"
            }).then(response=>{
                return response.json()
            }).then(data=>{
                const status = data.status;
                const message = data.message;

                if(status == 201){
                    alert("Project created succesfully!");
                }else{
                    alert(message);
                }
            }).catch(error=>{
                alert("Something went wrong!");
                console.error(error);
            })
        }


    });
});