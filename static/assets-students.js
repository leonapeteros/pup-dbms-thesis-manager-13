function loadStudents () {
	// body...
	var Students_list_api = '/student/api'

	$.get(Students_list_api, {}, function(response) {
    response.data.forEach(function(student) {
      var Students_item = student.full_name;
      $('.students').prepend('<li><i class="fui-arrow-right"></i><a href="' + student.id + '">' + Students_item + '</a>' + '</li>');
      $('.thesis_proponents').prepend('<option value="' + Students_item + '">' + Students_item + '</option>');
      });
    $('.thesis_proponents').chosen();
	});
}

function studentAdd(event)
{
  var data = $(event.target).serializeArray();

  var student = {};
  for (var i = 0; i < data.length; i++) {
    student[data[i].name] = data[i].value;
  }

  var user_api = '/student/create';
  $.post(user_api, student, function(response) {
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

loadStudents();
$('.student-entry').submit(studentAdd);