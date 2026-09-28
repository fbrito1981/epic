# Correo info@fuerz4.com

Consulta hecha el 28 de septiembre de 2026.

## Cómo está el dominio hoy

- Los NS de `fuerz4.com` son de Cloudflare (`jobs.ns.cloudflare.com` y `holly.ns.cloudflare.com`).
- No hay registros MX. Un mensaje a `info@fuerz4.com` hoy no tiene dónde entregarse.
- Hay un TXT de verificación de Brevo. No apareció un SPF ni un DKIM en esa consulta.

Brevo, con ese TXT, sirve para **enviar**. No recibe el buzón. Para leer `info@` hace falta un MX.

## Recibir y reenviar

La vía más corta es **Cloudflare Email Routing**. Es gratis, el DNS ya está en Cloudflare y no hay un MX anterior que pisar. El destino es `fbrito@gmail.com`.

1. En el dashboard, menú izquierdo → **Cómputo** → **Email Service** → **Email Routing**. Atajo: [Email Routing](https://dash.cloudflare.com/?to=/:account/email-service/routing).
2. **Onboard Domain** → `fuerz4.com`. Cloudflare agrega los MX, el SPF y un DKIM de reenvío. No borra el TXT `brevo-code`.
3. En DNS, el SPF tiene que quedar así (sumá Brevo si el asistente escribió solo el de Cloudflare):

   ```text
   v=spf1 include:_spf.mx.cloudflare.net include:spf.brevo.com ~all
   ```

4. **Destination addresses** → `fbrito@gmail.com`. Llega un correo de confirmación. Hasta abrirlo y tocar **Verify email address**, el reenvío no sale.
5. En el dominio, **Routing rules** → **Create routing rule**:
   - Email pattern: `info`
   - Dominio: `fuerz4.com`
   - Action: Send to an email
   - Destination: `fbrito@gmail.com`
6. Probar desde otra cuenta (no desde `fbrito@gmail.com`) escribiendo a `info@fuerz4.com`.

Con eso, lo que escriban a `info@fuerz4.com` llega a tu correo. Email Routing no guarda una copia propia: si la regla está activa, el mensaje se entrega en el destino.

## Contestar como info@

El reenvío solo cubre la entrada. La respuesta, si se manda desde Gmail, sale como `fbrito@gmail.com`.

Para que la respuesta salga de `info@fuerz4.com`:

1. En Brevo, dar de alta el remitente `info@fuerz4.com` y publicar el CNAME de DKIM que indique el panel. El dominio ya tiene el TXT de verificación.
2. En el cliente de correo, agregar "enviar como" `info@fuerz4.com` usando el SMTP de Brevo (host, puerto, usuario y clave SMTP del panel de Brevo).
3. Al contestar un mensaje reenviado, elegir ese remitente.

Otra opción es responder desde `fbrito@gmail.com`. Quien escribió ve esa dirección, no `info@`.

No hace falta Google Workspace ni otro hosting de buzones si el objetivo es recibir en la casilla que ya usás y, si hace falta, contestar por el SMTP de Brevo.
