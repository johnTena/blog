---
title: "Antes de tocar un solo endpoint: cómo leo el alcance de un programa de bug bounty"
slug: bug-bounty-alcance
date: 2026-06-28
category: research
tags: ["bug-bounty", "metodologia", "recon"]
author: John
summary: "El paso que más gente se salta al empezar en bug bounty no es técnico: es leer la política del programa completa antes de lanzar la primera petición."
---

## Contexto

Es tentador abrir Burp y empezar a mandar tráfico en cuanto entras a un
programa nuevo. El problema es que "está en el dominio" no es lo mismo que
"está en el alcance", y esa diferencia es la que separa un reporte válido de
una violación de política.

## Desarrollo

### Qué reviso, en orden

1. **Assets in-scope vs out-of-scope.** Muchos programas incluyen
   subdominios de terceros (CDNs, SaaS de soporte, landing pages en
   plataformas externas) que parecen del dominio principal pero están
   explícitamente excluidos.
2. **Tipos de prueba prohibidos.** Casi todos prohíben pruebas de denegación
   de servicio, ingeniería social contra empleados, y acceso a datos de otros
   usuarios más allá de una prueba de concepto mínima.
3. **Cuentas de prueba vs cuentas reales.** Si el programa provee cuentas de
   prueba, úsalas. Probar contra datos de usuarios reales sin necesidad es la
   forma más rápida de que te saquen del programa.
4. **Ventanas de tiempo y rate limits.** Algunos programas piden anunciar
   pruebas de carga o pentesting activo con anticipación.
5. **Reglas de divulgación.** Cuánto tiempo hay que esperar antes de publicar
   un writeup, y si se necesita autorización explícita para hacerlo.

### Una nota sobre reconocimiento pasivo vs activo

Incluso el recon "pasivo" tiene matices. Consultar `crt.sh` o hacer búsquedas
en buscadores no toca la infraestructura del objetivo. Pero herramientas de
enumeración de subdominios que sí generan tráfico activo (fuerza bruta de
DNS, escaneo de puertos) deben evaluarse contra el alcance igual que
cualquier otra prueba.

```bash
# recon pasivo — no toca la infraestructura del objetivo
curl -s "https://crt.sh/?q=%25.ejemplo.com&output=json" | jq -r '.[].name_value' | sort -u
```

## Conclusión

La parte técnica del bug bounty es reemplazable por herramientas y práctica.
La disciplina de leer el alcance completo, cada vez, sin asumir que se parece
al del programa anterior, es lo que evita que un hallazgo legítimo se
convierta en un problema legal.
