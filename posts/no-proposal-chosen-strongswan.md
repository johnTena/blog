---
title: "NO_PROPOSAL_CHOSEN: cazando el mismatch de propuestas IKE en strongSwan"
slug: no-proposal-chosen-strongswan
date: 2026-07-18
category: writeup
tags: ["ipsec", "strongswan", "vpn", "networking"]
author: John
summary: "Diagnóstico paso a paso de un túnel site-to-site que muere en IKE_SA_INIT, y el checklist que uso para no volver a perder una tarde con esto."
---

## Contexto

Un túnel `IKEv2` entre mi gateway y un peer remoto se quedaba pegado en `CONNECTING`.
Los paquetes de `IKE_SA_INIT` salían, pero el peer respondía con un rechazo limpio:

```
charon: 08[IKE] received NO_PROPOSAL_CHOSEN notify error
charon: 08[IKE] establishing IKE_SA failed, peer not authenticated
```

`NO_PROPOSAL_CHOSEN` casi siempre significa lo mismo: **ambos lados están vivos y
se están hablando**, pero ninguna combinación de cifrado/hash/grupo DH que ofrece
un lado coincide con lo que el otro lado acepta. No es un problema de firewall
(eso daría timeout, no un notify), y no es un problema de PSK (eso falla más
adelante, en `IKE_AUTH`).

## Desarrollo

### 1. Confirmar que el fallo es de fase 1, no de fase 2

```bash
sudo journalctl -u strongswan -f | grep -E "IKE_SA_INIT|NO_PROPOSAL|AUTH"
```

Si el log muere justo después de `generating IKE_SA_INIT request`, el problema
vive en la sección `ike=` de la conexión, no en `esp=`.

### 2. Revisar la propuesta que realmente se está enviando

```bash
sudo swanctl --log | grep -A3 "sending proposals"
```

Compara contra lo que documentación o equipo remoto declaran soportar. Un caso
típico: yo tenía `ike=aes256-sha256-modp2048!` pero el otro extremo era un
equipo legado que solo aceptaba `sha1` en fase 1.

### 3. Ampliar la propuesta en vez de adivinar

En lugar de adivinar una sola combinación, listo varias con `,` y dejo que
strongSwan negocie:

```
conn cliente-pdv
    keyexchange=ikev2
    left=%defaultroute
    leftid=203.0.113.10
    right=198.51.100.20
    ike=aes256-sha256-modp2048,aes256-sha1-modp2048,aes128-sha1-modp1024!
    esp=aes256-sha256,aes256-sha1!
    authby=psk
    forceencaps=yes
    keyingtries=%forever
    dpdaction=restart
    closeaction=restart
```

El `!` al final de cada línea es importante: le dice a strongSwan que **no**
proponga combinaciones fuera de esa lista aunque tenga otras disponibles por
defecto, lo cual ayuda a que el log de negociación sea legible.

### 4. Si sigue fallando, probar IKEv1

Algunos equipos (sobre todo appliances más viejos) no implementan bien
IKEv2. Cambiar `keyexchange=ikev2` por `keyexchange=ikev1` y, si aplica,
`aggressive=yes`, resuelve una fracción sorprendente de estos casos.

## Conclusión

`NO_PROPOSAL_CHOSEN` es información, no un error genérico: te está diciendo
que la sesión sí se estableció a nivel de red y que el problema es
puramente de configuración criptográfica. El checklist que me ahorra tiempo:

1. Confirmar en qué fase muere (`IKE_SA_INIT` vs `IKE_AUTH`).
2. Loggear la propuesta real enviada, no la que crees que enviaste.
3. Ampliar la lista de cifrados antes de asumir que el peer está mal configurado.
4. IKEv1 como último recurso para equipos legados.
