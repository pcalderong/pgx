$(function() {
    $("#selectPais").change(function() {
        var paisId = $('#selectPais option:selected').val();
        $.ajax({
            url: '/getCiudad',
            type: 'GET',
            data: { pais: paisId },
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                $("#selectCiudad").empty();
                var output = "";
                $.each(response, function(a,b){
                  $('#selectCiudad').append($('<option>',
                    {
                        value: b.id,
                        text : b.nombre
                    }));
                });
            },
            error: function(error) {
                console.log(error);
            }
        });
    });


    type = ['','info','success','warning','danger'];

     $.ajax({
        url: '/getGruposMetabolicosChart',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            Chartist.Pie('#chartGM', {
              labels: [response[0]+'%',response[1]+'%',response[2]+'%'],
              series: [response[0],response[1],response[2]]
            });
        },
        error: function(error) {
            console.log(error);
        }
    });

    $("#selectTratamiento").change(function() {
        var tratamientoId = $('#selectTratamiento option:selected').val();

        $.ajax({
            url: '/getGruposMetabolicosChartByTratamiento',
            type: 'GET',
            data: {tratamientoId: tratamientoId},
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                if (response[3] > 0){
                    $('#lblTratamiento').text("Comportamiento de los "+response[3]+" pacientes encontrados");
                } else {
                    $('#lblTratamiento').text("0 pacientes encontrados");
                }
                Chartist.Pie('#chartGMtratamientos', {
                      labels: [response[0]+'%',response[1]+'%',response[2]+'%'],
                      series: [response[0],response[1],response[2]]
                    });
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#selectRangoEdades").change(function() {
        var rangoId = $('#selectRangoEdades option:selected').val();

        $.ajax({
            url: '/getGruposMetabolicosChartByEdad',
            type: 'GET',
            data: {rangoId: rangoId},
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                if (response[3] > 0){
                    $('#lblEdad').text("Comportamiento de los "+response[3]+" pacientes encontrados");
                } else {
                    $('#lblEdad').text("0 pacientes encontrados");
                }
                Chartist.Pie('#chartGMedades', {
                      labels: [response[0]+'%',response[1]+'%',response[2]+'%'],
                      series: [response[0],response[1],response[2]]
                    });
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});