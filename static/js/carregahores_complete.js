// Filtros dependientes CarregaHores - Versión completa
console.log('🚀 CARGANDO FILTROS COMPLETOS...');

// Esperar a que todo esté listo
window.addEventListener('load', function () {
    console.log('✅ PÁGINA CARGADA - Iniciando filtros completos...');

    // Buscar elementos
    const clientFilter = document.querySelector('#id_client_filter');
    const projecteFilter = document.querySelector('#id_projecte_filter');
    const pressupostSelect = document.querySelector('#id_pressupost');
    const liniaSelect = document.querySelector('#id_linia');

    console.log('🔍 ELEMENTOS:', {
        clientFilter: !!clientFilter,
        projecteFilter: !!projecteFilter,
        pressupostSelect: !!pressupostSelect,
        liniaSelect: !!liniaSelect
    });

    if (!clientFilter || !projecteFilter || !pressupostSelect || !liniaSelect) {
        console.error('❌ FALTAN ELEMENTOS NECESARIOS');
        return;
    }

    console.log('✅ TODOS LOS ELEMENTOS ENCONTRADOS - Configurando eventos...');

    // FILTRO 1: Cliente → Proyectos y Presupuestos
    clientFilter.addEventListener('change', function () {
        const clientId = this.value;
        console.log('👥 CLIENTE SELECCIONADO:', clientId);

        // Resetear filtros dependientes
        projecteFilter.value = '';
        pressupostSelect.value = '';
        liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';

        if (!clientId) {
            console.log('🔄 Cliente vacío - Restaurando todo...');
            return;
        }

        // Filtrar proyectos por cliente
        console.log('📡 FILTRANDO PROYECTOS POR CLIENTE...');
        fetch('/carrega-hores/ajax/projectes-by-client/?client_id=' + clientId, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log('📡 RESPUESTA PROYECTOS:', response.status);
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(proyectos => {
                console.log('📁 PROYECTOS RECIBIDOS:', proyectos);

                // Actualizar select de proyectos
                projecteFilter.innerHTML = '<option value="">--- Filtrar per projecte ---</option>';
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
                console.error('❌ ERROR FILTRANDO PROYECTOS:', error);
            });

        // Filtrar presupuestos por cliente
        console.log('📡 FILTRANDO PRESUPUESTOS POR CLIENTE...');
        fetch('/carrega-hores/ajax/pressupostos-by-filters/?client_id=' + clientId, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log('📡 RESPUESTA PRESUPUESTOS:', response.status, response.statusText);
                console.log('📡 HEADERS RESPUESTA:', response.headers);
                if (!response.ok) {
                    console.error('❌ ERROR HTTP:', response.status, response.statusText);
                    throw new Error('HTTP ' + response.status + ' - ' + response.statusText);
                }
                return response.json();
            })
            .then(presupuestos => {
                console.log('📋 PRESUPUESTOS RECIBIDOS:', presupuestos);
                console.log('📋 TIPO DE RESPUESTA:', typeof presupuestos);
                console.log('📋 LONGITUD ARRAY:', Array.isArray(presupuestos) ? presupuestos.length : 'No es array');

                // Actualizar select de presupuestos
                pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';
                presupuestos.forEach(function (presupuesto) {
                    const option = document.createElement('option');
                    option.value = presupuesto.id;
                    option.textContent = presupuesto.nom + ' (' + presupuesto.client_nom + ' - ' + presupuesto.projecte_nom + ')';
                    pressupostSelect.appendChild(option);
                    console.log('➕ PRESUPUESTO AGREGADO:', presupuesto.nom);
                });

                console.log('✅ PRESUPUESTOS ACTUALIZADOS POR CLIENTE');
            })
            .catch(error => {
                console.error('❌ ERROR FILTRANDO PRESUPUESTOS:', error);
            });
    });

    // FILTRO 2: Proyecto → Presupuestos
    projecteFilter.addEventListener('change', function () {
        const projecteId = this.value;
        const clientId = clientFilter.value;
        console.log('📁 PROYECTO SELECCIONADO:', projecteId, 'Cliente actual:', clientId);

        // Resetear filtros dependientes
        pressupostSelect.value = '';
        liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';

        if (!projecteId) {
            // Si no hay proyecto seleccionado, mostrar presupuestos por cliente (si hay)
            if (clientId) {
                console.log('🔄 Sin proyecto - Mostrando presupuestos por cliente...');
                // Aquí podrías volver a cargar presupuestos solo por cliente
                return;
            }
            console.log('🔄 Sin proyecto ni cliente - Restaurando...');
            return;
        }

        // Filtrar presupuestos por cliente + proyecto
        console.log('📡 FILTRANDO PRESUPUESTOS POR PROYECTO...');
        let url = '/carrega-hores/ajax/pressupostos-by-filters/?';
        if (clientId) url += 'client_id=' + clientId + '&';
        url += 'projecte_id=' + projecteId;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log('📡 RESPUESTA PRESUPUESTOS POR PROYECTO:', response.status);
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(presupuestos => {
                console.log('📋 PRESUPUESTOS FILTRADOS POR PROYECTO:', presupuestos);

                // Actualizar select de presupuestos
                pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';
                presupuestos.forEach(function (presupuesto) {
                    const option = document.createElement('option');
                    option.value = presupuesto.id;
                    option.textContent = presupuesto.nom + ' (' + presupuesto.client_nom + ' - ' + presupuesto.projecte_nom + ')';
                    pressupostSelect.appendChild(option);
                    console.log('➕ PRESUPUESTO AGREGADO:', presupuesto.nom);
                });

                console.log('✅ PRESUPUESTOS ACTUALIZADOS POR PROYECTO');
            })
            .catch(error => {
                console.error('❌ ERROR FILTRANDO PRESUPUESTOS POR PROYECTO:', error);
            });
    });

    // FILTRO 3: Presupuesto → Líneas
    pressupostSelect.addEventListener('change', function () {
        const pressupostId = this.value;
        console.log('📋 PRESUPUESTO SELECCIONADO:', pressupostId);

        // Resetear líneas
        liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';

        if (!pressupostId) {
            console.log('🔄 Sin presupuesto - No cargar líneas');
            return;
        }

        // Cargar líneas del presupuesto
        console.log('📡 CARGANDO LÍNEAS DEL PRESUPUESTO...');
        liniaSelect.innerHTML = '<option value="">🔄 Carregant línies...</option>';
        liniaSelect.disabled = true;

        fetch('/carrega-hores/ajax/lineas/?pressupost=' + pressupostId, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log('📡 RESPUESTA LÍNEAS:', response.status);
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(data => {
                console.log('📝 LÍNEAS RECIBIDAS:', data);

                // Actualizar select de líneas
                liniaSelect.innerHTML = '<option value="">--- Selecciona una línia ---</option>';

                if (data.lineas && data.lineas.length > 0) {
                    data.lineas.forEach(function (linea) {
                        const option = document.createElement('option');
                        option.value = linea.id;
                        option.textContent = linea.treball + ' - ' + linea.tasca + ' (' + (linea.recurs || 'Sense recurs') + ')';
                        liniaSelect.appendChild(option);
                        console.log('➕ LÍNEA AGREGADA:', linea.treball, '-', linea.tasca);
                    });
                    liniaSelect.disabled = false;
                    console.log('✅ LÍNEAS CARGADAS CORRECTAMENTE');
                } else {
                    liniaSelect.innerHTML = '<option value="">No hi ha línies disponibles</option>';
                    liniaSelect.disabled = true;
                    console.log('⚠️ No hay líneas disponibles');
                }
            })
            .catch(error => {
                console.error('❌ ERROR CARGANDO LÍNEAS:', error);
                liniaSelect.innerHTML = '<option value="">❌ Error carregant línies</option>';
                liniaSelect.disabled = true;
            });
    });

    console.log('🎉 TODOS LOS FILTROS CONFIGURADOS CORRECTAMENTE');
});

console.log('📱 SCRIPT COMPLETO CARGADO - Esperando página...');