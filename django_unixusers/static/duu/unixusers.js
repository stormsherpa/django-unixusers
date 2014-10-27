
function request_email_validation(){
    $.ajax({
            url: '/accounts/validate_email/',
            method: 'GET',
            dataType: 'json',
            success: function(data, textStatus, jqXHR){
                alert(data.result);
            },
            error: function(jqXHR, textStatus, errorThrown){

            }
        }

    );
}