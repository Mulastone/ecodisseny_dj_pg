// Filtros dependientes CarregaHores - Versión corregida
console.log('🚀 INICIANDO FILTROS DEPENDIENTES...');

document.addEventListener('DOMContentLoaded', function () {
    console.log('📱 DOM CARGADO - Buscando elementos...');

    // Buscar elementos del formulario
    const clientFilter = document.querySelector('#id_client_filter');
    const projecteFilter = document.querySelector('#id_projecte_filter');
    const pressupostSelect = document.querySelector('#id_pressupost');
    const liniaSelect = document.querySelector('#id_linia');

    console.log('🔍 ELEMENTOS ENCONTRADOS:', {
        clientFilter: !!clientFilter,
        projecteFilter: !!projecteFilter,
        pressupostSelect: !!pressupostSelect,
        liniaSelect: !!liniaSelect
    });

    if (!clientFilter || !projecteFilter || !pressupostSelect || !liniaSelect) {
        console.error('❌ FALTAN ELEMENTOS DEL FORMULARIO');
        return;
    }

    console.log('✅ TODOS LOS ELEMENTOS ENCONTRADOS');

    // EVENTO: Cliente seleccionado
    clientFilter.addEventListener('change', function () {
        const clientId = this.value;
        console.log('👥 CLIENTE SELECCIONADO:', clientId);

        // Limpiar selects dependientes
        projecteFilter.value = '';
        pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';
        liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';

        if (!clientId) {
            console.log('🔄 Sin cliente - restaurando opciones por defecto');
            return;
        }

        // 1. Cargar proyectos del cliente
        console.log('📡 CARGANDO PROYECTOS...');
        fetch(`/carrega-hores/ajax/projectes-by-client/?client_id=${clientId}`)
            .then(response => {
                console.log('📡 RESPUESTA PROYECTOS:', response.status);
                return response.json();
            })
            .then(proyectos => {
                console.log('📁 PROYECTOS RECIBIDOS:', proyectos.length);

                projecteFilter.innerHTML = '<option value="">--- Filtrar per projecte ---</option>';
                proyectos.forEach(proyecto => {
                    const option = document.createElement('option');
                    option.value = proyecto.id;
                    option.textContent = proyecto.nom;
                    projecteFilter.appendChild(option);
                });
                console.log('✅ PROYECTOS ACTUALIZADOS');
            })
            .catch(error => {
                console.error('❌ ERROR CARGANDO PROYECTOS:', error);
            });

        // 2. Cargar presupuestos del cliente
        console.log('📡 CARGANDO PRESUPUESTOS...');
        fetch(`/carrega-hores/ajax/pressupostos-by-filters/?client_id=${clientId}`)
            .then(response => {
                console.log('📡 RESPUESTA PRESUPUESTOS:', response.status);
                return response.json();
            })
            .then(presupuestos => {
                console.log('📋 PRESUPUESTOS RECIBIDOS:', presupuestos.length);

                pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';
                presupuestos.forEach(presupuesto => {
                    const option = document.createElement('option');
                    option.value = presupuesto.id;
                    option.textContent = `${presupuesto.nom} (${presupuesto.client_nom} - ${presupuesto.projecte_nom})`;
                    pressupostSelect.appendChild(option);
                });
                console.log('✅ PRESUPUESTOS ACTUALIZADOS');
            })
            .catch(error => {
                console.error('❌ ERROR CARGANDO PRESUPUESTOS:', error);
            });
    });

    // EVENTO: Proyecto seleccionado
    projecteFilter.addEventListener('change', function () {
        const projecteId = this.value;
        const clientId = clientFilter.value;
        console.log('📁 PROYECTO SELECCIONADO:', projecteId);

        // Limpiar selects dependientes
        pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';
        liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';

        if (!projecteId) {
            // Si no hay proyecto, volver a cargar por cliente
            if (clientId) {
                console.log('🔄 Sin proyecto - recargando por cliente...');
                clientFilter.dispatchEvent(new Event('change'));
            }
            return;
        }

        // Cargar presupuestos por cliente + proyecto
        let url = `/carrega-hores/ajax/pressupostos-by-filters/?projecte_id=${projecteId}`;
        if (clientId) {
            url += `&client_id=${clientId}`;
        }

        console.log('📡 CARGANDO PRESUPUESTOS POR PROYECTO...');
        fetch(url)
            .then(response => {
                console.log('📡 RESPUESTA PRESUPUESTOS POR PROYECTO:', response.status);
                return response.json();
            })
            .then(presupuestos => {
                console.log('📋 PRESUPUESTOS POR PROYECTO:', presupuestos.length);

                pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';
                presupuestos.forEach(presupuesto => {
                    const option = document.createElement('option');
                    option.value = presupuesto.id;
                    option.textContent = `${presupuesto.nom} (${presupuesto.client_nom} - ${presupuesto.projecte_nom})`;
                    pressupostSelect.appendChild(option);
                });
                console.log('✅ PRESUPUESTOS POR PROYECTO ACTUALIZADOS');
            })
            .catch(error => {
                console.error('❌ ERROR CARGANDO PRESUPUESTOS POR PROYECTO:', error);
            });
    });

    // EVENTO: Presupuesto seleccionado
    pressupostSelect.addEventListener('change', function () {
        const pressupostId = this.value;
        console.log('📋 PRESUPUESTO SELECCIONADO:', pressupostId);

        liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';

        if (!pressupostId) {
            console.log('🔄 Sin presupuesto - no cargar líneas');
            return;
        }

        // Cargar líneas del presupuesto
        console.log('📡 CARGANDO LÍNEAS...');
        liniaSelect.innerHTML = '<option value="">🔄 Carregant línies...</option>';
        liniaSelect.disabled = true;

        fetch(`/carrega-hores/ajax/lineas/?pressupost_id=${pressupostId}`)
            .then(response => {
                console.log('📡 RESPUESTA LÍNEAS:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('📝 LÍNEAS RECIBIDAS:', data);

                liniaSelect.innerHTML = '<option value="">--- Selecciona una línia ---</option>';

                if (data.lineas && data.lineas.length > 0) {
                    data.lineas.forEach(linea => {
                        const option = document.createElement('option');
                        option.value = linea.id;
                        option.textContent = `${linea.treball} - ${linea.tasca} (${linea.recurs || 'Sense recurs'})`;
                        liniaSelect.appendChild(option);
                    });
                    liniaSelect.disabled = false;
                    console.log('✅ LÍNEAS CARGADAS');
                } else {
                    liniaSelect.innerHTML = '<option value="">No hi ha línies disponibles</option>';
                    console.log('⚠️ Sin líneas disponibles');
                }
            })
            .catch(error => {
                console.error('❌ ERROR CARGANDO LÍNEAS:', error);
                liniaSelect.innerHTML = '<option value="">❌ Error carregant línies</option>';
            })
            .finally(() => {
                liniaSelect.disabled = false;
            });
    });

    console.log('🎉 FILTROS DEPENDIENTES CONFIGURADOS');
});

console.log('📱 SCRIPT CARGADO - Esperando DOM...');