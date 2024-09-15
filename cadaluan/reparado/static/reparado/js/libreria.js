function modal(ruta) {
	$.ajax({
			method: "GET",
			url: ruta,
		})
		.done(function(respuesta) {
			$("#modal").html(respuesta);
			$('#modal').modal('show');
		})
		.fail(function() {
			console.error("La respuesta del servidor no es válida.");
			alert("Ocurrió un error al procesar la respuesta del servidor.");
		});
}

function registro(ruta) {
	$.ajax({
			method: "GET",
			url: ruta,
		})
		.done(function(respuesta) {
			$("#registrarseModal").html(respuesta);
			$("#registrarseModal").modal("show");
			$('#iniciarSesionModal').modal('hide');
		})
		.fail(function() {
			console.error("La respuesta del servidor no es válida.");
			alert("Ocurrió un error al procesar la respuesta del servidor.");
		});
}

// Funciones pertenecientes al carro

function offcanvas(ruta) {
	r = $("#offcanvasRight")

	$.ajax({
			method: "GET",
			url: ruta
		})
		.done(function(respuesta) {
			r.html(respuesta)
			quitar_alertas();
		})
		.fail(function() {
			alert("error");
		});
}

function add_carrito(ruta, id) {
	r = $("#offcanvasRight")

	id_solicitud = $("#id_solicitud_" + id).val();

	//dataType: 'json'
	$.ajax({
			method: "GET",
			url: ruta,
			data: {
				"id_solicitud": id_solicitud
			}
		})
		.done(function(respuesta) {
			r.html(respuesta);
			// abrir offcanvas
			offcanvas = $("#offcanvasRight").offcanvas('toggle');
			quitar_alertas();
		})
		.fail(function() {
			alert("error");
		});
}

function del_item_carrito(ruta) {
	r = $("#offcanvasRight")

	$.ajax({
			method: "GET",
			url: ruta
		})
		.done(function(respuesta) {
			r.html(respuesta);
			quitar_alertas();
		})
		.fail(function() {
			alert("error");
		});
}

function quitar_alertas() {
	console.log("Quitando alerta...");
	window.setTimeout(function() {
		$(".alert").fadeTo(500, 0).slideUp(500, function() {
			$(this).remove();
		});
	}, 1000);
}

// Calendario
document.addEventListener("DOMContentLoaded", function() {
    var calendarEl = document.getElementById("calendar");
    var calendar;

    if (calendarEl) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            themeSystem: 'standard',
            initialView: "dayGridMonth",
            headerToolbar: {
                left: "prev,next today",
                center: "title",
                right: "dayGridMonth,timeGridWeek,timeGridDay",
            },
            events: JSON.parse(calendarEl.dataset.solicitudes),
            dateClick: function(info) {
                var selectedDate = info.dateStr;
                alert("Fecha seleccionada: " + selectedDate);
                // Aquí puedes agregar código para mostrar detalles adicionales en un modal
            }
        });
    }

    // Event listener para mostrar el modal del calendario
    var btnShowCalendar = document.getElementById("btnShowCalendar");
    var modalCalendarElement = document.getElementById("modalCalendar");
    var modalCalendar = new bootstrap.Modal(modalCalendarElement);

    if (btnShowCalendar) {
        btnShowCalendar.addEventListener("click", function() {
            modalCalendar.show();
        });
    }

    // Ensure the calendar resizes correctly when the modal is shown
    modalCalendarElement.addEventListener('shown.bs.modal', function() {
        if (calendar) {
            calendar.render();
            calendar.updateSize();
        }
    });
});
