document.addEventListener("DOMContentLoaded", () => {
  const forms = [
    { id: "signinForm", fields: ["email", "password"] },
    { id: "signupForm", fields: ["name", "email", "password", "confirm_password"] },
    { id: "resetPasswordForm", fields: ["email"] },
    { id: "resetPasswordTokenForm", fields: ["password", "confirm_password"] },
  ];

  const clearFields = (form, fields) => {
    fields.forEach((name) => {
      const field = form.querySelector(`[name="${name}"]`);
      if (field) {
        field.value = "";
        field.setAttribute("value", "");
      }
    });
  };

  forms.forEach(({ id, fields }) => {
    const form = document.getElementById(id);
    if (!form) return;

    const clearIfRestored = (event) => {
      const nav = performance.getEntriesByType("navigation")[0];
      const fromBackForward = event.persisted || nav?.type === "back_forward";

      if (fromBackForward) {
        clearFields(form, fields);
        requestAnimationFrame(() => clearFields(form, fields));
        setTimeout(() => clearFields(form, fields), 50);
      }
    };

    window.addEventListener("pageshow", clearIfRestored);
    window.addEventListener("pagehide", () => clearFields(form, fields));
    window.addEventListener("beforeunload", () => clearFields(form, fields));
  });
});
