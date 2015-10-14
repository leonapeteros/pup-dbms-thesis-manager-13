function loadAll() {
  var thesis_list_api = '/api/thesis';
  $.get(thesis_list_api, {}, function(response) {
    response.thesis_data.forEach(function(thesis_list) {
      var thesis_item = thesis_list.year + ' ' + thesis_list.title;
      $('.thesis-list').prepend('<li><a href="/thesis/' + thesis_list.id + '">' + thesis_item + '</a></li>');
      });
    $('.filter').append('<optgroup label="Year">');
    response.thesis_data.forEach(function(thesis_list) {
      if ($('#filter option[value=' + thesis_list.year + ']').length == 0 ) {
        $('.filter').append('<option value="' + thesis_list.year + '">' + thesis_list.year + '</option>')
        }
      });
    $('.filter').append('</optgroup>');
    $('.filter').append('<optgroup label="University">');
    response.thesis_data.forEach(function(thesis_list) {
      thesis_list.department.forEach(function(d){
        if (!($('select#filter option').hasClass(d.university)) ) {
          $('.filter').append('<option class="' + d.university + '"value="' + d.university_id + '">' + d.university + '</option>')
        }
        });
      });
    $('.filter').append('</optgroup>');
    $('.filter').append('<optgroup label="Adviser">');
    response.thesis_data.forEach(function(thesis_list) {
      thesis_list.adviser.forEach(function(f){
        if (!($('select#filter option').hasClass(f.name)) ) {
          $('.filter').append('<option class="' + f.name + '" value="' + f.faculty_id + '">' + f.name + '</option>')
        }
        });
      });
    $('.filter').append('</optgroup>');
  });
}
function onReg(event)
{
  var data = $(event.target).serializeArray();

  var user = {};
  for (var i = 0; i < data.length; i++) {
    user[data[i].name] = data[i].value;
  }

  var user_api = '/register';
  $.post(user_api, user, function(response) {
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

function search(event)
{
  var data = $(event.target).serializeArray();
  var user = {};
  for (var i = 0; i < data.length; i++) {
    user[data[i].name] = data[i].value;
  }

  var user_api = '/search';
  $.post(user_api, user, function(response) {
      console.log('data', response);
      $('.search-results').empty()
      if (!response.data) {
        alert("No Search Results!");
      } else {
        $.each(response.data, function(key, value){
        $('.search-results').append('<li><i class="fui-arrow-right"></i><a href="/thesis/' + value + '">' + key + '</a></li>');
      });
      }
      
  });
  return false;
}

loadAll();
$('.regform').submit(onReg);
$('.thesis-search').submit(search);
