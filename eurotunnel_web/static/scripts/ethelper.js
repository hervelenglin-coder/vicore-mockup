

class ETHelper
{
    //performs a POST request and calls a callback function on response
    //  Example use:
    //    request_get_json('/uri_to_call', '{ "someJson": "toSend" }', myCallback);
    //  Callback function example:
    //    function myCallback(replyJson) { alert("Got a reply containing " + replyJson); }
    static request_post_json(requestUri, requestJson, responseCallback)
    {             
        var request;
        if (window.XMLHttpRequest) request = new XMLHttpRequest(); //New browsers.
        else if (window.ActiveXObject) request = new ActiveXObject("Microsoft.XMLHTTP"); //Old IE Browsers.
        if (request != null)
        {
            request.open("POST", requestUri, false);
            request.setRequestHeader("Content-Type", "application/json");
            //request.setRequestHeader('RequestVerificationToken', afToken);
            request.onreadystatechange = function () {
                if (request.readyState == 4 && request.status == 200) {
                    responseCallback(request.responseText);
                }
            };
            request.send(requestJson);
            //alert("Sent " + requestJson + " to " + requestUri);
        }
    }
}