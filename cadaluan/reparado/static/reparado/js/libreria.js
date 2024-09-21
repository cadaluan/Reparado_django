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

	id_servicio = $("#id_servicio_" + id).val();

	//dataType: 'json'
	$.ajax({
			method: "GET",
			url: ruta,
			data: {
				"id_servicio": id_servicio
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

const panels = document.querySelectorAll('.panel')

panels.forEach(panel => {
    panel.addEventListener('click', () => {
        removeActiveClasses()
        panel.classList.add('active')
    })
})

const removeActiveClasses = () => {
    panels.forEach(panel => {
        panel.classList.remove('active')
    })
}

/* split- landing page */

const left = document.querySelector('.left')
const right = document.querySelector('.right')
const container = document.querySelector('.container2')

left.addEventListener('mouseenter', () => container.classList.add('hover-left'))
left.addEventListener('mouseleave', () => container.classList.remove('hover-left'))

right.addEventListener('mouseenter', () => container.classList.add('hover-right'))
right.addEventListener('mouseleave', () => container.classList.remove('hover-right'))

/* contenido usuarios interactivo */

const jokeEl = document.getElementById('joke');
const jokeBtn = document.getElementById('jokeBtn');

jokeBtn.addEventListener('click', generateJoke);

generateJoke();

/* siguenos*/

const counters = document.querySelectorAll('.counter')

counters.forEach(counter => {
    counter.innerText = '0'

    const updateCounter = () => {
        const target = +counter.getAttribute('data-target')
        const c = +counter.innerText

        const increment = target / 200

        if (c < target) {
            counter.innerText = `${ Math.ceil(c + increment) }`
            setTimeout(updateCounter, 1)
        } else {
            counter.innerText = target
        }
    }

    updateCounter()
})

/* estilos js preguntas */

const toggles = document.querySelectorAll('.faq-toggle')

toggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
        toggle.parentNode.classList.toggle('active')
    })
})

/*====================================
			Single Portfolio Slider JS
		======================================*/ 
		$('.pf-details-slider').owlCarousel({
			items:1,
			autoplay:false,
			autoplayTimeout:5000,
			smartSpeed: 400,
			autoplayHoverPause:true,
			loop:true,
			merge:true,
			nav:true,
			dots:false,
			navText: ['<i class="icofont-rounded-left"></i>', '<i class="icofont-rounded-right"></i>'],
		});