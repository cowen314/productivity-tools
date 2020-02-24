const base_api_url = "http://127.0.0.1:5001/"
const component_update_method = "update_component"

function update_component(componentId)
{
    var request = new XMLHttpRequest();
    request.onreadystatechange = function ()
    {
        if (this.readyState == 4)
        {
            if (this.status == 200)
                document.getElementById(componentId).innerHTML = this.responseText;
            else
                document.getElementById(componentId).innerHTML = "Request error";
        }
    }
    request.open("GET", base_api_url.concat('', component_update_method), true);
    request.setRequestHeader("componentId", componentId);
    request.send();
}