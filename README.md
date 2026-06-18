# SAKU Feed — Catálogo Meta/Facebook

Feed XML actualizado para el catálogo de Meta (Facebook/Instagram Shopping) de SAKU Lencería.

## Por qué existe

El feed legacy de Tiendanube (`themes/common/fb_catalog.xml`) se **congeló el 2026-03-25** y dejó de incluir productos nuevos. Meta seguía leyendo ese archivo viejo (735 variantes, sin los productos del Mundial, Victoria, Gloria, etc.).

Este repo genera un feed completo y actualizado desde la API de Tiendanube (1000+ variantes, todos los productos publicados).

## URL del feed (pegar en Meta Commerce Manager)

```
https://raw.githubusercontent.com/LauraSaku/saku-feed/main/fb_catalog.xml
```

## Actualizar manualmente

```bash
python generar_feed.py   # regenera fb_catalog.xml
bash actualizar.sh       # regenera + push a GitHub
```

## Auto-actualización

`actualizar.sh` está pensado para correr cada 6 h vía Task Scheduler de Windows.
