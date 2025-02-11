document.addEventListener("DOMContentLoaded", function(){
    const update_space = document.getElementById('sidebar-updates');

    if (!update_space){
        console.log("sidebar not found.");
        return;
    }
    
    const eventsource = new EventSource(event_url);

    eventsource.onmessage = function(event){
        console.log("Message: ", event.data);
        const new_update = document.createElement("p");
        new_update.textContent = event.data;
        update_space.prepend(new_update)
    }
})
