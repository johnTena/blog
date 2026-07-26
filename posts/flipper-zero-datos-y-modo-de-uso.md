---
title: "Flipper Zero: qué es realmente y para qué lo uso"
slug: flipper-zero-datos-y-modo-de-uso
date: 2026-07-21
category: nota
tags: ["flipper-zero", "rf", "nfc", "hardware"]
author: John
summary: "Datos curiosos y casos de uso reales del Flipper Zero, más allá del hype de redes sociales: qué protocolos lee, qué no puede hacer, y cómo lo integro en pruebas autorizadas."
---

## Contexto

El Flipper Zero se hizo viral como "la navaja suiza del hacker", pero buena
parte de lo que circula en redes exagera sus capacidades reales. Es, en el
fondo, una plataforma de pruebas de radiofrecuencia y protocolos
inalámbricos de corto alcance con una interfaz muy accesible — no es un
dispositivo mágico que "hackea" cualquier cosa con solo apuntarlo.

## Datos curiosos

- **El nombre viene de un delfín.** El "Flipper" de la mascota (un delfín
  ciberpunk) referencia la idea de un compañero curioso y juguetón — de ahí
  el tono desenfadado de toda la interfaz, muy distinto al de una
  herramienta de pentest tradicional.
- **Corre un firmware abierto.** El firmware oficial es de código abierto,
  lo que dio pie a forks de la comunidad (como Unleashed o RogueMaster) que
  añaden funciones o remueven límites regulatorios — algo a tener en cuenta,
  porque cambia qué frecuencias transmite y con qué restricciones legales.
- **No clona todo.** Tarjetas NFC/RFID modernas con cifrado (como la mayoría
  de tarjetas bancarias o pasaportes con chip) no se clonan con un Flipper:
  el dispositivo lee y muestra los datos, pero no rompe el cifrado
  subyacente. Lo que sí puede leer y a veces reproducir son sistemas más
  antiguos o mal configurados (EM4100, Mifare Classic con claves por
  defecto, mandos de garage sin rolling code).
- **El chip Sub-GHz es el corazón real del dispositivo.** Más que el NFC, la
  capacidad de capturar y analizar señales en 300-928 MHz (mandos de
  cocheras, sensores IoT, algunos controles remotos) es donde más se nota la
  diferencia frente a un teléfono normal.

## Modo de uso — casos donde realmente aporta

### Auditar tus propios controles de acceso

```
Menú → 125 kHz RFID → Leer
```

Leer una credencial propia de acceso (una pulsera de gimnasio, una tarjeta
de oficina que administras) para verificar si usa un esquema vulnerable
(EM4100 sin cifrado) es el caso de uso más directo: te dice si tu propio
control de acceso es tan seguro como crees.

### Analizar el propio mando del garage

```
Menú → Sub-GHz → Leer → (accionar el mando propio)
```

Si el mando no implementa `rolling code` (código que cambia en cada uso),
el Flipper captura una señal fija y puede reproducirla. Es una forma
práctica de descubrir, sobre tu propio equipo, si vale la pena actualizarlo
a un receptor más moderno.

### Depurar protocolos IR en desarrollo de IoT

```
Menú → Infrared → Aprender señal
```

Para quien desarrolla o da soporte a hardware con control remoto IR, capturar
y reproducir señales acelera muchísimo la depuración comparado con probar
mando por mando.

### Lo que NO hace (y por qué importa saberlo)

- No clona tarjetas bancarias ni pasaportes (cifradas y con protecciones
  anti-clonado).
- No "hackea" WiFi por sí solo — necesita un módulo adicional (como el
  DevBoard con ESP32) que ni siquiera viene incluido de fábrica.
- No transmite legalmente en cualquier frecuencia en cualquier país: las
  bandas Sub-GHz permitidas varían por región, y el firmware oficial
  respeta esas restricciones regionales por defecto.

## Conclusión

El valor real del Flipper Zero está en hacer accesible algo que antes
requería SDRs, lectores RFID dedicados y bastante conocimiento de
radiofrecuencia por separado — todo en una interfaz que cabe en un bolsillo.
Pero como con cualquier herramienta de este tipo, su uso legítimo se limita
a equipos propios o pruebas explícitamente autorizadas: leer o reproducir
credenciales, mandos o tarjetas de terceros sin permiso es ilegal
independientemente de qué tan trivial lo haga el dispositivo.
