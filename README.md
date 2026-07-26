# 0xBitácora — blog personal (Jinja2)

Generador de sitio estático para un blog de ciberseguridad, CTF y hacking.
Escribes posts en Markdown con front matter, y `build.py` los convierte en
HTML usando las plantillas Jinja2 de `/templates`.

## Estructura

```
blog/
├── build.py          # genera el sitio en /site
├── new_post.py        # crea un post nuevo con front matter listo
├── posts/              # tus posts en Markdown (.md)
├── templates/           # base.html, index.html, post.html, about.html
├── static/
│   ├── css/style.css     # todo el diseño vive aquí
│   ├── css/pygments.css  # resaltado de sintaxis, mismo tema de color
│   └── js/main.js         # botón "copiar" en bloques de código
└── site/                  # salida generada (se borra y regenera en cada build)
```

## Uso

Instalar dependencias (una sola vez):

```bash
pip install -r requirements.txt --break-system-packages
```

Crear un post nuevo:

```bash
python3 new_post.py "Explotando un XXE en un endpoint SOAP" --category writeup --tags xxe,soap,web
```

Esto crea `posts/explotando-un-xxe-en-un-endpoint-soap.md` con el front
matter ya armado. Edítalo, escribe el contenido en Markdown y luego:

```bash
python3 build.py
```

Para previsualizar en local con recarga manual:

```bash
python3 build.py --serve
# abre http://localhost:8000
```

## Front matter de un post

```yaml
---
title: "Título del post"
slug: url-corta-opcional        # si se omite, se genera del título
date: 2026-07-26
category: writeup               # writeup | research | tool | nota
tags: ["ctf", "web"]
author: John
summary: "Resumen de 1-2 líneas, aparece en el índice y como meta description."
---
```

Las categorías tienen colores fijos en `static/css/style.css`
(`.tag-writeup`, `.tag-research`, `.tag-tool`, `.tag-nota`). Para agregar una
categoría nueva, añade su propia clase `.tag-<slug>` con un color del token
system.

## Configuración del sitio

El diccionario `SITE` al inicio de `build.py` controla el título, tagline,
áreas de enfoque y demás textos globales — no hay que tocar las plantillas
para cambiarlos.

## Publicar

`site/` es HTML/CSS/JS estático puro: se puede desplegar tal cual en GitHub
Pages, Netlify, Cloudflare Pages, S3+CloudFront, o cualquier servidor que
sirva archivos estáticos. No requiere backend ni base de datos.
