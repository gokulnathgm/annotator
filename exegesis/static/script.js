function displayDiv(screen) {
  document.getElementById(screen).style.display = "block";
  if (screen == 'android') {
    document.getElementById('ios').style.display = "none";
    document.getElementById('web').style.display = "none";
  }
  if (screen == 'ios') {
    document.getElementById('android').style.display = "none";
    document.getElementById('web').style.display = "none";
  }
  if (screen == 'web') {
    document.getElementById('android').style.display = "none";
    document.getElementById('ios').style.display = "none";
  }
}

function update(project) {
  $('#project-uuid').val(project);
  $('#svgfile').click();
  document.getElementById('svgfile').onchange = function() {
    document.getElementById('update-project').submit();
  };
}

function search() {
  var input = document.getElementById('search');
  var filter = input.value.toUpperCase();
  var divs =document.getElementsByClassName('col-md-3');
  for (i = 0; i < divs.length; i++) {
    div = divs[i]
    if (div.id.toUpperCase().indexOf(filter) > -1) {
      div.style.display = '';
    } else {
      div.style.display = 'none';
    }
  }
}

function updateArtboard(artboard) {
  $('#artboard-uuid').val(artboard);
  $('#svgfile').click();
  document.getElementById('svgfile').onchange = function() {
    document.getElementById('update-artboard').submit();
  }
}

function sortByName(id1, id2) {
  var $divs = $('div.col-md-3');
  var alphabeticallyOrderedDivs = $divs.sort(function (a, b) {
    return $(a).find('button').text() > $(b).find('button').text();
  });
  $('#sorted-class').html(alphabeticallyOrderedDivs);
  $('#' + id1).css('font-weight','Bold');
  $('#' + id2).css('font-weight','Normal');
}

function sortByUpdate(id1, id2) {
  var $divs = $('div.col-md-3');
  var updateOrderedDivs = []
  len = $divs.length;
  for (var i=len; i>=0; i--) {
    updateOrderedDivs.push($divs[i]);
  }
  $('#sorted-class').html(updateOrderedDivs);
  $('#' + id1).css('font-weight','Bold');
  $('#' + id2).css('font-weight','Normal');
}

function changeDash(){
  $('#dash').removeClass('btn-style');
  $('#dash').addClass('btn-dash');
  $('#style').removeClass('btn-dash');
  $('#style').addClass('btn-style');
};

function changeStyle() {
  $('#style').removeClass('btn-style');
  $('#style').addClass('btn-dash');
  $('#dash').removeClass('btn-dash');
  $('#dash').addClass('btn-style');
};
