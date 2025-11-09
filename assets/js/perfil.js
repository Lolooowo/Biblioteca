const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
async function librosLeyendo() {
    const res = await fetch("http://127.0.0.1:5000/api/leyendo");
    if(!res.ok) throw new Error("Error al obtener los libros");
    const libros = await res.json();
    return libros;
}
function renderLibros(libros){
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
    console.error("Error al cargar los libros de la categoría:", error);
  }
});