# dist/

Aquí van los 26 RPM de Asterisk 20.18.0 para Issabel 5 (`asterisk20-*-20.18.0-1.el8.x86_64.rpm`, 7,6 MB en total) y `SHA256SUMS`.

Los `.rpm` **no se versionan en git** (son binarios): se publican como archivos de una *Release* del repositorio, o se construyen. También puedes construirlos tú con `build/00_dependencias.sh` y `build/01_construir_rpm.sh`, que los dejan aquí.

Antes de instalar, verifica siempre:

```bash
sha256sum -c SHA256SUMS
```
