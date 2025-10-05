// Filtros dependientes CarregaHores - Versión super simple
console.log('🚀 CARGANDO FILTROS...');

// Esperar a que todo esté listo
window.addEventListener('load', function () {
    console.log('✅ PÁGINA CARGADA - Iniciando filtros...');

    // Buscar elementos
    const clientFilter = document.querySelector('#id_client_filter');
    const projecteFilter = document.querySelector('#id_projecte_filter');
    const pressupostSelect = document.querySelector('#id_pressupost');

    console.log('🔍 ELEMENTOS:', {
        clientFilter: !!clientFilter,
        projecteFilter: !!projecteFilter,
        pressupostSelect: !!pressupostSelect
    });

    if (!clientFilter) {
        console.error('❌ NO SE ENCONTRÓ EL FILTRO DE CLIENTE');
        return;
    }

    if (!projecteFilter) {
        console.error('❌ NO SE ENCONTRÓ EL FILTRO DE PROYECTO');
        return;
    }

    console.log('✅ ELEMENTOS ENCONTRADOS - Configurando eventos...');

    // Configurar evento de cambio en cliente
    clientFilter.addEventListener('change', function () {
        const clientId = this.value;
        console.log('👥 CLIENTE SELECCIONADO:', clientId);

        if (!clientId) {
            console.log('🔄 Cliente vacío - Restaurando proyectos...');
            return;
        }

        console.log('📡 HACIENDO PETICIÓN AJAX...');

        // Hacer petición AJAX
        fetch('/carrega-hores/ajax/projectes-by-client/?client_id=' + clientId, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log('📡 RESPUESTA RECIBIDA:', response.status);
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }
                return response.json();
            })
            .then(proyectos => {
                console.log('📁 PROYECTOS RECIBIDOS:', proyectos);

                // Limpiar select de proyectos
                projecteFilter.innerHTML = '<option value="">--- Filtrar per projecte ---</option>';

                // Agregar proyectos
                proyectos.forEach(function (proyecto) {
                    const option = document.createElement('option');
                    option.value = proyecto.id;
                    option.textContent = proyecto.nom;
                    projecteFilter.appendChild(option);
                    console.log('➕ PROYECTO AGREGADO:', proyecto.nom);
                });

                console.log('✅ PROYECTOS ACTUALIZADOS');
            })
            .catch(error => {
                console.error('❌ ERROR EN AJAX:', error);
            });
    });

    console.log('🎉 FILTROS CONFIGURADOS CORRECTAMENTE');
});

console.log('📱 SCRIPT CARGADO - Esperando página...');