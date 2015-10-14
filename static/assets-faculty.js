function loadFaculty () {
	// body...
	var faculty_list_api = '/faculty/api'

	$.get(faculty_list_api, {}, function(response) {
    response.faculty_data.forEach(function(faculty) {
      var faculty_item = faculty.full_name;
      var id_name = faculty.id
      $('.faculty').prepend('<li>' + '<a href="' + faculty.id + '">'+ faculty_item + '</a>' + '</li>');
      //$('.faculty-list').prepend('<option value="' + faculty_item + '">' + faculty_item + '</option>');
      var select = document.getElementById('faculty-list');
        var opt = document.createElement('option'); 
            opt.value = faculty_item;
            opt.innerHTML = faculty_item;
            select.appendChild(opt);
      });
	});
}

function facultyAdd(event)
{
  var data = $(event.target).serializeArray();

  var faculty = {};
  for (var i = 0; i < data.length; i++) {
    faculty[data[i].name] = data[i].value;
  }

  var faculty_api = '/faculty/create';
  $.post(faculty_api, faculty, function(response) {
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

loadFaculty();
$('.faculty-entry').submit(facultyAdd);
