# Subdominio epic.fuerz4.com

El sitio queda servido en nano-server por nginx, en `127.0.0.1:8091`. Esa máquina no escucha en los puertos 80 ni 443. `nano.fuerz4.com` entra por el túnel de Cloudflare que ya corre ahí (`cloudflared`, configuración remota del túnel, sin un `config.yml` local).

`epic.fuerz4.com` tiene que usar ese mismo túnel. Un registro A hacia la IP de la máquina no alcanza: el puerto 8091 está atado a localhost.

## Alta del hostname

1. Entrar a [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) → **Networks** → **Tunnels**.
2. Abrir el túnel que ya publica `nano.fuerz4.com`.
3. **Public Hostname** → **Add a public hostname**.
   - Subdomain: `epic`
   - Domain: `fuerz4.com`
   - Path: vacío
   - Type: `HTTP`
   - URL: `localhost:8091`
4. Guardar.

Cloudflare crea el CNAME `epic` apuntando al túnel y lo deja en naranja (proxied). No hace falta un certificado en el servidor: el túnel habla HTTP con nginx en localhost.

En el dominio, **SSL/TLS** tiene que quedar en **Full**. Con el túnel no uses **Flexible**.

## Comprobación

```bash
curl -I https://epic.fuerz4.com
```

Un `200` confirma que el hostname, el túnel y nginx están alineados. Un error de resolución significa que el CNAME todavía no existe. Un `502` significa que el hostname existe pero el túnel no llega a `localhost:8091` (contenedor `epic` caído, u otro puerto).

## Lo que no hay que hacer

- No publicar el puerto 8091 a internet.
- No crear un registro A de `epic` hacia la IP de la máquina mientras el túnel sea la entrada.
- Si ya existe un CNAME o A suelto de `epic`, borrarlo y dejar que el hostname público del túnel lo cree de nuevo.
