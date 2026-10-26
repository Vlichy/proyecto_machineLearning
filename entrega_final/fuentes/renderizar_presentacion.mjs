// Importar el PowerPoint final y exportar vistas para revisión visual sin modificarlo.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const runtime='C:/Users/panio/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
// Cargar únicamente el archivo de presentación final para su inspección.
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'entrega_final/presentacion_final.pptx')));
// Renderizar todas las diapositivas para revisar legibilidad y distribución.
for(let i=0;i<p.slides.items.length;i++){let png=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(root,'tmp/fase10',`final-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));}
console.log('15 diapositivas finales renderizadas. Sin modificar el PPTX.');
