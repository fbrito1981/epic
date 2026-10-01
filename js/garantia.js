const form = document.querySelector(".claim-form");
const status = document.querySelector(".form-status");
const send = form.querySelector(".send");
const phone = form.elements.telefono;
const email = form.elements.email;
const verifyDialog = document.querySelector(".verify");
const doneDialog = document.querySelector(".done");
const verifyForm = document.querySelector(".verify-form");
const verifyStatus = document.querySelector(".verify-status");
const verifyMail = document.querySelector(".verify-mail");
const codeInput = document.querySelector("#codigo");
const confirmButton = verifyForm.querySelector(".send");
const actions = document.querySelector(".form-actions");
const back = actions.querySelector(".back");
const PHONE_RE = /^[0-9]{8,15}$/;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const CODE_RE = /^[0-9]{8}$/;

let pendingToken = "";

function digitsOnly(input, max) {
  const digits = input.value.replace(/\D/g, "").slice(0, max);
  if (input.value !== digits) input.value = digits;
}

function explain() {
  digitsOnly(phone, 15);
  if (!phone.value) phone.setCustomValidity("Ingresá tu teléfono.");
  else if (!PHONE_RE.test(phone.value)) phone.setCustomValidity("Ingresá solo números, con código de área. Ejemplo: 3434123456.");
  else phone.setCustomValidity("");

  if (!email.value) email.setCustomValidity("Ingresá tu email.");
  else if (!EMAIL_RE.test(email.value)) email.setCustomValidity("Ingresá un email válido. Ejemplo: nombre@correo.com.");
  else email.setCustomValidity("");
}

function payload() {
  return {
    nombre: form.elements.nombre.value.trim(),
    direccion: form.elements.direccion.value.trim(),
    telefono: form.elements.telefono.value.trim(),
    email: form.elements.email.value.trim(),
    comentarios: form.elements.comentarios.value.trim()
  };
}

async function post(body) {
  const response = await fetch("/api/garantia", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify(body)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) {
    const error = new Error(data.error || "No se pudo enviar");
    error.code = data.error || "";
    throw error;
  }
  return data;
}

let holdingBack = false;

function clearForm() {
  form.reset();
  form.querySelectorAll("input, textarea").forEach((field) => field.setCustomValidity(""));
  pendingToken = "";
  status.textContent = "";
  status.classList.remove("is-error");
  codeInput.value = "";
  verifyStatus.textContent = "";
  verifyStatus.classList.remove("is-error");
}

function alignBack(dialog) {
  const rect = actions.getBoundingClientRect();
  dialog.appendChild(back);
  back.style.position = "fixed";
  back.style.top = `${rect.top}px`;
  back.style.left = "auto";
  back.style.right = `${window.innerWidth - rect.right}px`;
}

function restoreBack() {
  back.style.position = "";
  back.style.top = "";
  back.style.left = "";
  back.style.right = "";
  actions.appendChild(back);
}

function finish() {
  clearForm();
  if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
  holdingBack = true;
  verifyDialog.close();
  doneDialog.showModal();
  alignBack(doneDialog);
  holdingBack = false;
}

function volver() {
  clearForm();
  holdingBack = true;
  if (verifyDialog.open) verifyDialog.close();
  if (doneDialog.open) doneDialog.close();
  holdingBack = false;
  restoreBack();
  window.location.href = "index.html";
}

phone.addEventListener("input", () => digitsOnly(phone, 15));
email.addEventListener("input", () => email.setCustomValidity(""));
codeInput.addEventListener("input", () => {
  digitsOnly(codeInput, 8);
  verifyStatus.textContent = "";
  verifyStatus.classList.remove("is-error");
});

function onDialogDismiss(dialog) {
  if (holdingBack) return;
  const other = dialog === verifyDialog ? doneDialog : verifyDialog;
  if (other.open) return;
  restoreBack();
}

verifyDialog.querySelector(".verify-close").addEventListener("click", () => verifyDialog.close());
doneDialog.querySelector(".done-close").addEventListener("click", () => doneDialog.close());
for (const dialog of [verifyDialog, doneDialog]) {
  dialog.addEventListener("close", () => onDialogDismiss(dialog));
  dialog.addEventListener("beforetoggle", (event) => {
    if (event.newState === "closed") onDialogDismiss(dialog);
  });
}
back.addEventListener("click", volver);
function trackBack() {
  if (verifyDialog.open) alignBack(verifyDialog);
  else if (doneDialog.open) alignBack(doneDialog);
}
window.addEventListener("resize", trackBack);
window.addEventListener("scroll", trackBack, true);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "";
  status.classList.remove("is-error");

  if (form.elements._honey.value) return;

  explain();
  if (!form.reportValidity()) return;

  const data = payload();
  send.disabled = true;
  const previous = send.textContent;
  send.textContent = "Enviando";

  try {
    const result = await post({ paso: "codigo", ...data });
    pendingToken = result.token;
    verifyMail.textContent = data.email;
    codeInput.value = "";
    verifyStatus.textContent = "";
    verifyStatus.classList.remove("is-error");
    holdingBack = true;
    verifyDialog.showModal();
    alignBack(verifyDialog);
    holdingBack = false;
    codeInput.focus();
  } catch (error) {
    status.textContent = "No pudimos enviar la solicitud. Escribinos a info@fuerz4.com.";
    status.classList.add("is-error");
  } finally {
    send.disabled = false;
    send.textContent = previous;
  }
});

verifyForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  verifyStatus.textContent = "";
  verifyStatus.classList.remove("is-error");
  digitsOnly(codeInput, 8);

  if (!CODE_RE.test(codeInput.value)) {
    verifyStatus.textContent = "Ingresá los 8 dígitos que te enviamos.";
    verifyStatus.classList.add("is-error");
    return;
  }

  confirmButton.disabled = true;
  const previous = confirmButton.textContent;
  confirmButton.textContent = "Confirmando";

  try {
    await post({ paso: "confirmar", token: pendingToken, codigo: codeInput.value });
    holdingBack = true;
    verifyDialog.close();
    finish();
  } catch (error) {
    verifyStatus.textContent = error.code === "código incorrecto" || error.code === "código vencido"
      ? "El código no coincide. Revisá el correo e intentá de nuevo."
      : "No pudimos confirmar el código. Escribinos a info@fuerz4.com.";
    verifyStatus.classList.add("is-error");
  } finally {
    confirmButton.disabled = false;
    confirmButton.textContent = previous;
  }
});
