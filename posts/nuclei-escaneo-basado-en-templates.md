---
title: "Nuclei en la práctica: escaneo de vulnerabilidades basado en templates"
slug: nuclei-escaneo-basado-en-templates
date: 2026-07-23
category: tool
tags: ["nuclei", "recon", "bug-bounty", "automatizacion"]
author: John
summary: "Cómo integro Nuclei en mi flujo de reconocimiento para bug bounty: instalación, templates, y un patrón de uso que evita ruido innecesario contra el objetivo."
---

## Contexto

`Nuclei` (ProjectDiscovery) es un escáner de vulnerabilidades basado en
templates YAML: en vez de un motor cerrado con lógica de detección
hardcodeada, cada firma de vulnerabilidad es un archivo de texto legible,
versionado en un repositorio público que crece con aportes de la comunidad.
Eso lo hace rápido de actualizar y fácil de auditar antes de correrlo contra
un objetivo real.

Como con cualquier herramienta de escaneo activo, solo se usa contra
objetivos donde tienes autorización explícita — un programa de bug bounty
en el que estás inscrito, o infraestructura propia.

## Desarrollo

### Instalación

```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -update-templates
```

Actualizar los templates antes de cada sesión importa: la utilidad real de
Nuclei está en la frescura de sus firmas, no en el binario en sí.

### Un escaneo básico y acotado

```bash
nuclei -u https://objetivo-autorizado.com -t http/exposures/ -t http/misconfiguration/
```

Empezar con categorías específicas (`exposures`, `misconfiguration`) en vez
de `-t /` (todos los templates) reduce el ruido y el tiempo de escaneo, y es
más fácil de justificar dentro de las reglas de rate-limit de un programa.

### Integrarlo con un listado de subdominios

El valor real aparece al combinarlo con otras herramientas de
reconocimiento, formando un pipeline:

```bash
subfinder -d objetivo.com -silent | \
  httpx -silent | \
  nuclei -t http/cves/ -t http/exposed-panels/ -severity medium,high,critical -o hallazgos.txt
```

`httpx` filtra qué subdominios responden por HTTP antes de que Nuclei
gaste tiempo en hosts caídos, y `-severity` limita la salida a lo que de
verdad vale la pena reportar.

### Rate limiting — el ajuste que más importa

```bash
nuclei -u https://objetivo-autorizado.com -t http/cves/ -rate-limit 20 -c 10
```

`-rate-limit` (peticiones por segundo) y `-c` (concurrencia) son los
parámetros que evitan que un escaneo "agresivo por defecto" se convierta en
una queja del equipo de seguridad del objetivo. La mayoría de programas de
bug bounty documentan un límite razonable de peticiones por segundo; vale la
pena respetarlo incluso cuando la herramienta permite ir más rápido.

### Escribir un template propio

Cuando un hallazgo no está cubierto por la comunidad, un template mínimo se
ve así:

```yaml
id: exposed-env-file
info:
  name: Archivo .env expuesto
  severity: high
http:
  - method: GET
    path:
      - "{{BaseURL}}/.env"
    matchers:
      - type: word
        words:
          - "DB_PASSWORD"
        part: body
```

## Conclusión

Nuclei no reemplaza el análisis manual — sigue haciendo falta validar cada
hallazgo antes de reportarlo, porque los falsos positivos existen — pero
como primera pasada sobre un alcance grande, con templates acotados y un
rate limit razonable, encuentra en minutos configuraciones expuestas que
manualmente tomarían horas de revisión.
