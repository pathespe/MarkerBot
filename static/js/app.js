$(document).ready(function() {
  var auth = new auth0.WebAuth({
    domain: AUTH0_DOMAIN,
    clientID: AUTH0_CLIENT_ID,
    theme: {
     logo: '/static/img/WWlogo.svg'
   },
   languageDictionary: {
     title: "python time"
   }});


    $('.b').click(function(e) {
      e.preventDefault();
      auth.authorize({
        audience: 'https://' + AUTH0_DOMAIN + '/userinfo',
        scope: 'openid profile',
        responseType: 'code',
        redirectUri: AUTH0_CALLBACK_URL
      });
    });
});  
