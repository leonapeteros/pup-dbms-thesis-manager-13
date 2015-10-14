function loadcollege () {
	// body...
	var college_list_api = '/college/api'

	$.get(college_list_api, {}, function(response) {
    response.data.forEach(function(college) {
      var college_item = college.college_name;
      $('.college').append('<li><i class="fui-arrow-right"></i>' +  '<a href="'+ college.id + '">' + college_item + '</a> -- ' + college.college_university + '</li>');
      //$('.college-list').prepend('<option value="' + college_item + '">' + college_item + '</option>');
      var select = document.getElementById('college-list');
        var opt = document.createElement('option'); 
            opt.value = college_item;
            opt.innerHTML = college_item;
            select.appendChild(opt);
      });
    $('.college_department').chosen();
	});
}

function collegeAdd(event)
{
  var data = $(event.target).serializeArray();

  var college = {};
  for (var i = 0; i < data.length; i++) {
    college[data[i].name] = data[i].value;
  }

  var college_api = '/college/create';
  $.post(college_api, college, function(response) {
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

loadcollege();
$('.college-entry').submit(collegeAdd);
