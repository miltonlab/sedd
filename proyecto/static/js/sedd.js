
function menu_academico_ajax(){
    $('#cargando').hide();
    var ids = new Array();
    var cont = 0;
    $('select').each(function(){
	ids[cont++] = $(this).attr('id');
    });
    /* Actualizacion de los ComboBox */
    $('select').change(function(){
	var valor = $(this).val()
	var id = $(this).attr('id');
	var indice = -1;
	for (var i=0; i<ids.length; i++){
	    if (ids[i] == id){ indice = i; break; }
	}
	if (valor == ''){
	    return;
	}
	$.ajax({
	    url: "/admin/resumen/evaluaciones/",
	    method: "GET",
	    data: {id:id, valor:valor},
	    dataType: "JSON",
	    success: function (response){
		/* Limpiamos los select que deben ser cambiados */
		for (var i=0; i<ids.length; i++){
		    if ( i > indice ){
			$('#' + ids[i]).find('option').remove();
			$('#' + ids[i]).append(new Option('---------',''));
		    }
		}
		/* Actualizamos el siguiente campo que le corresponde*/
		var valores = response['valores'];
		for (var i=0; i<valores.length; i++){
		    var option = new Option(valores[i]['valor'],valores[i]['id']);
		    $('#' + response['id']).append(option);
		}
	    },
	    error: function(xhr,status,error){
		alert("error: " + status + "-" + error);
	    }
	});
    });
}