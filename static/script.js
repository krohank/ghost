// script.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chatForm");
  const input = form.querySelector("input");

  form.addEventListener("submit", () => {
    input.disabled = true;
    setTimeout(() => {
      input.disabled = false;
      input.focus();
    }, 500); // Slight delay to mimic processing
  });
});
