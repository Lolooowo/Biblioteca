
document.addEventListener("DOMContentLoaded", () => {
  // Toggle mostrar/ocultar confirmar contraseña
  const confirmar = document.getElementById("confirmar");
  const btnToggle = document.querySelector(".toggle");
  if (confirmar && btnToggle) {
    btnToggle.addEventListener("click", () => {
      const esPassword = confirmar.getAttribute("type") === "password";
      confirmar.type = esPassword ? "text" : "password";
      btnToggle.textContent = esPassword ? "Ocultar" : "Mostrar";
      const presionado = btnToggle.getAttribute("aria-pressed") === "true";
      btnToggle.setAttribute("aria-pressed", String(!presionado));
      confirmar.focus({ preventScroll: true });
    });
  }
  const contrasena = document.getElementById("contrasena");
  const btnToggle2 = document.querySelector(".toggle2");
  if (contrasena && btnToggle2) {
    btnToggle2.addEventListener("click", () => {
      const esPassword = contrasena.getAttribute("type") === "password";
      contrasena.type = esPassword ? "text" : "password";
      btnToggle2.textContent = esPassword ? "Ocultar" : "Mostrar";
      const presionado = btnToggle2.getAttribute("aria-pressed") === "true";
      btnToggle2.setAttribute("aria-pressed", String(!presionado));
      contrasena.focus({ preventScroll: true });
    });
  }
  

  const regForm = document.getElementById("form-registro");
  if (!regForm) return;

  const $ = (id) => document.getElementById(id);
  const chips = Array.from(document.querySelectorAll(".chip"));
  const hiddenCats = $("categorias");          // <input type="hidden" id="categorias">
  const countCats = $("cats-count");           // <span id="cats-count">
  const selectedContains = $("cats_selected"); // <div id="cats_selected">

  function getSelected(){
    return chips.filter(chip => chip.classList.contains("is-active"));
  }
  function updateEscondidas(){
    const valores = getSelected().map(chip => chip.dataset.value);
    if (hiddenCats) hiddenCats.value = JSON.stringify(valores);
  }
  function renderEstado(){
    const selec = getSelected();
    if (countCats) countCats.textContent = String(selec.length);
    if (selectedContains) {
      selectedContains.innerHTML = "";
      selec.forEach(chip => {
        const tag = document.createElement("span");
        tag.className = "chip--mini";
        tag.textContent = chip.dataset.value;
        selectedContains.appendChild(tag);
      });
    }
  }

  renderEstado();
  updateEscondidas();

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const activado = chip.classList.toggle("is-active");
      chip.setAttribute("aria-pressed", activado ? "true" : "false");
      if (activado) {
        chip.classList.add("anim--pulse");
        chip.addEventListener("animationend", () => chip.classList.remove("anim--pulse"), { once:true });
      }
      updateEscondidas();
      renderEstado();
    });
  });

  regForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const usuarioEl = $("usuario");
    const contrasenaEl = $("contrasena");
    const confirmarEl = $("confirmar");
    const tiempoEl = $("tiempo");

    const usuario = (usuarioEl?.value || "").trim();
    const contrasena = contrasenaEl?.value || "";
    const confirmarPwd = confirmarEl?.value || "";
    const tiempoNum = Number(tiempoEl?.value || NaN);

    if (!usuario || !contrasena || !confirmarPwd) {
      alert("No se pueden dejar espacios en blanco.");
      return;
    }
    if (contrasena !== confirmarPwd) {
      alert("Las contraseñas no coinciden.");
      return;
    }
    if (!Number.isInteger(tiempoNum)) {
      alert("El tiempo libre debe ser un número entero (minutos, por ejemplo).");
      return;
    }

    // categorías
    if (!hiddenCats?.value) updateEscondidas();
    let categorias = [];
    try {
      categorias = hiddenCats?.value ? JSON.parse(hiddenCats.value) : getSelected().map(x => x.dataset.value);
    } catch {
      categorias = getSelected().map(x => x.dataset.value);
    }
    const payload = {
      usuario: usuario,
      password: contrasena,
      tiempo_libre: tiempoNum,
      categorias: categorias
    };

    try {
      const res = await fetch("http://127.0.0.1:5000/api/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify(payload),
      });
      console.log(payload)
      const json = await res.json();

      if (!res.ok || !json.ok) {
        alert(json.message || "Error registrando al usuario.");
        return;
      }
      window.location.href = "./login.html";
      alert("Usuario creado correctamente.");
      
    } catch (err) {
      console.error(err);
      alert("No se pudo conectar con el servidor");
    }
  });
});
