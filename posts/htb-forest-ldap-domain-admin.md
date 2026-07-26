---
title: "HTB Forest: de enumeración LDAP anónima a Domain Admin"
slug: htb-forest-ldap-domain-admin
date: 2026-06-15
category: writeup
tags: ["htb", "active-directory", "ldap", "ctf"]
author: John
summary: "Writeup de la máquina Forest de HackTheBox: enumeración anónima de LDAP, abuso de un grupo delegado y escalada final vía DCSync."
summary_short: "Enumeración LDAP + abuso de delegación + DCSync."
---

## Contexto

`Forest` es una máquina educativa de Active Directory en HackTheBox, pensada
para practicar el flujo típico de reconocimiento y escalada en un dominio de
Windows mal configurado. Todo lo aquí descrito ocurre dentro del entorno
autorizado de HTB.

## Desarrollo

### Reconocimiento inicial

```bash
nmap -p- --min-rate 5000 -sV 10.10.10.161 -oA forest_full
```

Los puertos abiertos (`53`, `88`, `389`, `445`, `3268`) apuntan de inmediato
a un controlador de dominio: DNS, Kerberos, LDAP y SMB juntos son la huella
clásica de un DC de Active Directory.

### Enumeración anónima de LDAP

Muchos controladores de dominio permiten *binds* anónimos de solo lectura
por configuración heredada:

```bash
ldapsearch -x -H ldap://10.10.10.161 -b "DC=htb,DC=local" \
  "(objectClass=user)" sAMAccountName | grep sAMAccountName
```

Esto entrega la lista completa de usuarios del dominio sin credenciales,
suficiente para armar un ataque de `AS-REP Roasting` contra las cuentas que
tienen deshabilitada la preautenticación de Kerberos.

```bash
impacket-GetNPUsers htb.local/ -usersfile usuarios.txt -no-pass -dc-ip 10.10.10.161
```

Una de las cuentas devuelve un hash `AS-REP` crackeable, lo que da el primer
punto de apoyo dentro del dominio con una cuenta de bajo privilegio.

### Del usuario inicial a un grupo con delegación

Con esas credenciales, `BloodHound` mapea las relaciones del dominio:

```bash
bloodhound-python -u svc_user -p '********' -d htb.local -ns 10.10.10.161 -c All
```

El grafo muestra que la cuenta pertenece, de forma indirecta, a
`Exchange Windows Permissions`, un grupo que en instalaciones por defecto de
Exchange termina con `WriteDacl` sobre el objeto del dominio. Eso permite
otorgarse a uno mismo derechos de replicación (`DS-Replication-Get-Changes` y
`DS-Replication-Get-Changes-All`).

### Escalada final: DCSync

```bash
impacket-secretsdump -just-dc htb.local/svc_user:'********'@10.10.10.161
```

Con esos dos derechos de replicación otorgados, `secretsdump` puede simular
a un controlador de dominio pidiendo una sincronización de contraseñas —
el mismo mecanismo que usan los DC reales entre sí — y extraer los hashes
NTLM de todo el dominio, incluido `Administrator`.

## Conclusión

La cadena completa —bind anónimo → AS-REP Roasting → pertenencia heredada a
un grupo con `WriteDacl` → DCSync— es un recordatorio de que en Active
Directory casi ningún hallazgo individual es crítico por sí solo. Lo que
convierte una mala configuración menor en compromiso total del dominio es la
cadena de relaciones entre objetos, que es exactamente lo que herramientas
como BloodHound están diseñadas para exponer.
