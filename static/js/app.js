$(document).ready(function() {
  var auth = new auth0.WebAuth({
    domain: 'arupdigital.au.auth0.com',
    clientID: 'xXpLrCXjZL4Almq312RFRVP3ElIcUOU0'
   });


    $('.btn-login').click(function(e) {
      e.preventDefault();
      auth.authorize({
        audience: 'https://' + 'arupdigital.au.auth0.com' + '/userinfo',
        scope: 'openid profile',
        responseType: 'code',
        redirectUri: 'http://127.0.0.1:5000/callback'
      });
    });
});  
