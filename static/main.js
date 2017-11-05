function nextLogin() {
  document.getElementById('next').classList.toggle('hide');
  document.getElementById('login').classList.toggle('hide');
  document.getElementById('email_field').classList.toggle('hide');
  document.getElementById('password_field').classList.toggle('hide');
  document.getElementById('directions').innerHTML = "Please enter your password";
}
