$('#myModal').modal({ show: false})

var frm = $('.upload-file');
frm.submit(function (ev) {

    ev.preventDefault();

    var formData = new FormData($(this)[0]);          
    $.ajax({
        url: "/mark-my-work",
        type: 'POST',
        data: formData,
        async: false,
        cache: false,
        contentType: false,
        processData: false,
        success: function(data, status, request) {
            console.log(request);
            status = request.responseJSON['status'];
            messages = request.responseJSON['messages'];
            question_name = request.responseJSON['question_name'];
            q_id = request.responseJSON['q_id'];
            $('#modalConent').html(
                '<div><h3>Results</h3>'+ messages+'</div>'+
                '<div><h3>Overall Result</h3>'+status+'</p></div>'
                );
            $('#myModalLabel').html('<h1>'+question_name+'</h1>');
            $('#myModal').modal('show');

            if (status === 'Successful!'){
                $('#' + q_id).html('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
            }else{
                $('#' + q_id).html('<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>');
            }
        }, error: function() {
            alert('Unexpected error');
        }});
});

function changeText(idElement) {
    key = 'session_'+String(idElement)
    $('#main-div').html(pageContent[key]);
}
