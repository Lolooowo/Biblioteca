export const cat = "musica";
document.addEventListener("DOMContentLoaded", () => {
        const password = document.getElementById("password");
        const btnToggle = document.querySelector(".toggle");
        if (!password || !btnToggle) return;
        btnToggle.addEventListener("click", () => {
          const esPassword = password.getAttribute("type") === "password";
          password.type = esPassword ? "text" : "password";
          btnToggle.textContent = esPassword ? "Ocultar" : "Mostrar";
          const presionado = btnToggle.getAttribute("aria-pressed") === "true";
          btnToggle.setAttribute("aria-pressed", String(!presionado));
          password.focus({preventScroll: true});
        });
      });
      
const form = document.getElementById("form-login");
if(form){
  const usuario = document.getElementById("usuario");
  const password = document.getElementById("password");
  const btnSubmit = document.getElementById("btnLogin");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    if(data.usuario === ""||data.password === ""){
    alert("No se puede dejar espacios en blanco");
    return;
  }
  })


  form.addEventListener("submit", async (e) => {
  e.preventDefault();
  btnSubmit.setAttribute("disabled", "true");
  try{
    const resp = await fetch("http://127.0.0.1:5000/api/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      credentials: "include",
      body: JSON.stringify({
      usuario: usuario.value.trim(),
      password: password.value
      })
    });
    const datos = await resp.json();
      if (!resp.ok){
        alert(datos.message)
        form.Error = false;
        btnSubmit.removeAttribute("disabled");
        return;
      }
       //Si se incia sesion bien, te manda al home
      //cat = datos.cat;
      window.location.href = "/paginas/home.html";
    } catch (error){
      error.textContent = "Error en el servidor. Intente más tarde.";
      form.Error = false;
      btnSubmit.removeAttribute("disabled");
    }
  });
}
      


      