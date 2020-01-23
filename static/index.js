function processForm(e) {
    if (e.preventDefault) e.preventDefault();
    var auth2 = gapi.auth2.getAuthInstance();
    if (auth2.isSignedIn.get()) {
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

    $.ajax({
        data: {
            loggedIn: profile.getEmail()
        },
        type: 'POST',
        url: '/login'
    })

    var a = document.createElement('a');
    a.href = "#";
    a.onclick = function () { signOut(); };
    t = document.createTextNode("Sign Out");
    a.appendChild(t);
    document.getElementsByClassName("bgimg")[0].appendChild(a);
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        var i;
        for (i = 0; i < document.getElementsByTagName('input').length; i++) {
            document.getElementsByTagName('input')[i].disabled = true;
        } 
    });
    window.location.reload(false); 
}