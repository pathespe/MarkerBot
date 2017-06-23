
// hide div with progress bar on page load
$("#marking").hide();


// progressbar.js@1.0.0 version is used
// Docs: http://progressbarjs.readthedocs.org/en/1.0.0/
var bar = new ProgressBar.Circle(container, {
  color: '#aaa',
  // This has to be the same size as the maximum width to
  // prevent clipping
  strokeWidth: 4,
  trailWidth: 1,
  easing: 'easeInOut',
  duration: 500,
  text: {
    autoStyleContainer: false,
    style: {
            // Text color.
            // Default: same as stroke color (options.color)
            position: 'absolute',
            left: '50%',
            top: '40%',
            padding: 0,
            margin: 0,
            // You can specify styles which will be browser prefixed
            transform: {
                prefix: true,
                value: 'translate(-50%, -50%)'
            }
            },
    },
  from: { color: '#aaa', width: 1 },
  to: { color: '#333', width: 4 },
  // Set default step function for all animate calls
  step: function(state, circle) {
    circle.path.setAttribute('stroke', state.color);
    circle.path.setAttribute('stroke-width', state.width);

    var value = Math.round(circle.value() * 100);
    if (value === 0) {
      circle.setText('');
    } else {
      circle.setText(value);
    }

  }
});
bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
bar.text.style.fontSize = '2rem';

$('#myModal').modal({ show: false});

var frm = $('.upload-file');

frm.submit(function (ev) {
    $("#marking").show();
    ev.preventDefault();

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
            status_url = request.responseJSON['Location'];
            bar.animate(0.01);
            update_progress(status_url);
        }, error: function() {
            alert(`oh no! Something went wrong with you submission,
                  please check you have named you file and function
                  correctly and try again`);
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

function unpack_user_progress(user_progress){
    var output = `<table class="table table-hover">
                    <thead>
                    <tr>
                        <th>Question</th>
                        <th>Attempts</th>
                        <th>Complete</th>
                    </tr>
                    </thead>
                    <tbody>`;
    for (var i= 0; i < user_progress.length; i++){
        output += '<tr><td>' + user_progress[i]['q_name'] + 
                   '</td><td> ' + user_progress[i]['attempts'] + 
                   '<td> ' + user_progress[i]['correct'] + '<td/></tr>'
    }
    return output + '</tbody></table>';
}


function update_progress(status_url) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI

        percent = parseInt(data['current'] * 100 / data['total']);

        $('#messages').empty();
        $('#messages').html('<h3>hang on m8!</h3>');
        bar.animate(percent/100);

        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                status = data['status'];
                messages = unpack_result(data['result']);
                question_name = data['question_name'];
                q_id =data['q_id'];
                console.log(data);
                /// show results in a modal
                $('#modalConent').html(
                    '<div><h3>Results</h3>' + messages + '</div>' +
                    '<div><h3>Overall Result</h3>'+ status +'</p></div>'
                    );
                bar.animate(1);
                $('#myModalLabel').html('<h1>'+question_name+'</h1>');
                $('#myModal').modal('show');

                // create a tick beside question if the attempt is sucessful
                if (status === 'Successful!'){
                    $('#' + q_id).html('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
                }else{
                    $('#' + q_id).html('<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>');
                }
                $('#messages').html('<h3>marking complete, prego!</h3>');

            }
            else {
                // something unexpected happened
                $('#messages').html('<h3>oooft thats not good</h3>');
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url);
            }, 2000);
        }
    });
}

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

//// main div event handlers

$("#button").click(function() {
    $('#main-div').html(cheat['cheat']);
    Prism.highlightAll();
});

$("#prebutton").click(function() {
    $('#main-div').html(preWork['pre_work']);
    Prism.highlightAll();
});

// modal event handlers

$("#your_progress").click(function() {
    $.ajax({

        url: "/api/user-progress/" + user_id + "/",
        type: 'GET',
        async: false,
        cache: false,
        contentType: false,
        processData: false,
        success: function(request) {
            status_url = request
            console.log(request);
            $('#modalConent').html(unpack_user_progress(status_url));
            $('#myModalLabel').html('<h1>Your Progress</h1>');
            $('#myModal').modal('show');
        }, error: function() {
            alert("oh shii");
        }});
});

$("#about").click(function() {
    $('#modalConent').html(`
    <h3>muchos gracias todos python maestros y amigos!</h3>
    <p>In random.shuffle() order</p>
    <ul>
        <li>Tom Valorsa</li>
        <li>Ian MacKenzie</li>
        <li>Ben Harrison</li>
        <li>Sam Diamond</li>
        <li>Kim Sherwin</li>
        <li>Selma Parris</li>
        <li>Penny Maber</li>
        <li>Alex Smith</li>
        <li>Oliver Lock</li>
        <li>Ben Branson</li>
        <li>Patrick Hespe</li>
        <li>Tom Gasson</li>
    </ul>
    
    <p><b>Lunchtime Markerbot</b> (this site) built with love, plenty of face palms and late nights by Patrick Hespe</p>
    <b>Big thanks to Arup Digital & Arup Uni for supporting this course</b>
    `);
    $('#myModalLabel').html('<h1>About Lunchtime Programming</h1>');
    $('#myModal').modal('show');
});

$("#leaderbutton").click(function() {
    $.ajax({
            url: "/api/rankings",
            type: 'GET',
            async: false,
            cache: false,
            contentType: false,
            processData: false,
            success: function(request) {
                status_url = request
                console.log(request);
                $('#modalConent').html(request);
                $('#myModalLabel').html('<h1>Leader Board</h1>');
                $('#myModal').modal('show');
        }, error: function() {
            alert("oh shii");
        }});
});

$('.upload-file');

   
