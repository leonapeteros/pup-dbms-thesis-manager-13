function loaddepartment () {
	// body...
	var department_list_api = '/department/api'

	$.get(department_list_api, {}, function(response) {
    response.data.forEach(function(department) {
      var department_item = department.department_name;
      $('.department').prepend('<li><i class="fui-arrow-right"></i><a href="' + department.id + '">' + department_item + '</a> -- ' + department.department_college + ' / ' + department.department_university + '</li>');
      //$('.department-list').prepend('<option value="' + department_item + '">' + department_item + '</option>');
      var select = document.getElementById('department-list');
        var opt = document.createElement('option'); 
            opt.value = department_item;
            opt.innerHTML = department_item;
            select.appendChild(opt);
      });
	});

}

function departmentAdd(event)
{
  var data = $(event.target).serializeArray();

  var dept = {};
  for (var i = 0; i < data.length; i++) {
    dept[data[i].name] = data[i].value;
  }

  var dept_api = '/department/create';
  $.post(dept_api, dept, function(response) {
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

loaddepartment();
$('.department-entry').submit(departmentAdd);