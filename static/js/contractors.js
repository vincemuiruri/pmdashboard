$(document).ready(function(){
    $("#contractors-form").submit(function(event){
        event.preventDefault();
        
    });
    $("#contractors-form").submit(function(event){
        event.preventDefault();

        if(is_verified_register()){
            const formData = new FormData(this);

            fetch("project/details",{
                body: formData,
                method: "POST"
            }).then(response=>{
                return response.json()
            }).then(data=>{
                const status = data.status;
                const message = data.message;

                if(status == 201){
                    alert("Phases created succesfully!");
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