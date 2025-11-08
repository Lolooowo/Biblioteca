//import { cat } from "./login";      
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const cat = "musica";
const API_KEY = "AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o";
const BASE = "https://www.googleapis.com/books/v1/volumes";
//const urlCategorias = `https://www.googleapis.com/books/v1/volumes?q=subject:${categoria}$&maxResults=10&startIndex=0&orderBy=relevance&key=AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o`;
//const urlBusqueda = `https://www.googleapis.com/books/v1/volumes?q=${busqueda}&maxResults=10&startIndex=0&orderBy=relevance&key=${API_KEY}`;

async function buscarLibrosCategoria(cat){
  const urlCategorias = `https://www.googleapis.com/books/v1/volumes?q=subjects:${cat}$&maxResults=40&startIndex=0&orderBy=relevance&langRestrict=es&key=AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o`;
  const busqueda = await fetch(urlCategorias);
  if(!busqueda.ok){
    throw new Error(`ERROR en la llamada a la API: ${busqueda.status}`);
  }
  const datos = await busqueda.json();
  const items = datos.items || [];
  if(items.length === 0){
    throw new Error("No se encontraron libros para la categoría seleccionada.");
  }

  const soloPortada = items.filter(item => mejorPortada(item.volumeInfo?.imageLinks))
  .map(item => {
    const info = item.volumeInfo || {};
    return {
          id: item.id,
          titulo: item.volumeInfo.title,
          autores: item.volumeInfo.authors || ["Desconocido"],
          categoria: item.volumeInfo.categories ? item.volumeInfo.categories[0] : "Sin categoría",
          portada: mejorPortada(info.imageLinks),
          descripcion: item.volumeInfo.description || "Sin descripción",
          paginas: item.volumeInfo.pageCount || "Desconocido",
          editorial: item.volumeInfo.publisher || "Desconocido",
          fecha: item.volumeInfo.publishedDate || "Desconocido",
          idioma: item.volumeInfo.language || "Desconocido",
          enlace: item.volumeInfo.infoLink || "",
        };
      });
      return soloPortada;
    }

    


    async function buscarLibros(busqueda){
      const urlBusqueda = `https://www.googleapis.com/books/v1/volumes?q=${busqueda}&maxResults=40&startIndex=0&orderBy=relevance&langRestrict=es&key=AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o`;
      const busquedaLibros =  await fetch(urlBusqueda)
      if(!busquedaLibros.ok){
        throw new Error(`ERROR en la llamada a la API: ${busquedaLibros.status}`);
      }
      const datos = await busquedaLibros.json();
      const items = datos.items || [];
      if(items.length === 0){
        throw new Error("No se encontraron libros para la búsqueda realizada.");
      }

      const soloPortada = items.filter(item => mejorPortada(item.volumeInfo?.imageLinks))
      .map(item => {
        const info = item.volumeInfo || {};
        return {
          id: item.id,
          titulo: item.volumeInfo.title,
          autores: item.volumeInfo.authors || ["Desconocido"],
          categoria: item.volumeInfo.categories ? item.volumeInfo.categories[0] : "Sin categoría",
          portada: mejorPortada(info.imageLinks),
          descripcion: item.volumeInfo.description || "Sin descripción",
          paginas: item.volumeInfo.pageCount || "Desconocido",
          editorial: item.volumeInfo.publisher || "Desconocido",
          fecha: item.volumeInfo.publishedDate || "Desconocido",
          idioma: item.volumeInfo.language || "Desconocido",
          enlace: item.volumeInfo.infoLink || "",
        };
      });
      return soloPortada;
    }

    function mejorPortada(imageLinks){
      if(!imageLinks) return null;
      const posibles = [
        imageLinks.extraLarge,
        imageLinks.large,
        imageLinks.medium,
        imageLinks.small,
        imageLinks.thumbnail,
        imageLinks.smallThumbnail
      ].filter(Boolean);
      return posibles.length ? elLink(posibles[0]) : null;
    }
    function elLink(url){
      if(!url) return url;
      let nuevaUrl = url.replace(/^http:\/\//, 'https://');
      if(nuevaUrl.includes("zoom=0")){
        nuevaUrl=nuevaUrl.replace("zoom=0", "zoom=1");
      }else if(!nuevaUrl.includes("zoom=")){
        nuevaUrl += "&zoom=1";
      }
      return nuevaUrl;
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
    const libros = await buscarLibrosCategoria(cat);
    renderLibros(libros);
  } catch (error) {
    console.error("Error al cargar los libros de la categoría:", error);
  }
});

const buscarInput = document.getElementById("buscador");
const resultados = document.getElementById("resutados");
const termino = document.getElementById("aBuscar");
const tituloMain = document.getElementById("tituloMain");
const regresarInicio = document.getElementById("regresarInicio");

buscarInput.addEventListener("input", async (e)=>{
  const valor = e.target.value.toLowerCase();
  if(valor === "") {
    showRecomendaciones();
  }else{
    const librosBuscados = await buscarLibros(valor);
    renderLibros(librosBuscados);
    resultados.classList.remove("hidden");
    termino.textContent = valor;
    tituloMain.textContent = `Resultados de búsqueda para: "${valor}"`;
  }
});
regresarInicio.addEventListener("click", () => {
  showRecomendaciones();
  tituloMain.textContent = "Recomendaciones para ti";
  resultados.classList.add("hidden");
  buscarInput.value = "";
});
async function showRecomendaciones(){
  resultados.classList.add("hidden");
  tituloMain.textContent = "Recomendaciones para ti";
  const libros = await buscarLibrosCategoria(cat);
  renderLibros(libros);
}

function abrirMenuLibro(libro){
  const menu = document.getElementById("menuLibro");
  const imagen = document.getElementById("imagenLibro");
  const titulo = document.getElementById("tituloLibro");
  const autor = document.getElementById("autorLibro");
  const descripcion = document.getElementById("descripcionLibro");

  imagen.src = libro.portada;
  imagen.alt = libro.titulo;
  titulo.textContent = libro.titulo;
  autor.textContent =  `Por: ${libro.autores.join(", ")}`;
  descripcion.textContent = libro.descripcion || "Sin descripción disponible.";
  menu.classList.add("active");

document.getElementById("porLeer").addEventListener("click", async () => {
// Aqui colocamos el fetch para enviar el libro al por leer del usuario
  try {
    const resp = await fetch("http://127.0.0.1:5000/api/por-leer", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      credentials: "include",
      body: JSON.stringify({
        id_libro: libro.id,
        titulo: libro.titulo,
        autores: libro.autores,
        categoria: libro.categoria,
        portada: libro.portada,
        descripcion: libro.descripcion,
        paginas: libro.paginas,
        editorial: libro.editorial,
        idioma: libro.idioma,
        enlace: libro.enlace,
        })
    });
    const datos = await resp.json();
      if (!resp.ok){
        alert(datos.message)
        return;
      }
      alert("Libro agregado a tu lista de libros Por Leer.");
    } catch (error){
      alert("Error en el servidor. Intente más tarde.");
    }
});
const submenu = document.getElementById("subMenuleyendo");
const leyendo = document.getElementById("leyendo");
if(submenu && leyendo){
  document.getElementById("leyendo").addEventListener("click", async () => {
  //Aqui colocamos el fetch para enviar el libro al leyendo del usuario
  submenu.hidden = false;
  const primeraOpcion = document.querySelector("-submenu-item");
  primeraOpcion && primeraOpcion.focus();

  const cerrarsubMenu = document.querySelector(".submenu-close");
  if(cerrarsubMenu){
    cerrarsubMenu.addEventListener("click", () => submenu.hidden = true);
  }
  const opcion1 = document.getElementById("opcion1");
  const opcion2 = document.getElementById("opcion2");
  const opcion3 = document.getElementById("opcion3");
  const pagxhora = 40;
  const horas = libro.paginas / pagxhora;
  
  opcion1.textContent = `Leer 1 hora al día: Libro acabado en: ${Math.ceil(horas)} días`;
  opcion1.dataset.action = "1";
  opcion2.textContent = `Leer 2 horas al día: Libro acabado en: ${Math.ceil(horas / 2)} días`;
  opcion2.dataset.action = "2";
  opcion3.textContent = `Leer 3 horas al día: Libro acabado en: ${Math.ceil(horas / 3)} días`;
  opcion3.dataset.action = "3";
  submenu?.addEventListener("click", async (e) => {
    const btn = e.target.closest(".submenu-item");
    if(!btn) return;
    const horas = btn.dataset.action;
    if(!horas) return;
    try {
    const resp = await fetch("http://127.0.0.1:5000/api/leyendo", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      credentials: "include",
      body: JSON.stringify({
        id_libro: libro.id,
        titulo: libro.titulo,
        autores: libro.autores,
        categoria: libro.categoria,
        portada: libro.portada,
        descripcion: libro.descripcion,
        paginas: libro.paginas,
        editorial: libro.editorial,
        idioma: libro.idioma,
        enlace: libro.enlace,
        horas: horas
        })
    });
    const datos = await resp.json();
      if (!resp.ok){
        alert(datos.message)
        return;
      }
      alert("Libro agregado a tu lista de libros leyendo.");
    } catch (error){
      alert("Error en el servidor. Intente más tarde.");
    }
  });
});
}

document.getElementById("leidos").addEventListener("click", async () => {
  //Aqui colocamos el fetch para enviar el libro al leidos del usuario
  try {
    const resp = await fetch("http://127.0.0.1:5000/api/leido", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      credentials: "include",
      body: JSON.stringify({
        id_libro: libro.id,
        titulo: libro.titulo,
        autores: libro.autores,
        categoria: libro.categoria,
        portada: libro.portada,
        descripcion: libro.descripcion,
        paginas: libro.paginas,
        editorial: libro.editorial,
        idioma: libro.idioma,
        enlace: libro.enlace,
        })
    });
    const datos = await resp.json();
      if (!resp.ok){
        alert(datos.message)
        return;
      }
      alert("Libro agregado a tu lista de libros leídos.");
    } catch (error){
      alert("Error en el servidor. Intente más tarde.");
    }
});
}

function cerrarMenuLibro(){
  const menu = document.getElementById("menuLibro");
  menu.classList.remove("active");
}
const BtnCerrarMenu = document.getElementById("cerrarMenu");

BtnCerrarMenu.addEventListener("click", cerrarMenuLibro);




