const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
let libroSeleccionado = null;
async function librosLeyendo() {
    const resp = await fetch("http://127.0.0.1:5000/api/leyendos", {
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
        librosGrind.innerHTML = "<p class='no-books-message'>No estás leyendo ningún libro actualmente.</p>";
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
    const libros = await librosLeyendo();
    renderLibros(libros);
  } catch (error) {
    console.error("Error al cargar los libros que se están leyendo", error);
  }
});
const pasarLeidos = document.getElementById("pasarLeidos");
pasarLeidos?.addEventListener("click", async () => {
    if (!libroSeleccionado) return;
    try{
        const resp = await fetch("http://127.0.0.1:5000/api/mover_a_leidos",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({id_libro: libroSeleccionado.id_libro
            })
        });
        const datos = await resp.json();
        if (!resp.ok) {
            throw new Error(datos.message || "Error al mover el libro a Leídos");
        }
        alert("Libro movido a Leídos correctamente.");
    } catch (error) {
        console.error("Error al mover el libro a Leídos", error);
    }
});



function abrirMenuLibro(libro, libros) {
  libroSeleccionado = libro;

  const menu = document.getElementById("menuLibro");
  const imagen = document.getElementById("imagenLibro");
  const titulo = document.getElementById("tituloLibro");
  const autor = document.getElementById("autorLibro");
  const descripcion = document.getElementById("descripcionLibro");

  if (imagen) {
    imagen.src = libro.portada;
    imagen.alt = libro.titulo;
  }
  if (titulo) titulo.textContent = libro.titulo;
  if (autor) autor.textContent = `Por: ${libro.autores.join(", ")}`;
  if (descripcion) descripcion.textContent = libro.descripcion || "Sin descripción disponible.";
  menu?.classList.add("active");

  const BtnCerrarMenu = document.getElementById("cerrarMenu");
  if (BtnCerrarMenu) {
    BtnCerrarMenu.onclick = () => cerrarMenuLibro(libros);
  }
}

function cerrarMenuLibro(libros) {
  const menu = document.getElementById("menuLibro");
  menu?.classList.remove("active");
}