async function  CargarLibros() {
    try{
        const url = "https://openlibrary.org/search.json?q=*&sort=random&limit=33&fields=key,title,author_name,cover_i,subject,subject_facet,subject_key"
        const respuesta = await fetch(url);
        const datos =  await respuesta.json();
        const docs = datos.docs || [];
        // aqui empezamos a ver su faltan las categorias para las recomendaciones
        const work = docs.filter(doc => !doc.subject && doc.key);
        const workMap = {};
        await Promise.all(work.map(async doc => {
            const workR = await fetch("https://openlibrary.org" + doc.key + ".json");
            const jWork = await workR.json();
            workMap[doc.key] = jWork.language || null;
            workMap[doc.key] = jWork.subjects || null;
        }));
        // Ahora ya hacemos el docs con las categorias
         return docs.map(doc => {
            const subjects = doc.subject || doc.subject_facet || workMap[doc.key] || [];
            return {
                titulo: doc.title,
                autores: doc.author_name || [],
                categorias: subjects,
                portada: doc.cover_i ? "https://covers.openlibrary.org/b/id/" + doc.cover_i + "-M.jpg" : null,
                url:"https://openlibrary.org" + doc.key,
                idioma: doc.language || []
            };
        });
        
    }catch(error){
        console.log("Error: " + error);
    }
}

// function BuscarTitulo(titulo) {
//     const respuesta = fetch("http://openLibrary.org/search.json?title=" + titulo)
//         .then(res => res.json())
// }
recomendaciones1 = CargarLibros()
recomendaciones2 = CargarLibros()
Promise.all([recomendaciones1, recomendaciones2]).then(values => {
    const recomendaciones = [...values[0], ...values[1]];
    console.log(recomendaciones)
})
