#!/usr/bin/env python3
"""
Generador de feed XML para Meta/Facebook Catalog desde la API de Tiendanube.

Resuelve el problema del feed legacy de Tiendanube (themes/common/fb_catalog.xml)
que se congelo el 2026-03-25 y dejo de incluir productos nuevos.

Este script regenera el feed completo con TODOS los productos publicados
y hace push al repo, para que Meta lo descargue actualizado.

Uso: python generar_feed.py
"""
import urllib.request
import json
import re
import html
import time
import os
from xml.sax.saxutils import escape

# Config (token de solo lectura de la tienda SAKU)
TOKEN = os.environ.get("TN_ACCESS_TOKEN", "7ad679ec70856470d9322d8439cb3a2f174b7c64")
STORE = os.environ.get("TN_STORE_ID", "1382908")
UA = "SAKU-Feed-Generator (soylauramallo@gmail.com)"
OUT_FILE = os.path.join(os.path.dirname(__file__), "fb_catalog.xml")


def api_get(url):
    req = urllib.request.Request(
        url, headers={"Authentication": f"bearer {TOKEN}", "User-Agent": UA}
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def fetch_all_products():
    allp = []
    page = 1
    while True:
        url = f"https://api.tiendanube.com/v1/{STORE}/products?published=true&per_page=200&page={page}"
        data = api_get(url)
        if not data:
            break
        allp.extend(data)
        if len(data) < 200:
            break
        page += 1
        time.sleep(0.3)
    return allp


def txt(v):
    if isinstance(v, dict):
        return v.get("es") or next(iter(v.values()), "")
    return v or ""


def clean(s):
    s = re.sub(r"<[^>]+>", "", str(s))
    s = html.unescape(s)
    return escape(s).strip()


def build_feed(prods):
    items = []
    for p in prods:
        pid = p["id"]
        name = txt(p["name"])
        desc = clean(txt(p.get("description", "")) or name)[:5000] or clean(name)
        base_link = txt(p.get("canonical_url")) or \
            f"https://www.sakulenceria.com/productos/{txt(p.get('handle'))}/"
        imgs = p.get("images", [])
        img_by_id = {im["id"]: im["src"] for im in imgs}
        main_img = imgs[0]["src"] if imgs else ""
        addl = [im["src"] for im in imgs[1:11]]
        for v in p.get("variants", []):
            vid = v["id"]
            vals = [txt(x) for x in v.get("values", [])]
            title = f"{name} ({', '.join(vals)})" if vals else name
            stock = v.get("stock")
            avail = "in stock" if (stock is None or stock > 0) else "out of stock"
            price = v.get("promotional_price") or v.get("price") or "0"
            price = f"{float(price):.2f} ARS"
            weight = float(v.get("weight") or 0.1)
            vimg = img_by_id.get(v.get("image_id")) or main_img
            link = f"{base_link}?variant={vid}"
            addl_xml = "".join(
                f"\n      <g:additional_image_link>{escape(a)}</g:additional_image_link>"
                for a in addl
            )
            items.append(
                f"""    <item>
      <g:id>{vid}</g:id>
      <g:item_group_id>{pid}</g:item_group_id>
      <g:title>{clean(title)}</g:title>
      <g:description>{desc}</g:description>
      <g:link>{escape(link)}</g:link>
      <g:image_link>{escape(vimg)}</g:image_link>
      <g:condition>new</g:condition>
      <g:availability>{avail}</g:availability>
      <g:price>{price}</g:price>
      <g:shipping_weight>{weight:.4f} kg</g:shipping_weight>
      <g:brand>Sakú</g:brand>{addl_xml}
    </item>"""
            )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
  <channel>
    <title>SAKU Lencería</title>
    <link>https://www.sakulenceria.com</link>
    <description>Catálogo SAKU Lencería</description>
{chr(10).join(items)}
  </channel>
</rss>"""


def main():
    prods = fetch_all_products()
    feed = build_feed(prods)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(feed)
    n_items = feed.count("<item>")
    print(f"Feed generado: {OUT_FILE} | {len(prods)} productos | {n_items} variantes")


if __name__ == "__main__":
    main()
