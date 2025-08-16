/**
 * CarregaHores - JavaScript para formulario de carga de horas
 * Maneja la interacción AJAX entre presupuestos y líneas
 */

class CarregaHoresManager {
    constructor() {
        this.pressupostSelect = document.getElementById("id_pressupost");
        this.liniaSelect = document.getElementById("id_linia");
        this.horesSelect = document.getElementById("id_hores_seleccionades");
        this.horesField = document.getElementById("id_hores");
        
        console.log('🔧 Constructor elements found:');
        console.log('  - pressupostSelect:', !!this.pressupostSelect);
        console.log('  - liniaSelect:', !!this.liniaSelect);
        console.log('  - horesSelect:', !!this.horesSelect);
        console.log('  - horesField:', !!this.horesField);
        
        this.init();
    }
    
    init() {
        if (!this.pressupostSelect || !this.liniaSelect) {
            console.error('Elements necessaris no trobats');
            return;
        }
        
        // Event listeners
        this.pressupostSelect.addEventListener("change", () => this.onPressupostChange());
        
        // Event listener para las horas seleccionadas
        if (this.horesSelect) {
            this.horesSelect.addEventListener("change", () => this.onHoresChange());
        }
        
        // Event listener para el formulario submit
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => this.onFormSubmit(e));
        }
        
        // Estado inicial
        this.updateLiniaState();
        
        // Si ya hay un presupuesto seleccionado, cargar líneas
        if (this.pressupostSelect.value) {
            this.loadLineas();
        }
        
        console.log('🎯 CarregaHores Manager inicializado');
    }
    
    onPressupostChange() {
        console.log('📝 Pressupost changed:', this.pressupostSelect.value);
        this.clearLinia();
        this.updateLiniaState();
        
        if (this.pressupostSelect.value) {
            this.loadLineas();
        }
    }
    
    onHoresChange() {
        console.log('⏰ onHoresChange triggered');
        console.log('  - horesSelect value:', this.horesSelect ? this.horesSelect.value : 'null');
        console.log('  - horesField exists:', !!this.horesField);
        
        if (this.horesSelect && this.horesField) {
            const selectedOption = this.horesSelect.options[this.horesSelect.selectedIndex];
            console.log('  - selectedOption:', selectedOption);
            console.log('  - selectedOption text:', selectedOption ? selectedOption.textContent : 'null');
            
            const horesValue = selectedOption.getAttribute('data-hores');
            console.log('  - data-hores attribute:', horesValue);
            
            this.horesField.value = horesValue || '';
            console.log('  - horesField value set to:', this.horesField.value);
            console.log('⏰ Hores actualitzades:', horesValue);
        } else {
            console.error('❌ Missing elements in onHoresChange');
        }
    }
    
    onFormSubmit(e) {
        console.log('📤 Form submit triggered');
        
        // Log all form data
        const formData = new FormData(e.target);
        console.log('📋 Form data being sent:');
        for (let [key, value] of formData.entries()) {
            console.log(`  - ${key}: "${value}"`);
        }
        
        // Specifically check hores field
        console.log('🎯 Specific field checks:');
        console.log('  - pressupost:', formData.get('pressupost'));
        console.log('  - linia:', formData.get('linia'));
        console.log('  - hores_seleccionades:', formData.get('hores_seleccionades'));
        console.log('  - hores:', formData.get('hores'));
        console.log('  - data:', formData.get('data'));
        
        // Don't prevent the default submission, just log
    }
    
    clearLinia() {
        this.liniaSelect.innerHTML = '<option value="">---------</option>';
        this.liniaSelect.disabled = true;
    }
    
    updateLiniaState() {
        if (!this.pressupostSelect.value) {
            this.liniaSelect.disabled = true;
            this.liniaSelect.innerHTML = '<option value="">Primer selecciona un pressupost</option>';
        }
    }
    
    async loadLineas() {
        const pressupostId = this.pressupostSelect.value;
        if (!pressupostId) return;
        
        try {
            // UI: Loading state
            this.liniaSelect.disabled = true;
            this.liniaSelect.innerHTML = '<option value="">🔄 Carregant línies...</option>';
            
            // Construir URL
            const url = new URL(window.location.origin + '/carrega-hores/ajax/lineas/');
            url.searchParams.set('pressupost', pressupostId);
            
            console.log('🌐 Fetching:', url.toString());
            
            const response = await fetch(url);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const lineas = await response.json();
            console.log('📦 Línies rebudes:', lineas.length);
            
            // Actualizar opciones
            this.populateLinias(lineas);
            
        } catch (error) {
            console.error('❌ Error carregant línies:', error);
            this.showLiniaError(error.message);
        }
    }
    
    populateLinias(lineas) {
        // Limpiar y añadir opción por defecto
        this.liniaSelect.innerHTML = '<option value="">Selecciona una línia...</option>';
        
        if (lineas.length === 0) {
            this.liniaSelect.innerHTML = '<option value="">No hi ha línies disponibles per aquest pressupost</option>';
            this.liniaSelect.disabled = true;
            return;
        }
        
        // Añadir líneas
        lineas.forEach(linia => {
            const option = document.createElement('option');
            option.value = linia.id;
            option.textContent = linia.detall;
            option.title = linia.detall; // Tooltip
            this.liniaSelect.appendChild(option);
        });
        
        this.liniaSelect.disabled = false;
        console.log('✅ Línies carregades:', lineas.length);
    }
    
    showLiniaError(message) {
        this.liniaSelect.innerHTML = `<option value="">❌ Error: ${message}</option>`;
        this.liniaSelect.disabled = true;
        
        // Mostrar alerta si es crítico
        if (message.includes('tancat') || message.includes('assignat')) {
            this.showAlert(message, 'warning');
        }
    }
    
    showAlert(message, type = 'info') {
        // Crear alerta temporal
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alertDiv.innerHTML = `
            <strong>Atenció:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insertar después del formulario
        const form = document.querySelector('form');
        form.parentNode.insertBefore(alertDiv, form.nextSibling);
        
        // Auto-hide después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
    new CarregaHoresManager();
});
