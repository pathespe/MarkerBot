$('#myModal').modal({ show: false});

var frm = $('.upload-file');

frm.submit(function (ev) {
    $('#progress').empty();
    ev.preventDefault();
    div = $('<div class="progress"><div></div><div>0%</div><div><br>djkfbsdkjfb</br></div><div>lets do this</div></div><hr>');
    $('#progress').append(div);
    // create a progress bar
    var nanobar = new Nanobar({
        // bg: '#44f',
        target: div[0].childNodes[0]
    });


    var formData = new FormData($(this)[0]);          
    $.ajax({
        url: "/api/mark-my-work",
        type: 'POST',
        data: formData,
        async: false,
        cache: false,
        contentType: false,
        processData: false,
        success: function(data, status, request) {
            status_url = request.responseJSON['Location']
            update_progress(status_url, nanobar, div[0]);
        }, error: function() {
            alert('oh shii unexpected error');
        }});
});


function unpack_result(results){
    var output = `<table class="table table-hover">
                    <thead>
                    <tr>
                        <th>Input</th>
                        <th>Output</th>
                        <th>Result</th>
                    </tr>
                    </thead>
                    <tbody>`;

    for (var i= 0; i < results.length; i++){
        output += '<tr><td>' + results[i]['input'] + 
                   '</td><td> ' + results[i]['output'] + 
                   '<td> ' + results[i]['result'] + '<td/></tr>'
    }

    return output + '</tbody></table>';
}


function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text('hang on m8');

        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                $(status_div.childNodes[3]).text('Result: ' + data['result']);

                status = data['status'];
                messages = unpack_result(data['result']);


                question_name = data['question_name'];
                q_id =data['q_id'];
                console.log(data);
                // console.log(data['result']);
                /// show results in a modal
                $('#modalConent').html(
                    '<div><h3>Results</h3>'+ messages+'</div>'+
                    '<div><h3>Overall Result</h3>'+status+'</p></div>'
                    );
                $('#myModalLabel').html('<h1>'+question_name+'</h1>');
                $('#myModal').modal('show');

                // create a tick beside question if the attempt is sucessful
                if (status === 'Successful!'){
                    $('#' + q_id).html('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
                }else{
                    $('#' + q_id).html('<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>');
                }
                
                $(status_div.childNodes[1]).text('100%');
                $(status_div.childNodes[2]).text('marking complete');
                nanobar.go(100);
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[2]).text('oooft thats not good');
                // $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            console.log('run again');
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 2000);
        }
    });
}

////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////


function changeText(idElement) {
    key = 'session_'+String(idElement)
    $('#main-div').html(pageContent[key]);
}

function changeText(idElement) {
    key = 'session_'+String(idElement)
    $('#main-div').html(pageContent[key]);
    Prism.highlightAll();
    $('#cheat-div').hide();
}

$("#button").click(function() {
    $('#main-div').html(cheat['cheat']);
    Prism.highlightAll();
});

$("#prebutton").click(function() {
    $('#main-div').html(preWork['pre_work']);
    Prism.highlightAll();
});