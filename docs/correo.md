# Correo info@fuerz4.com

Consulta hecha el 28 de septiembre de 2026.

## Cómo está el dominio hoy

- Los NS de `fuerz4.com` son de Cloudflare (`jobs.ns.cloudflare.com` y `holly.ns.cloudflare.com`).
- No hay registros MX. Un mensaje a `info@fuerz4.com` hoy no tiene dónde entregarse.
- Hay un TXT de verificación de Brevo. No apareció un SPF ni un DKIM en esa consulta.

Brevo, con ese TXT, sirve para **enviar**. No recibe el buzón. Para leer `info@` hace falta un MX.

## Recibir y reenviar

La vía más corta es **Cloudflare Email Routing**. Es gratis, el DNS ya está en Cloudflare y no hay un MX anterior que pisar. El destino de reenvío usado abajo es `fernando.brito@iph.digital` (la dirección del `git config` de esta máquina). Si el buzón real es otro, se cambia solo ese destino.

1. [dash.cloudflare.com](https://dash.cloudflare.com) → dominio `fuerz4.com` → **Email** → **Email Routing**.
2. Activar Email Routing y aceptar los registros que propone (MX y el SPF de Cloudflare).
3. Antes de guardar el SPF, conservar a Brevo. El registro tiene que incluir los dos:

   ```text
   v=spf1 include:_spf.mx.cloudflare.net include:spf.brevo.com ~all
   ```

   Si el asistente escribe solo el de Cloudflare, editar el TXT y sumar `include:spf.brevo.com`.
4. **Destination addresses** → agregar `fernando.brito@iph.digital`. Llega un correo de confirmación a esa casilla. Hasta aceptarlo, el reenvío no sale.
5. **Routing rules** → Custom address:
   - Custom address: `info`
   - Action: Forward to `fernando.brito@iph.digital`
6. Enviar una prueba desde una cuenta que no sea esa, hacia `info@fuerz4.com`, y confirmar que aparece en la bandeja de `fernando.brito@iph.digital`.

Con eso, lo que escriban a `info@fuerz4.com` llega a tu correo. Email Routing no guarda una copia propia: si la regla está activa, el mensaje se entrega en el destino.

## Contestar como info@

El reenvío solo cubre la entrada. La respuesta, si se manda desde el cliente habitual, sale como `fernando.brito@iph.digital`.

Para que la respuesta salga de `info@fuerz4.com`:

1. En Brevo, dar de alta el remitente `info@fuerz4.com` y publicar el CNAME de DKIM que indique el panel. El dominio ya tiene el TXT de verificación.
2. En el cliente de correo, agregar "enviar como" `info@fuerz4.com` usando el SMTP de Brevo (host, puerto, usuario y clave SMTP del panel de Brevo).
3. Al contestar un mensaje reenviado, elegir ese remitente.

Otra opción es responder desde `fernando.brito@iph.digital` y listo. Quien escribió ve tu dirección personal, no `info@`.

No hace falta Google Workspace ni otro hosting de buzones si el objetivo es recibir en la casilla que ya usás y, si hace falta, contestar por el SMTP de Brevo.
