// hide div with progress bar on page load
$(document).ready(function() {
    $("#marking").hide();
    $('#myModal').modal({ show: false});

});
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
            alert("oh no! Something went wrong with you submission, please check you have named you file and function correctly and try again");
        }});
});

function unpack_result(results){
    var output = '<div class="table-responsive"><table class="table table-hover"><thead><tr>th>Input</th><th>Output</th><th>Expected</th><th>Result</th></tr></thead><tbody>';
    for (var i= 0; i < results.length; i++){
        output += '<tr><td>' + results[i]['input'] + 
                   '</td><td> ' + JSON.stringify(results[i]['output']) +
                   '</td><td> ' + JSON.stringify(results[i]['expected']) +   
                   '<td> ' + results[i]['result'] + '<td/></tr>'
    }
    return output + '</tbody></table></div';
}

function unpack_user_progress(user_progress){
    var output = '<table class="table table-hover"><thead><tr><th>Question</th><th>Attempts</th><th>Complete</th></tr></thead><tbody>';
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

function panel_ticks(){

 $.ajax({
        url: "/api/user-progress/" + user_id + "/",
        type: 'GET',
        async: false,
        cache: false,
        contentType: false,
        processData: false,
        success: function(user_progress) {
            for (var i= 0; i < user_progress.length; i++){
                var q_id = user_progress[i]['q_id'];
                if(user_progress[i]['correct']){
                    $('#' + q_id).html('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
                }else{
                    $('#' + q_id).html('<span class="glyphicon glyphicon-minus" aria-hidden="true"></span>');
                }
            }
        }, error: function() {
            alert("oh shii");
        }});
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
            alert("Ah something bad happened, please report issue with events leading up to it at https://github.com/pathespe/MarkerBot/issues");
        }});
});

$("#about").click(function() {
    $('#modalConent').html("<p>The lunchtime programming courses were started in 2016 in the Arup Sydney office by Alex Smith and Patrick Hespe.</p></br><p>The course aim isn't to turn everyone into software engineers, but to upskill Arup employees so they can work smarter not harder.Our view is that computers are good at repetitive tasks so why not let them to the mundane, while you focus on overarching task at hand.</p><br/><p> We hope you end up loving writing programs to remove tedious tasks from your day to day too.</p><hr/><h3>Acknowledgements</h3><p><b>Big &#10084; to Arup Digital & Arup Uni for supporting this course</b>and a special mention to the tutors, content writers and friends of the coursewithout whom it wouldn't have been possible. So muchos gracias to the following in <code>random.shuffle()</code> order:</p><ul><li>Tom Valorsa</li><li>Sam Diamond</li><li>Ian MacKenzie</li><li>Ben Harrison</li><li>Ben Brannon</li><li>Kim Sherwin</li><li>Selma Parris</li><li>Penny Maber</li><li>Oliver Lock</li><li>Tom Gasson</li></ul><hr/><p>This <b>Lunchtime Markerbot</b> aka this site built with coffee, late nights and love by Patrick Hespe</p>");
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
                $('#modalConent').html(unpack_ranking(request));
                $('#myModalLabel').html('<h1>Leader Board</h1>');
                $('#myModal').modal('show');
        }, error: function() {
            alert("oh shii");
        }});
});

function unpack_ranking(p){
    var rank = 0;
    var output = "<table class='table table-hover'><thead><tr><th>Rank</th><th>User</th><th>Questions Complete</th></tr></thead><tbody>";

    var prev_count = -999;
    for (var i= 0; i < p.length; i++){
        if (p[i][1]['count'] != prev_count){
            rank = i +1;
            prev_count = p[i][1]['count'];
        }

        output += '<tr><td>' + rank + 
                   '</td><td>' + p[i][1]['user'] + 
                   '</td><td> ' + p[i][1]['count'] + '</tr>'
    }

    return output + "</tbody></table><p>* Reverse Aplhabetical in case of a tie</p><p>** Number of attempts not considered</p>";
}

$( document ).ready(function() {
    panel_ticks();
});
