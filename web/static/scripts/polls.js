$(function () {
  $('.poll_units').on('change', function () {
    $('div.polls div').remove();
    const option = $(this).find('option:selected');
    const id = option.attr('id');
    $.get('http://localhost:5000/parties', function (response) {
      parties = response;
      $.get(`http://localhost:5000/results/pu/${id}`, function (response) {
        const name = Object.keys(response)[0];
        const div = $('<div>').append($('<h3>').text(`Showing results for ${name} polling unit`));
        if (Object.keys(response[name]).length !== 0) {
          const table = $('<table>');
          let tr = $('<tr>');
          tr.append($('<th>').text('Party name')).append($('<th>').text('Vote count'));
          table.append(tr);

	  const results = response[name];
          for (const party of parties) {
            tr = $('<tr>');
	    tr.append($('<td>').text(party));
	    if (results[party]) {
	      tr.append($('<td>').text(results[party]));
	    } else {
	      tr.append($('<td>').text('Nil'));
	    }
	    table.append(tr);
            div.append(table);
	    $('div.polls').append(div);
          }
        } else {
          $('div.polls').append($('<div>').append($('<p>').text('No result found')));
        }
      });
    });
  });

  $('.lga_units').on('change', function () {
    $('div.lgas div').remove();
    const option = $(this).find('option:selected');
    const id = option.attr('id');
    $.get('http://localhost:5000/parties', function (response) {
      parties = response;
      $.get(`http://localhost:5000/results/lga/${id}`, function (response) {
        const name = option.val();
        const div = $('<div>').append($('<h3>').text(`Showing results for ${name} LGA`));
        if (Object.keys(response.total).length !== 0) {
          const table = $('<table>');
          let tr = $('<tr>');
          tr.append($('<th>').text('Polling unit'));

	  for (const party of parties) {
            tr.append($('<th>').text(party));
	  }
          table.append(tr);
	
          for (const unit of Object.keys(response)) {
            if (unit === 'total') continue;
            tr = $('<tr>').append($('<td>').text(unit));
            results = response[unit];
	    for (const party of parties) {
	      if (results[party]) {
	        tr.append($('<td>').text(results[party]));
	      } else {
	        tr.append($('<td>').text('Nil'));
	      }
	    }
	    table.append(tr);
          }
          tr = $('<tr>').addClass('total').append($('<td>').text('Total'));
          results = response['total'];
	  for (const party of parties) {
	    if (results[party]) {
	      tr.append($('<td>').text(results[party]));
	    } else {
	      tr.append($('<td>').text('Nil'));
	    }
	  }
	  table.append(tr);
          div.append(table);
	  $('div.lgas').append(div);
        } else {
          $('div.lgas').append($('<div>').append($('<p>').text('No result found')));
        }
      });
    });
  });

  $('form').on('submit', function (e) {
    const data_obj = {
      username: $('input#name').val(),
      pu_id: $('input#unit_id').val()
    };

    $('input[type="number"]').each(function (i, input) {
      const inp = $(input);
      if (inp.attr('id') !== 'unit_id') {
	if (inp.val()) data_obj[inp.attr('id')] = Number(inp.val());
      }
    });

    $.ajax({
      url: 'http://localhost:5000/results/pu',
      type: 'POST',
      data: JSON.stringify(data_obj),
      contentType: 'application/json',
      success: function (response) {
        if (response.success) {
	  $('form h3').text("Uploaded successfully");
	}
      }
    });
    $(this).find('input').val('');
    e.preventDefault();
  });
});      
