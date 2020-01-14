function processForm(e) {
    if (e.preventDefault) e.preventDefault();
    var auth2 = gapi.auth2.getAuthInstance();
    if (auth2.isSignedIn.get()) {
        var a = document.createElement('a');
        a.href = "#";
        a.onclick="signOut()";
        t = "Sign Out";
        a.appendChild(t);
        document.getElementsByClassName("center")[0].appendChild(a);

<a href="#" onclick="signOut()">Sign out</a>

        return true
    }

    return false;
}

function onSignIn(googleUser) { 
    var i;
    for (i = 0; i < document.getElementsByTagName('input').length; i++) {
        document.getElementsByTagName('input')[i].disabled = false;
    } 

    var profile = googleUser.getBasicProfile();

    document.getElementById('text-input').value = profile.getEmail();
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        var i;
        for (i = 0; i < document.getElementsByTagName('input').length; i++) {
            document.getElementsByTagName('input')[i].disabled = true;
        } 
    });
}