// var loginForm = document.querySelector('.login_page form#login');

// loginForm.addEventListener("submit", function(e) {
//   e.preventDefault();
//   if (loginForm.classList.contains("password")) {
//     loginForm.submit();
//   } else {
//     loginForm.classList.add("password");
//     // FIXME: not sure why this isn't working. Maybe the CSS transition? Using setTimeout didn't seem to help.
//     document.querySelector('#password_field input').focus();
//     return false;
//   }
// });

// document.querySelector('#email_field input').focus();

function toggleUserOptionsNav() {
  document.getElementById('user_options').classList.toggle('hidden');
  document.getElementById('manage_options').classList.add('hidden');
};

function toggleMangeOptionsNav() {
  document.getElementById('manage_options').classList.toggle('hidden');
  document.getElementById('user_options').classList.add('hidden');
};

// Select crops to harvest

function toggleCheck() {
  var checkbox = this.parentNode.querySelector(".checkbox");

  var icon = this.parentNode.querySelector(".crop_tap_box");

  if (checkbox.checked == false) {
    checkbox.checked = true;
    icon.classList.toggle('checked');
  }
  else {
    checkbox.checked = false;
    icon.classList.toggle('checked');
  }
}

function checkBoxes() {
  console.log('test');

  var boxes = document.querySelectorAll(".crop_selector");

  for (var i=0; i<boxes.length; i++) {
      var box = boxes[i];
      var icon = box.querySelector(".crop_tap_box");
      icon.addEventListener("click", toggleCheck);
  }
}

checkBoxes();
// end crop selection
