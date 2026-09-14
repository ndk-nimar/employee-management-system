/* Small UI helpers. No framework, no build step.
   Everything here is progressive: the app still works with JS disabled,
   because deletion also has its own confirmation page and the sidebar
   links are plain anchors. */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    setupSidebar();
    setupToasts();
    setupDeleteModal();
    setupPasswordToggle();
  });

  /* Mobile sidebar -------------------------------------------------------*/
  function setupSidebar() {
    var sidebar = document.getElementById("sidebar");
    var scrim = document.querySelector(".sidebar-scrim");
    if (!sidebar) return;

    function open() {
      sidebar.classList.add("is-open");
      if (scrim) scrim.hidden = false;
      document.body.style.overflow = "hidden";
    }

    function close() {
      sidebar.classList.remove("is-open");
      if (scrim) scrim.hidden = true;
      document.body.style.overflow = "";
    }

    document.querySelectorAll("[data-sidebar-open]").forEach(function (el) {
      el.addEventListener("click", open);
    });
    document.querySelectorAll("[data-sidebar-close]").forEach(function (el) {
      el.addEventListener("click", close);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
  }

  /* Auto-dismissing flash messages --------------------------------------*/
  function setupToasts() {
    document.querySelectorAll("[data-autodismiss]").forEach(function (toast, index) {
      var timer = window.setTimeout(function () {
        dismiss(toast);
      }, 5000 + index * 400);

      var closeBtn = toast.querySelector("[data-toast-close]");
      if (closeBtn) {
        closeBtn.addEventListener("click", function () {
          window.clearTimeout(timer);
          dismiss(toast);
        });
      }
    });

    function dismiss(toast) {
      toast.classList.add("is-leaving");
      window.setTimeout(function () {
        toast.remove();
      }, 320);
    }
  }

  /* Delete confirmation modal on the employee table ----------------------*/
  function setupDeleteModal() {
    var modal = document.getElementById("deleteModal");
    if (!modal) return;

    modal.addEventListener("show.bs.modal", function (event) {
      var trigger = event.relatedTarget;
      if (!trigger) return;

      var form = modal.querySelector("[data-delete-form]");
      var nameSlot = modal.querySelector("[data-delete-name]");
      var idSlot = modal.querySelector("[data-delete-id]");

      // The form posts to this employee's delete URL; the CSRF token is
      // already inside the form, rendered by Django.
      if (form) form.setAttribute("action", trigger.dataset.deleteUrl || "");
      if (nameSlot) nameSlot.textContent = trigger.dataset.employeeName || "this employee";
      if (idSlot) idSlot.textContent = trigger.dataset.employeeId || "";
    });
  }

  /* Show/hide password on the login page ---------------------------------*/
  function setupPasswordToggle() {
    var toggle = document.querySelector("[data-password-toggle]");
    if (!toggle) return;

    toggle.addEventListener("click", function () {
      var input = toggle.parentElement.querySelector("input");
      if (!input) return;
      var showing = input.type === "text";
      input.type = showing ? "password" : "text";
      toggle.innerHTML = showing
        ? '<i class="bi bi-eye"></i>'
        : '<i class="bi bi-eye-slash"></i>';
      toggle.setAttribute("aria-label", showing ? "Show password" : "Hide password");
    });
  }
})();
