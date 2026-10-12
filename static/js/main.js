// Gym Management System - Main Client JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // 1. Sidebar Toggle for Mobile
  const toggleBtn = document.getElementById("sidebarToggle");
  const sidebar = document.querySelector(".sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  // 2. Demo Credentials Filler (for rapid testing & viva demo)
  window.fillCredentials = function (email, password) {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    if (emailInput && passwordInput) {
      emailInput.value = email;
      passwordInput.value = password;
      // highlight effect
      emailInput.classList.add("is-valid");
      passwordInput.classList.add("is-valid");
      setTimeout(() => {
        emailInput.classList.remove("is-valid");
        passwordInput.classList.remove("is-valid");
      }, 1200);
    }
  };

  // 3. Dynamic Exercise Row in Workout Plan Builders
  const addExerciseBtn = document.getElementById("addExerciseBtn");
  const exerciseContainer = document.getElementById("exerciseContainer");

  if (addExerciseBtn && exerciseContainer) {
    addExerciseBtn.addEventListener("click", function () {
      const rowCount = exerciseContainer.querySelectorAll(".exercise-row").length;
      const newRow = document.createElement("div");
      newRow.className = "row g-2 mb-2 exercise-row align-items-center";
      newRow.innerHTML = `
        <div class="col-md-4">
          <input type="text" name="exercise_name[]" class="form-control form-control-sm" placeholder="Exercise Name (e.g. Bench Press)" required>
        </div>
        <div class="col-md-2">
          <input type="text" name="exercise_sets[]" class="form-control form-control-sm" placeholder="Sets (e.g. 3)" value="3">
        </div>
        <div class="col-md-2">
          <input type="text" name="exercise_reps[]" class="form-control form-control-sm" placeholder="Reps (e.g. 10-12)" value="10">
        </div>
        <div class="col-md-3">
          <input type="text" name="exercise_notes[]" class="form-control form-control-sm" placeholder="Form Tips / Notes">
        </div>
        <div class="col-md-1 text-end">
          <button type="button" class="btn btn-outline-danger btn-sm remove-row-btn" title="Remove Exercise">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      `;
      exerciseContainer.appendChild(newRow);

      // Attach remove handler
      newRow.querySelector(".remove-row-btn").addEventListener("click", function () {
        newRow.remove();
      });
    });

    // Delegate remove handler for initial rows
    exerciseContainer.querySelectorAll(".remove-row-btn").forEach(btn => {
      btn.addEventListener("click", function () {
        btn.closest(".exercise-row").remove();
      });
    });
  }

  // 4. Auto-dismiss flash alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {}
    }, 5000);
  });
});
