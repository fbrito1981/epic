# EPIC Sound System

Sitio de [epic.fuerz4.com](https://epic.fuerz4.com), el sistema de sonido 2.1 de Fuerz4.

Página estática. Tipografía, color `#1A1F25` / `#BA4C1B` y el isotipo salen de NanoServer. Las medidas del gabinete y la placa salen de los planos de EPIC Sound System. Los transductores son Tonhalle W8150, RM5 y T13DR, con los datos publicados por Audifan.

## Vista local

```bash
cd /home/fbrito/Documentos/Projects/epic
python3 -m http.server 8766
```

Abrir `http://127.0.0.1:8766`.

## Deploy

`deploy/deploy.sh` copia el sitio a nano-server, deja nginx en `127.0.0.1:8091` y agrega el servicio `epic` a `docker-compose.yml` si todavía no está. No recrea el resto de los contenedores.

```bash
./deploy/deploy.sh
```

El nombre público no resuelve hasta dar de alta el hostname en el túnel. Los pasos están en [docs/cloudflare.md](docs/cloudflare.md).

El alta del buzón `info@fuerz4.com` y el reenvío están en [docs/correo.md](docs/correo.md).
