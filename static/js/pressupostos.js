if (window.__pressupostos_js_loaded__) {
  console.warn("⚠️ pressupostos.js ja carregat, s'ignora execució duplicada.");
} else {
  window.__pressupostos_js_loaded__ = true;

  document.addEventListener("DOMContentLoaded", function () {
    console.log("🧩 Script pressupostos.js carregat ✅");

        // 🔄 Eliminar línies buides abans de guardar
    document.querySelector("form")?.addEventListener("submit", () => {
      netejarLiniesBuides();
    });

    function netejarLiniesBuides() {
      document.querySelectorAll(".pressupost-linea").forEach((linea) => {
        const inputs = linea.querySelectorAll("input, select, textarea");
        const isEmpty = [...inputs].every(el =>
          (el.type === "checkbox" || el.type === "radio") ? true : !el.value
        );

        if (isEmpty) {
          const deleteField = linea.querySelector(`[name$="-DELETE"]`);
          if (deleteField) {
            deleteField.checked = true;
            linea.style.display = "none";
          } else {
            linea.remove();
            const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
            totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
          }
        }
      });
    }


    const clientField = document.querySelector("#id_client");
    clientField?.addEventListener("change", function () {
      const clientId = this.value;
      console.log("🔄 Canvi de client:", clientId);
      const projectSelect = document.querySelector("#id_projecte");
      if (!clientId || clientId === "0") {
        projectSelect.innerHTML = '<option value="">Seleccioni Projecte</option>';
        return;
      }
      fetch(`/pressupostos/get_projectes/${clientId}/`)
        .then((response) => response.json())
        .then((data) => {
          console.log("📦 Projectes rebuts:", data);
          projectSelect.innerHTML = '<option value="">Seleccioni Projecte</option>';
          data.forEach((item) => {
            const option = document.createElement("option");
            option.value = item.id;
            option.textContent = item.nom;
            projectSelect.appendChild(option);
          });
        });
    });

    document.querySelectorAll(".pressupost-linea").forEach((linea, index) => {
      console.log(`🔧 Inicialitzant línia ${index}`);
      setupLinea(linea, index);
    });

    const addBtn = document.querySelector("#add-linea");
    if (addBtn) {
      addBtn.addEventListener("click", function () {
        const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
        const currentIndex = parseInt(totalFormsInput.value);
        const container = document.querySelector("#lineas-container");
        const emptyForm = document.querySelector("#empty-form");

        if (!emptyForm) {
          console.error("❌ No es troba #empty-form al DOM.");
          return;
        }

        const newLinea = emptyForm.cloneNode(true);
        newLinea.removeAttribute("id");
        newLinea.style.display = "";
        newLinea.classList.add("pressupost-linea");

        newLinea.querySelectorAll("input, select, textarea, label").forEach((el) => {
          if (el.name) el.name = el.name.replace(/__prefix__/, currentIndex);
          if (el.id) el.id = el.id.replace(/__prefix__/, currentIndex);
          if (el.tagName !== "LABEL") {
            if (el.type === "checkbox" || el.type === "radio") {
              el.checked = false;
            } else {
              el.value = "";
            }

            // 🟢 Inicialitzar benefici a 10
            if (el.name?.endsWith("-benefici")) {
              el.value = "10";
            }
            if (el.name?.endsWith("-quantitat")) {
              el.value = "1";
            }
          }
        });


        newLinea.querySelectorAll("input[readonly]").forEach((el) => el.value = "");

        totalFormsInput.value = currentIndex + 1;
        container.appendChild(newLinea);
        setupLinea(newLinea, currentIndex);
        console.log("➕ Nova línia afegida:", currentIndex);
      });
    }

    function setupLinea(linea, index) {
      console.log(`⚙️ Setup de línia [${index}]`);

      const treballSelect = linea.querySelector(`[id$="-treball"]`);
      const tascaSelect = linea.querySelector(`[id$="-tasca"]`);
      const recursSelect = linea.querySelector(`[id$="-recurs"]`);
      const preuTancatCheck = linea.querySelector(`[id$="-preu_tancat"]`);
      const horaField = linea.querySelector(`[id$="-hora"]`);
      const horesHidden = linea.querySelector(".hores-value");
      const incrementField = linea.querySelector(`[id$="-increment_hores"]`);
      const horesTotalsField = linea.querySelector(`[id$="-hores_totals"]`);
      const costHoresField = linea.querySelector(`[id$="-cost_hores"]`);
      const costTotalsField = linea.querySelector(`[id$="-cost_hores_totals"]`);
      const costTancatField = linea.querySelector(`[id$="-cost_tancat"]`);
      const subtotalField = linea.querySelector(`[id$="-subtotal"]`);
      const quantitatField = linea.querySelector(`[id$="-quantitat"]`);
      const beneficiField = linea.querySelector(`[id$="-benefici"]`);
      const totalLineaField = linea.querySelector(`[id$="-total"]`);
      const deleteBtn = linea.querySelector(".eliminar-linea");

      // 🔒 Bloquejar select hora si preu_tancat activat
      if (preuTancatCheck && horaField) {
        function toggleHoraSelect() {
          if (preuTancatCheck.checked) {
            horaField.value = "";
            horaField.disabled = true;
          } else {
            horaField.disabled = false;
          }
        }
        preuTancatCheck?.addEventListener("change", toggleHoraSelect);
        toggleHoraSelect();
      }

      
      deleteBtn?.addEventListener("click", () => {
        const deleteField = linea.querySelector(`[name$="-DELETE"]`);
        if (deleteField) {
          deleteField.checked = true;
          linea.style.display = "none";
        } else {
          linea.remove();
        }
        calcularTotalPressupost();
      });

      
      treballSelect?.addEventListener("change", function () {
        const idTreball = this.value;
        console.log("📥 Treball seleccionat:", idTreball);
        tascaSelect.innerHTML = '<option value="">Seleccioni Tasca</option>';
        if (idTreball) {
          fetch(`/pressupostos/get_tasques/${idTreball}/`)
            .then((res) => res.json())
            .then((data) => {
              console.log("📦 Tasques rebudes:", data);
              const tasques = data.tasques || [];
              tasques.forEach((item) => {
                const option = document.createElement("option");
                option.value = item.id;
                option.textContent = item.tasca;
                tascaSelect.appendChild(option);
              });
            });
        }
      });

      recursSelect?.addEventListener("change", function () {
        const idRecurs = this.value;
        console.log("📦 Recurs seleccionat:", idRecurs);
        if (!idRecurs) return;
        fetch(`/pressupostos/get_recurso/${idRecurs}/`)
          .then((res) => res.json())
          .then((data) => {
            console.log("📦 Dades del recurs:", data);
            if (data.PreuTancat) {
              preuTancatCheck.checked = true;
              horaField.classList.add("readonly-select");
              horaField.value = "";
              horaField.disabled = true;
              costTancatField.removeAttribute("readonly");
              incrementField.value = "0";
              horesTotalsField.value = "0";
              costHoresField.value = "";
              costTotalsField.value = "";
            } else {
              preuTancatCheck.checked = false;
              horaField.classList.remove("readonly-select");
              horaField.disabled = false;
              costTancatField.setAttribute("readonly", "readonly");
              costHoresField.value = data.PreuHora || "0";
            }
            calcularSubtotal();
          });
      });

      [document.querySelector("#id_parroquia"), document.querySelector("#id_ubicacio"), tascaSelect].forEach((el) => {
        el?.addEventListener("change", () => {
          const idParroquia = document.querySelector("#id_parroquia")?.value;
          const idUbicacio = document.querySelector("#id_ubicacio")?.value;
          const idTasca = tascaSelect?.value;
          if (idParroquia && idUbicacio && idTasca) {
            console.log("🔍 Buscant increment hores per:", { idParroquia, idUbicacio, idTasca });
            fetch(`/pressupostos/get_increment_hores/?id_parroquia=${idParroquia}&id_ubicacio=${idUbicacio}&id_tasca=${idTasca}`)
              .then((res) => res.json())
              .then((data) => {
                console.log("📦 increment_hores rebut:", data);
                if (data.increment_hores !== undefined) {
                  incrementField.value = data.increment_hores;
                  calcularSubtotal();
                }
              });
          }
        });
      });

      if (horaField && horesHidden) {
        horaField.addEventListener("change", () => {
          const selectedOption = horaField.options[horaField.selectedIndex];
          const hores = selectedOption?.dataset.hores || 0;
          console.log("⏱️ Hores seleccionades:", hores);
          horesHidden.value = hores;
          calcularSubtotal();
        });
      }

      [horaField, incrementField, costHoresField, quantitatField, costTancatField].forEach((el) =>
        el?.addEventListener("input", calcularSubtotal)
      );
      beneficiField?.addEventListener("input", calcularSubtotal);

      function calcularSubtotal() {
        const q = parseFloat(quantitatField.value) || 0;
        const h = parseFloat(horesHidden.value) || 0;
        const inc = parseFloat(incrementField?.value) || 0;
        const cost = parseFloat(costHoresField?.value) || 0;
        const costTancat = parseFloat(costTancatField?.value) || 0;
        const preuTancat = preuTancatCheck?.checked;

        const totalHores = (h + inc) * q;
        const totalCostHores = totalHores * cost;
        const subtotal = preuTancat ? q * costTancat : totalCostHores;

        console.log("🧮 Subtotal línia", {
          quantitat: q,
          hores: h,
          increment: inc,
          costHora: cost,
          costTancat,
          totalHores,
          totalCostHores,
          subtotal
        });

        horesTotalsField.value = totalHores.toFixed(2);
        costTotalsField.value = totalCostHores.toFixed(4);
        subtotalField.value = subtotal.toFixed(4);

        const beneficiPercent = parseFloat(beneficiField.value) || 0;
        const benefici = subtotal * (beneficiPercent / 100);
        const total = subtotal + benefici;

        totalLineaField.value = total.toFixed(2);
        calcularTotalPressupost();
      }
    }

    function calcularTotalPressupost() {
      let total = 0;
      document.querySelectorAll(".pressupost-linea").forEach((linea) => {
        const isDeleted = linea.querySelector(`[name$="-DELETE"]`)?.checked;
        if (isDeleted) return;
        const totalLineaField = linea.querySelector(`[name$="-total"]`);
        total += parseFloat(totalLineaField?.value || "0");
      });
      const totalPressupostElement = document.getElementById("total-pressupost");
      if (totalPressupostElement) {
        totalPressupostElement.textContent = total.toFixed(2);
      }
    }

    calcularTotalPressupost();

     // 🎯 Flatpickr en català amb format dd/mm/yyyy
    flatpickr(".datepicker", {
      dateFormat: "d/m/Y",
      locale: "cat",
      allowInput: true,
    });
  });
     

}
