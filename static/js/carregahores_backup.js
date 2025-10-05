/**
 * CarregaHores - JavaScript para formulario de carga de horas
 * Sistema de filtros dependientes: Cliente -> Proyecto -> Presupuesto
 */

class CarregaHoresManager {
    constructor() {
        this.pressupostSelect = document.getElementById("id_pressupost");
        this.liniaSelect = document.getElementById("id_linia");
        this.horesSelect = document.getElementById("id_hores_seleccionades");
        this.horesField = document.getElementById("id_hores");

        // Campos de filtro
        this.clientFilter = document.getElementById("id_client_filter");
        this.projecteFilter = document.getElementById("id_projecte_filter");

        console.log('🔧 Elementos encontrados:');
        console.log('  - pressupostSelect:', !!this.pressupostSelect);
        console.log('  - liniaSelect:', !!this.liniaSelect);
        console.log('  - horesSelect:', !!this.horesSelect);
        console.log('  - clientFilter:', !!this.clientFilter);
        console.log('  - projecteFilter:', !!this.projecteFilter);

        // Cache de datos originales
        this.originalProjecteOptions = [];
        this.allPressupostos = [];

        this.init();
    }

    async init() {
        if (!this.pressupostSelect || !this.liniaSelect) {
            console.error('❌ Elementos necesarios no encontrados');
            return;
        }

        // Guardar opciones originales de proyectos
        this.saveOriginalProjecteOptions();

        // Cargar todos los presupuestos
        await this.loadAllPressupostos();

        // Event listeners
        this.setupEventListeners();

        // Estado inicial
        this.updateLiniaState();

        // Si ya hay un presupuesto seleccionado, cargar líneas
        if (this.pressupostSelect.value) {
            this.loadLineas();
        }

        console.log('✅ CarregaHores Manager inicializado con filtros dependientes');
    }

    saveOriginalProjecteOptions() {
        if (this.projecteFilter) {
            this.originalProjecteOptions = Array.from(this.projecteFilter.options).map(option => ({
                value: option.value,
                text: option.text,
                clientId: option.getAttribute('data-client') || ''
            }));
        }
    }

    async loadAllPressupostos() {
        try {
            const response = await fetch('/carrega-hores/ajax/pressupostos-data/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            this.allPressupostos = await response.json();
            console.log('📊 Presupuestos cargados:', this.allPressupostos.length);

        } catch (error) {
            console.error('❌ Error cargando presupuestos:', error);
            this.allPressupostos = [];
        }
    }

    setupEventListeners() {
        console.log('🔧 Configurando event listeners...');

        // Presupuesto cambio -> cargar líneas
        this.pressupostSelect.addEventListener("change", () => this.onPressupostChange());
        console.log('✅ Event listener presupuesto configurado');

        // Filtro cliente -> filtrar proyectos y presupuestos
        if (this.clientFilter) {
            this.clientFilter.addEventListener("change", () => {
                console.log('🎯 Event disparado: cliente cambió');
                this.onClientFilterChange();
            });
            console.log('✅ Event listener cliente configurado');
        } else {
            console.warn('⚠️ clientFilter no encontrado');
        }

        // Filtro proyecto -> filtrar presupuestos
        if (this.projecteFilter) {
            this.projecteFilter.addEventListener("change", () => {
                console.log('🎯 Event disparado: proyecto cambió');
                this.onProjecteFilterChange();
            });
            console.log('✅ Event listener proyecto configurado');
        } else {
            console.warn('⚠️ projecteFilter no encontrado');
        }

        // Horas seleccionadas
        if (this.horesSelect) {
            this.horesSelect.addEventListener("change", () => this.onHoresChange());
            console.log('✅ Event listener horas configurado');
        }

        // Submit del formulario
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => this.onFormSubmit(e));
            console.log('✅ Event listener formulario configurado');
        }

        console.log('🎉 Todos los event listeners configurados');
    }

    async onClientFilterChange() {
        const selectedClientId = this.clientFilter.value;
        console.log('👥 Cliente seleccionado:', selectedClientId);
        console.log('🔧 DEBUG: Iniciando filtrado por cliente...');

        // Resetear proyecto y presupuesto
        if (this.projecteFilter) {
            this.projecteFilter.value = '';
            console.log('🔄 Proyecto reseteado');
        }
        this.pressupostSelect.value = '';
        this.clearLinia();

        if (selectedClientId) {
            console.log('🔄 Filtrando proyectos y presupuestos...');
            // Filtrar proyectos por cliente
            await this.filterProjectesByClient(selectedClientId);
            // Filtrar presupuestos por cliente
            this.filterPressupostsByClient(selectedClientId);
        } else {
            console.log('🔄 Restaurando todos los elementos...');
            // Restaurar todos los proyectos
            this.restoreAllProjectes();
            // Restaurar todos los presupuestos
            this.restoreAllPressupostos();
        }
        console.log('✅ Filtrado por cliente completado');
    }

    async filterProjectesByClient(clientId) {
        console.log('🔧 DEBUG: filterProjectesByClient iniciado con clientId:', clientId);

        try {
            const url = `/carrega-hores/ajax/projectes-by-client/?client_id=${clientId}`;
            console.log('📡 Haciendo petición a:', url);

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const projectes = await response.json();
            console.log('📁 Proyectos recibidos:', projectes.length, projectes);

            // Verificar que el select de proyectos existe
            if (!this.projecteFilter) {
                console.error('❌ ERROR: projecteFilter no encontrado');
                return;
            }

            // Actualizar select de proyectos
            console.log('🔄 Actualizando select de proyectos...');
            this.projecteFilter.innerHTML = '<option value="">--- Filtrar per projecte ---</option>';

            projectes.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = p.nom;
                option.setAttribute('data-client', p.client_id);
                this.projecteFilter.appendChild(option);
                console.log('➕ Proyecto agregado:', p.nom);
            });

            console.log('✅ Select de proyectos actualizado correctamente');

        } catch (error) {
            console.error('❌ Error filtrando proyectos:', error);
        }
    }

    filterPressupostsByClient(clientId) {
        const filteredPressupostos = this.allPressupostos.filter(p =>
            p.client_id && p.client_id.toString() === clientId.toString()
        );

        this.updatePressupostSelect(filteredPressupostos);
        console.log('📋 Presupuestos filtrados por cliente:', filteredPressupostos.length);
    }

    async onProjecteFilterChange() {
        const selectedProjecteId = this.projecteFilter.value;
        const selectedClientId = this.clientFilter.value;

        console.log('📁 Proyecto seleccionado:', selectedProjecteId);

        // Resetear presupuesto
        this.pressupostSelect.value = '';
        this.clearLinia();

        if (selectedProjecteId) {
            // Filtrar presupuestos por proyecto
            await this.filterPressupostsByFilters(selectedClientId, selectedProjecteId);
        } else if (selectedClientId) {
            // Solo filtrar por cliente
            this.filterPressupostsByClient(selectedClientId);
        } else {
            // Restaurar todos los presupuestos
            this.restoreAllPressupostos();
        }
    }

    async filterPressupostsByFilters(clientId = null, projecteId = null) {
        try {
            let url = '/carrega-hores/ajax/pressupostos-by-filters/?';
            const params = new URLSearchParams();

            if (clientId) params.append('client_id', clientId);
            if (projecteId) params.append('projecte_id', projecteId);

            url += params.toString();

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const pressupostos = await response.json();
            this.updatePressupostSelect(pressupostos);
            console.log('📋 Presupuestos filtrados:', pressupostos.length);

        } catch (error) {
            console.error('❌ Error filtrando presupuestos:', error);
        }
    } restoreAllProjectes() {
        if (!this.projecteFilter) return;

        this.projecteFilter.innerHTML = '<option value="">--- Filtrar per projecte ---</option>';
        this.originalProjecteOptions.forEach(opt => {
            if (opt.value) { // Skip empty option
                const option = document.createElement('option');
                option.value = opt.value;
                option.textContent = opt.text;
                option.setAttribute('data-client', opt.clientId);
                this.projecteFilter.appendChild(option);
            }
        });
    }

    restoreAllPressupostos() {
        this.updatePressupostSelect(this.allPressupostos);
    }

    updatePressupostSelect(pressupostos) {
        this.pressupostSelect.innerHTML = '<option value="">--- Selecciona un pressupost ---</option>';

        pressupostos.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = `${p.nom} (${p.client_nom} - ${p.projecte_nom})`;
            option.setAttribute('data-client', p.client_id || '');
            option.setAttribute('data-projecte', p.projecte_id || '');
            this.pressupostSelect.appendChild(option);
        });
    }

    onPressupostChange() {
        console.log('📋 Presupuesto seleccionado:', this.pressupostSelect.value);

        if (this.pressupostSelect.value) {
            this.loadLineas();
        } else {
            this.clearLinia();
        }
    }

    onHoresChange() {
        const selectedOption = this.horesSelect.options[this.horesSelect.selectedIndex];
        const hores = selectedOption ? selectedOption.getAttribute('data-hores') : '0';

        if (this.horesField) {
            this.horesField.value = hores || '0';
        }

        console.log('⏰ Horas seleccionadas:', hores);
    }

    onFormSubmit(e) {
        console.log('📤 Enviando formulario...');

        // Validaciones básicas
        if (!this.pressupostSelect.value) {
            e.preventDefault();
            this.showAlert('Cal seleccionar un pressupost', 'error');
            return false;
        }

        if (!this.liniaSelect.value) {
            e.preventDefault();
            this.showAlert('Cal seleccionar una línia del pressupost', 'error');
            return false;
        }

        // Asegurar que el campo hores tenga valor
        this.onHoresChange();

        return true;
    }

    clearLinia() {
        this.liniaSelect.innerHTML = '<option value="">--- Primer selecciona un pressupost ---</option>';
        this.liniaSelect.disabled = true;
        console.log('🧹 Líneas limpiadas');
    }

    updateLiniaState() {
        const hasPressupost = this.pressupostSelect.value !== '';
        this.liniaSelect.disabled = !hasPressupost;
    }

    async loadLineas() {
        const pressupostId = this.pressupostSelect.value;

        if (!pressupostId) {
            this.clearLinia();
            return;
        }

        console.log('🔄 Cargando líneas para presupuesto:', pressupostId);

        try {
            const response = await fetch(`/carrega-hores/ajax/lineas/?pressupost_id=${pressupostId}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.error) {
                this.showLiniaError(data.error);
                return;
            }

            this.populateLinias(data.lineas || []);

        } catch (error) {
            console.error('❌ Error cargando líneas:', error);
            this.showLiniaError('Error de conexión. Intenta de nuevo.');
        }
    }

    populateLinias(lineas) {
        console.log('📋 Populando líneas:', lineas.length);

        this.liniaSelect.innerHTML = '<option value="">--- Selecciona una línia ---</option>';

        if (lineas.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = '--- No hi ha línies disponibles ---';
            option.disabled = true;
            this.liniaSelect.appendChild(option);
            this.liniaSelect.disabled = true;
            return;
        }

        lineas.forEach(linia => {
            const option = document.createElement('option');
            option.value = linia.id;
            option.textContent = `${linia.treball} - ${linia.tasca} (${linia.recurs || 'Sense recurs'})`;
            this.liniaSelect.appendChild(option);
        });

        this.liniaSelect.disabled = false;
        console.log('✅ Líneas cargadas correctamente');
    }

    showLiniaError(message) {
        this.liniaSelect.innerHTML = `<option value="">${message}</option>`;
        this.liniaSelect.disabled = true;
        console.error('❌ Error en líneas:', message);
    }

    showAlert(message, type = 'info') {
        // Crear alerta temporal
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insertar al inicio del formulario
        const form = document.querySelector('form');
        if (form) {
            form.insertBefore(alertDiv, form.firstChild);

            // Auto-dismiss después de 5 segundos
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Inicializando CarregaHores Manager...');
    new CarregaHoresManager();
});