function loaduniversity () {
    // body...
    var university_list_api = '/university/api'

    $.get(university_list_api, {}, function(response) {
    response.data.forEach(function(university) {
      var university_item = university.university_name;
      $('.university').prepend('<li><i class="fui-arrow-right"></i>' + '<a href="' + university.id + '">' + university_item + '</a>' + '</li>');
      //$('.form-control.select.select-primary.select-lg.university_list').append('<option value="' + university_item + '">' + university_item + '</option>');

      var select = document.getElementById('university_list');
        var opt = document.createElement('option'); 
            opt.value = university.university_name;
            opt.innerHTML = university.university_name;
            select.appendChild(opt);
      });
    //$('.university-list').chosen();
    });
}

function universityAdd(event)
{
  var data = $(event.target).serializeArray();

  var university = {};
  for (var i = 0; i < data.length; i++) {
    university[data[i].name] = data[i].value;
  }

  var user_api = '/university/create';
  $.post(user_api, university, function(response) {
    console.log('data', response)
    if (response.status = 'OK') {
       alert('Registration success');
       window.location.replace("/");
     } else {
       alert('Something went wrong');
     }
  });
  return false;
}

loaduniversity();
$('.university-entry').submit(universityAdd);
