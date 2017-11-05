function nextLogin() {
  document.querySelector('.login_page form').classList.toggle('password');
  document.getElementById('directions').innerHTML = "Please enter your password";
}
