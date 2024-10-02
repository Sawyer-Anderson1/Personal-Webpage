const enter = document.getElementById('enter');
  document.querySelectorAll('#enter[list]').forEach( function (formfield) {
    var options = document.getElementById('options');
    var lastlength = formfield.value.length;
    var checkInputValue = function (inputValue) {
      if (inputValue.length - lastlength > 1) {
        options.querySelectorAll('option').forEach( function(item) {
          if (item.value === inputValue) {
            formfield.form.submit();
          }
        });
      }
      lastlength = inputValue.length;
    };
    formfield.addEventListener('input', function () {
      checkInputValue(this.value);
    }, false);
  });