      function onSignIn(googleUser) {
 
        var i;
        for (i = 0; i < document.getElementsByTagName('input').length; i++) {
            document.getElementsByTagName('input')[i].disabled = false;
        } 

        // Useful data for your client-side scripts:
        //var profile = googleUser.getBasicProfile();
        //console.log("ID: " + profile.getId()); // Don't send this directly to your server!
        //console.log('Full Name: ' + profile.getName());
        //console.log('Given Name: ' + profile.getGivenName());
        //console.log('Family Name: ' + profile.getFamilyName());
        //console.log("Image URL: " + profile.getImageUrl());
        //console.log("Email: " + profile.getEmail());

        // The ID token you need to pass to your backend:
        //var id_token = googleUser.getAuthResponse().id_token;
        //console.log("ID Token: " + id_token);
      }

      function onLoad() {
        if (auth2.isSignedIn.get()) {   
            var i;
            for (i = 0; i < document.getElementsByTagName('input').length; i++) {
                document.getElementsByTagName('input')[i].disabled = false;
            } 
        }}

      function signOut() {
        var auth2 = gapi.auth2.getAuthInstance();
        auth2.signOut();
        var i;
        for (i = 0; i < document.getElementsByTagName('input').length; i++) {
            document.getElementsByTagName('input')[i].disabled = true;
            } 

      }