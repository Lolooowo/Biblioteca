//import { cat } from "./login";
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

const cat = "musica";
const API_KEY = "AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o";
const BASE = "https://www.googleapis.com/books/v1/volumes";

let libroSeleccionado = null;

async function buscarLibrosCategoria(cat) {
  const urlCategorias = `https://www.googleapis.com/books/v1/volumes?q=subjects:${cat}$&maxResults=40&startIndex=0&orderBy=relevance&langRestrict=es&key=${API_KEY}`;
  const busqueda = await fetch(urlCategorias);
  if (!busqueda.ok) {
    throw new Error(`ERROR en la llamada a la API: ${busqueda.status}`);
  }
  const datos = await busqueda.json();
  const items = datos.items || [];
  if (items.length === 0) {
    throw new Error("No se encontraron libros para la categoría seleccionada.");
  }

  const soloPortada = items
    .filter((item) => mejorPortada(item.volumeInfo?.imageLinks))
    .map((item) => {
      const info = item.volumeInfo || {};
      return {
        id: item.id,
        titulo: info.title,
        autores: info.authors || ["Desconocido"],
        categoria: info.categories ? info.categories[0] : "Sin categoría",
        portada: mejorPortada(info.imageLinks),
        descripcion: info.description || "Sin descripción",
        paginas: info.pageCount || "Desconocido",
        editorial: info.publisher || "Desconocido",
        fecha: info.publishedDate || "Desconocido",
        idioma: info.language || "Desconocido",
        enlace: info.infoLink || "",
      };
    });
  return soloPortada;
}

async function buscarLibros(termino) {
  const urlBusqueda = `https://www.googleapis.com/books/v1/volumes?q=${termino}&maxResults=40&startIndex=0&orderBy=relevance&langRestrict=es&key=${API_KEY}`;
  const busquedaLibros = await fetch(urlBusqueda);
  if (!busquedaLibros.ok) {
    throw new Error(`ERROR en la llamada a la API: ${busquedaLibros.status}`);
  }
  const datos = await busquedaLibros.json();
  const items = datos.items || [];
  if (items.length === 0) {
    throw new Error("No se encontraron libros para la búsqueda realizada.");
  }

  const soloPortada = items
    .filter((item) => mejorPortada(item.volumeInfo?.imageLinks))
    .map((item) => {
      const info = item.volumeInfo || {};
      return {
        id: item.id,
        titulo: info.title,
        autores: info.authors || ["Desconocido"],
        categoria: info.categories ? info.categories[0] : "Sin categoría",
        portada: mejorPortada(info.imageLinks),
        descripcion: info.description || "Sin descripción",
        paginas: info.pageCount || "Desconocido",
        editorial: info.publisher || "Desconocido",
        fecha: info.publishedDate || "Desconocido",
        idioma: info.language || "Desconocido",
        enlace: info.infoLink || "",
      };
    });
  return soloPortada;
}

function mejorPortada(imageLinks) {
  if (!imageLinks) return null;
  const posibles = [
    imageLinks.extraLarge,
    imageLinks.large,
    imageLinks.medium,
    imageLinks.small,
    imageLinks.thumbnail,
    imageLinks.smallThumbnail,
  ].filter(Boolean);
  return posibles.length ? elLink(posibles[0]) : null;
}

function elLink(url) {
  if (!url) return url;
  let nuevaUrl = url.replace(/^http:\/\//, "https://");
  if (nuevaUrl.includes("zoom=0")) {
    nuevaUrl = nuevaUrl.replace("zoom=0", "zoom=1");
  } else if (!nuevaUrl.includes("zoom=")) {
    nuevaUrl += "&zoom=1";
  }
  return nuevaUrl;
}

function renderLibros(libros) {
  const librosGrid = document.getElementById("librosGrid");
  if (!librosGrid) return;
  librosGrid.innerHTML = "";

  libros.forEach((libro) => {
    const libroCard = document.createElement("div");
    libroCard.className = "book-card";
    libroCard.innerHTML = `
      <img src="${libro.portada}" alt="${libro.titulo}" class="book-image"/>
      <div class="book-info">
        <h3 class="book-title">${libro.titulo}</h3>
        <p class="book-author">${libro.autores.join(", ")}</p>
      </div>
    `;
    libroCard.addEventListener("click", () => abrirMenuLibro(libro, libros));
    librosGrid.appendChild(libroCard);
  });
}

async function showRecomendaciones() {
  const resultados = document.getElementById("resutados");
  const tituloMain = document.getElementById("tituloMain");
  resultados?.classList.add("hidden");
  if (tituloMain) tituloMain.textContent = "Recomendaciones para ti";

  const libros = await buscarLibrosCategoria(cat);
  renderLibros(libros);
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const libros = await buscarLibrosCategoria(cat);
    renderLibros(libros);
  } catch (error) {
    console.error("Error al cargar los libros de la categoría:", error);
  }

  // Búsqueda
  const buscarInput = document.getElementById("buscador");
  const resultados = document.getElementById("resutados");
  const termino = document.getElementById("aBuscar");
  const tituloMain = document.getElementById("tituloMain");
  const regresarInicio = document.getElementById("regresarInicio");

  buscarInput?.addEventListener("input", async (e) => {
    const valor = e.target.value.toLowerCase();
    if (valor === "") {
      showRecomendaciones();
    } else {
      const librosBuscados = await buscarLibros(valor);
      renderLibros(librosBuscados);
      resultados?.classList.remove("hidden");
      if (termino) termino.textContent = valor;
      if (tituloMain) tituloMain.textContent = `Resultados de búsqueda para: "${valor}"`;
    }
  });

  regresarInicio?.addEventListener("click", () => {
    showRecomendaciones();
    if (tituloMain) tituloMain.textContent = "Recomendaciones para ti";
    resultados?.classList.add("hidden");
    if (buscarInput) buscarInput.value = "";
  });

  const btnPorLeer = document.getElementById("porLeer");
  const btnLeidos = document.getElementById("leidos");
  const btnLeyendo = document.getElementById("leyendo");
  const submenu = document.getElementById("subMenuleyendo");
  const cerrarSub = document.querySelector(".submenu-close");

  // POR LEER
  btnPorLeer?.addEventListener("click", async () => {
    if (!libroSeleccionado) return;
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/por-leer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          id_libro: libroSeleccionado.id,
          titulo: libroSeleccionado.titulo,
          autores: libroSeleccionado.autores,
          categoria: libroSeleccionado.categoria,
          portada: libroSeleccionado.portada,
          descripcion: libroSeleccionado.descripcion,
          paginas: libroSeleccionado.paginas,
          editorial: libroSeleccionado.editorial,
          idioma: libroSeleccionado.idioma,
          enlace: libroSeleccionado.enlace,
        }),
      });
      const datos = await resp.json();
      if (!resp.ok) {
        alert(datos.detail || "Error");
        return;
      }
      alert("Libro agregado a tu lista de Por leer.");
    } catch (error) {
      alert("Error en el servidor. Intente más tarde.");
    }
  });

  // LEYENDO:
  btnLeyendo?.addEventListener("click", () => {
    if (!libroSeleccionado || !submenu) return;
    submenu.hidden = false;

    const opcion1 = document.getElementById("opcion1");
    const opcion2 = document.getElementById("opcion2");
    const opcion3 = document.getElementById("opcion3");
    const pagxhora = 40;
    const horasTotales = (Number(libroSeleccionado.paginas) || 0) / pagxhora;

    if (opcion1) {
      opcion1.textContent = `Leer 1 hora al día: Libro acabado en: ${Math.ceil(horasTotales)} días`;
      opcion1.dataset.action = "1";
    }
    if (opcion2) {
      opcion2.textContent = `Leer 2 horas al día: Libro acabado en: ${Math.ceil(horasTotales / 2)} días`;
      opcion2.dataset.action = "2";
    }
    if (opcion3) {
      opcion3.textContent = `Leer 3 horas al día: Libro acabado en: ${Math.ceil(horasTotales / 3)} días`;
      opcion3.dataset.action = "3";
    }
  });

  cerrarSub?.addEventListener("click", () => {
    if (submenu) submenu.hidden = true;
  });

  submenu?.addEventListener("click", async (e) => {
    const btn = e.target.closest(".submenu-item");
    if (!btn || !libroSeleccionado) return;
    const horas = btn.dataset.action;
    if (!horas) return;

    try {
      const resp = await fetch("http://127.0.0.1:5000/api/leyendo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          id_libro: libroSeleccionado.id,
          titulo: libroSeleccionado.titulo,
          autores: libroSeleccionado.autores,
          categoria: libroSeleccionado.categoria,
          portada: libroSeleccionado.portada,
          descripcion: libroSeleccionado.descripcion,
          paginas: libroSeleccionado.paginas,
          editorial: libroSeleccionado.editorial,
          idioma: libroSeleccionado.idioma,
          enlace: libroSeleccionado.enlace,
          horas_dia: horas,
        }),
      });
      const datos = await resp.json();
      if (!resp.ok) {
        alert(datos.message || "Error");
        return;
      }
      alert("Libro agregado a tu lista de Leyendo.");
      submenu.hidden = true;
    } catch (error) {
      alert("Error en el servidor. Intente más tarde.");
    }
  });

  // LEÍDOS
  btnLeidos?.addEventListener("click", async () => {
    if (!libroSeleccionado) return;
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/leido", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          id_libro: libroSeleccionado.id,
          titulo: libroSeleccionado.titulo,
          autores: libroSeleccionado.autores,
          categoria: libroSeleccionado.categoria,
          portada: libroSeleccionado.portada,
          descripcion: libroSeleccionado.descripcion,
          paginas: libroSeleccionado.paginas,
          editorial: libroSeleccionado.editorial,
          idioma: libroSeleccionado.idioma,
          enlace: libroSeleccionado.enlace,
        }),
      });
      const datos = await resp.json();
      if (!resp.ok) {
        alert(datos.message || "Error");
        return;
      }
      alert("Libro agregado a tu lista de Leídos.");
    } catch (error) {
      alert("Error en el servidor. Intente más tarde.");
    }
  });
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