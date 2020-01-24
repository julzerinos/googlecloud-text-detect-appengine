      function processForm(e) {
    if (e.preventDefault) e.preventDefault();
    var auth2 = gapi.auth2.getAuthInstance();
    if (auth2.isSignedIn.get()) {
        
        var myForm = document.getElementById('califormication');
        var formData = new FormData(myForm);
        formData.append("gid", auth2.currentUser.get().getAuthResponse().id_token);
         
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if(xhr.readyState === XMLHttpRequest.DONE && (xhr.status === 200 || xhr.status === 302)) {
                window.location.replace(`${xhr.responseURL}`);
            }
        };
        xhr.open('POST', '/', true);
        xhr.send(formData);
    }
    return true;
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
            type: 'in',
            loggedIn: googleUser.getAuthResponse().id_token
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

    var form = document.getElementById('califormication');
    if (form.attachEvent) {
        form.attachEvent("submit", processForm);
    } else {
        form.addEventListener("submit", processForm);
}
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        var i;
        for (i = 0; i < document.getElementsByTagName('input').length; i++) {
            document.getElementsByTagName('input')[i].disabled = true;
        } 
    });

    var googleUser = auth2.currentUser.get()

    $.ajax({
        data: {
            type: 'out',
            loggedIn: googleUser.getAuthResponse().id_token
        },
        type: 'POST',
        url: '/login'
    })
    window.location.reload(false); 
}