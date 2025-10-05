/**
 * Debug simplificado para CarregaHores - Filtros dependientes
 */

// Debug directo al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DEBUG: Página cargada, iniciando debug...');

    // Verificar elementos
    const clientFilter = document.getElementById("id_client_filter");
    const projecteFilter = document.getElementById("id_projecte_filter");
    const pressupostSelect = document.getElementById("id_pressupost");

    console.log('🔧 Elementos encontrados:');
    console.log('  - clientFilter:', clientFilter ? 'SÍ' : 'NO');
    console.log('  - projecteFilter:', projecteFilter ? 'SÍ' : 'NO');
    console.log('  - pressupostSelect:', pressupostSelect ? 'SÍ' : 'NO');

    if (clientFilter) {
        console.log('  - clientFilter ID:', clientFilter.id);
        console.log('  - clientFilter opciones:', clientFilter.options.length);

        // Event listener directo y simple
        clientFilter.addEventListener('change', function () {
            const selectedClientId = this.value;
            console.log('🎯 CLIENTE CAMBIADO:', selectedClientId);

            if (selectedClientId && projecteFilter) {
                console.log('🔄 Filtrando proyectos...');

                // Hacer petición AJAX
                fetch(`/carrega-hores/ajax/projectes-by-client/?client_id=${selectedClientId}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => {
                        console.log('📡 Respuesta status:', response.status);
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(proyectos => {
                        console.log('📁 Proyectos recibidos:', proyectos);

                        // Limpiar y actualizar select de proyectos
                        projecteFilter.innerHTML = '<option value="">--- Filtrar per projecte ---</option>';

                        proyectos.forEach(proyecto => {
                            const option = document.createElement('option');
                            option.value = proyecto.id;
                            option.textContent = proyecto.nom;
                            option.setAttribute('data-client', proyecto.client_id);
                            projecteFilter.appendChild(option);
                            console.log('➕ Proyecto agregado:', proyecto.nom);
                        });

                        console.log('✅ Proyectos actualizados correctamente');
                    })
                    .catch(error => {
                        console.error('❌ Error filtrando proyectos:', error);
                    });

            } else if (!selectedClientId && projecteFilter) {
                console.log('🔄 Restaurando todos los proyectos...');
                // Aquí deberíamos restaurar todos los proyectos
                // Por ahora solo mostramos el mensaje
            }
        });

        console.log('✅ Event listener del cliente configurado');
    } else {
        console.error('❌ No se encontró el filtro de cliente');
    }

    // También configurar el filtro de proyecto si existe
    if (projecteFilter) {
        projecteFilter.addEventListener('change', function () {
            const selectedProjecteId = this.value;
            const selectedClientId = clientFilter ? clientFilter.value : '';

            console.log('🎯 PROYECTO CAMBIADO:', selectedProjecteId);
            console.log('📋 Cliente actual:', selectedClientId);

            if (pressupostSelect && (selectedClientId || selectedProjecteId)) {
                console.log('🔄 Filtrando presupuestos...');

                let url = '/carrega-hores/ajax/pressupostos-by-filters/?';
                const params = new URLSearchParams();

                if (selectedClientId) params.append('client_id', selectedClientId);
                if (selectedProjecteId) params.append('projecte_id', selectedProjecteId);

                url += params.toString();
                console.log('📡 URL presupuestos:', url);

                fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(presupuestos => {
                        console.log('📋 Presupuestos recibidos:', presupuestos);

                        // Actualizar select de presupuestos
                        pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';

                        presupuestos.forEach(presupuesto => {
                            const option = document.createElement('option');
                            option.value = presupuesto.id;
                            option.textContent = `${presupuesto.nom} (${presupuesto.client_nom} - ${presupuesto.projecte_nom})`;
                            pressupostSelect.appendChild(option);
                            console.log('➕ Presupuesto agregado:', presupuesto.nom);
                        });

                        console.log('✅ Presupuestos actualizados correctamente');
                    })
                    .catch(error => {
                        console.error('❌ Error filtrando presupuestos:', error);
                    });
            }
        });

        console.log('✅ Event listener del proyecto configurado');
    }

    console.log('🎉 Debug inicialización completada');
});

// También mantener la clase original por si se necesita
class CarregaHoresManager {
    constructor() {
        console.log('📱 CarregaHoresManager constructor ejecutado');
        // Versión simple para debug
    }
}

// Inicializar para compatibilidad
document.addEventListener('DOMContentLoaded', function () {
    new CarregaHoresManager();
});