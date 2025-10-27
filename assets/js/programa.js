      const $ = (sel, ctx = document) => ctx.querySelector(sel);
      const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
      
      const API_KEY = "AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o";
      const BASE = "https://www.googleapis.com/books/v1/volumes";
      //const urlCategorias = `https://www.googleapis.com/books/v1/volumes?q=subject:${categoria}$&maxResults=10&startIndex=0&orderBy=relevance&key=AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o`;
      //const urlBusqueda = `https://www.googleapis.com/books/v1/volumes?q=${busqueda}&maxResults=10&startIndex=0&orderBy=relevance&key=${API_KEY}`;

      async function buscarLibrosCategoria(categoria){
        const urlCategorias = `https://www.googleapis.com/books/v1/volumes?q=subjects:${categoria}$&maxResults=40&startIndex=0&orderBy=relevance&langRestrict=es&key=AIzaSyAgkuRpajM23siZRnyA4GQhrpOxz0OmC1o`;
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
        return url ? url.replace(/^http:\/\//, 'https://') : url;
      }



      const busqueda = document.getElementById("busqueda");
      const botonBuscar = document.getElementById("btnBuscar"); 

      botonBuscar.addEventListener("click", async () => {
        const librosBuscados =  await buscarLibros(busqueda.value)
        console.log(librosBuscados);
      });

      const buscarPorGustos = buscarLibrosCategoria("Fiction")
      console.log(buscarPorGustos);