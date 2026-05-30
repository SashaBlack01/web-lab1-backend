pm.test(Login successful, function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.globals.set(auth_token, jsonData.token);
});