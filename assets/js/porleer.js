const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
let libroSeleccionado = null;
async function librosLeidos() {
    const resp = await fetch("http://127.0.0.1:5000/api/por-leers", {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
        },
        credentials: "include"
    });
    const datos = await resp.json();
    if (!resp.ok) {
        throw new Error(datos.message || "Error al obtener los libros que se están leyendo");
    }
    return datos.libros;
}
function renderLibros(libros){
    if(libros.length === 0){
        const librosGrind = document.getElementById("librosGrid");
        librosGrind.innerHTML = "<p class='no-books-message'>No hay libros en Por Leer.</p>";
        return;
    }
  const librosGrind = document.getElementById("librosGrid");
  librosGrind.innerHTML = "";
  libros.forEach(libro => {
    const libroCard = document.createElement("div");
    libroCard.className = "book-card";
    libroCard.innerHTML = `
      <img src="${libro.portada}" alt="${libro.titulo}" class="book-image"/>
      <div class="book-info">
      <h3 class="book-title">${libro.titulo}</h3>
      <p class="book-author">${libro.autores.join(", ")}</p>
      </div>
    `;
    libroCard.addEventListener("click", () => abrirMenuLibro(libro));
    
    librosGrind.appendChild(libroCard);
  });
}
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const libros = await librosLeidos();
    renderLibros(libros);
  } catch (error) {
    console.error("Error al cargar los libros que se están leyendo", error);
  }
});



function abrirMenuLibro(libro){
  const menu = document.getElementById("menuLibro");
  const imagen = document.getElementById("imagenLibro");
  const titulo = document.getElementById("tituloLibro");
  const autor = document.getElementById("autorLibro");
  const descripcion = document.getElementById("descripcionLibro");
  const eliminar = document.getElementById("eliminarPorLeer");

  imagen.src = libro.portada;
  imagen.alt = libro.titulo;
  titulo.textContent = libro.titulo;
  autor.textContent =  `Por: ${libro.autores.join(", ")}`;
  descripcion.textContent = libro.descripcion || "Sin descripción disponible.";
  menu.classList.add("active");

  eliminar.addEventListener("click", async () => {
    try{
        const resp = await fetch("http://127.0.0.1:5000/api/por_leer/delete",{
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({id_libro: libro.id_libro})
        });
        const datos = await resp.json();
        if (!resp.ok) {
            throw new Error(datos.message || "Error al eliminar el libro de por leer");
        }
        alert("Libro eliminado de Por Leer correctamente.");
    } catch (error) {
        console.error("Error al eliminar el libro de Leídos", error);
        
  }

});
}
function cerrarMenuLibro(){
  const menu = document.getElementById("menuLibro");
  menu.classList.remove("active");
}
const BtnCerrarMenu = document.getElementById("cerrarMenu");

BtnCerrarMenu.addEventListener("click", cerrarMenuLibro);