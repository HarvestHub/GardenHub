var loginForm = document.querySelector('.login_page form#login');

loginForm.addEventListener("submit", function(e) {
  e.preventDefault();
  if (loginForm.classList.contains("password")) {
    loginForm.submit();
  } else {
    loginForm.classList.add("password");
    // FIXME: not sure why this isn't working. Maybe the CSS transition? Using setTimeout didn't seem to help.
    document.querySelector('#password_field input').focus();
    return false;
  }
});

document.querySelector('#email_field input').focus();
