(function() {
    // Load the script
    var script = document.createElement("SCRIPT");
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js';
    script.type = 'text/javascript';
    document.getElementsByTagName("head")[0].appendChild(script);

    // Poll for jQuery to come into existance
    var checkReady = function(callback) {
        if (window.jQuery) {
            callback(jQuery);
        }
        else {
            window.setTimeout(function() { checkReady(callback); }, 100);
        }
    };

    // Start polling...
    checkReady(function($) {
        // Use $ here...
    });


$(window).click(function(e) {
    var x = e.clientX, y = e.clientY,
        elementMouseIsOver = document.elementFromPoint(x, y);
    
    // console.log(elementMouseIsOver);
    var temp = elementMouseIsOver;
    rootString = '';
    while(true) {

        var elementString = temp.tagName.toLowerCase();
        if (elementString!='html' && elementString!='body')
            if(temp['id'])
                elementString=elementString+'#'+temp['id'];
            else
                for(var i=0;i<temp.classList.length;i++)
                    elementString=elementString+'.'+temp.classList[i];

        // console.log(elementString)
        rootString=elementString+' > '+rootString;

        temp = temp.parentElement;

        if(!temp)
            break;        

    }
    rootString = rootString.substring(0,rootString.length-3);
    send_request = confirm(rootString);
    if (send_request) {
        $.ajax({
            type: 'POST',
            url: 'http://127.0.0.1:5000/add',
            data: { 
                'url': window.location.href, 
                'data': rootString
            },
            success: function(msg){
                alert('Phantom will alert you when the webpage changes');
            }
        });
    }
});


})();
