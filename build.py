#!/usr/bin/env python3
"""Generador estático del sitio MERIDIANO · Casa Relojera."""
import json, os, re, math, html, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://meridiano-relojeria.co"  # dominio de referencia para SEO/sitemap
GITHUB_PAGES_BASE = "https://daniel666674.github.io/relojes/"
GA4_ID = "G-XXXXXXXXXX"  # ← reemplazar por el ID real de Google Analytics 4
WHATSAPP = "573001234567"

data = json.load(open(os.path.join(ROOT, "data/products.json"), encoding="utf-8"))
COLLECTIONS = data["collections"]
PRODUCTS = data["products"]
COL_ORDER = ["rolex", "patek", "cartier"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

for p in PRODUCTS:
    p["img_card"] = f"assets/img/products/{p['slug']}-card.webp"
    p["img_lg"] = f"assets/img/products/{p['slug']}-lg.webp"

by_col = {c: [p for p in PRODUCTS if p["collection"] == c] for c in COL_ORDER}
PER_PAGE = 9

def fmt_cop(n):
    return "$ " + f"{n:,}".replace(",", ".") + " COP"

def esc(s):
    return html.escape(str(s), quote=True)

GA_SNIPPET = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{ dataLayer.push(arguments); }}
      gtag('js', new Date());
      gtag('config', '{GA4_ID}', {{ anonymize_ip: true }});
    </script>"""

def base_head(title, desc, canonical, extra_ld="", ogimg="assets/img/og-cover.jpg"):
    return f"""<!doctype html>
<html lang="es-CO">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="{GITHUB_PAGES_BASE}">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="geo.region" content="CO">
<meta name="geo.placename" content="Colombia">
<meta name="language" content="es-CO">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">

<meta property="og:type" content="website">
<meta property="og:site_name" content="MERIDIANO · Casa Relojera">
<meta property="og:locale" content="es_CO">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{canonical}">
<meta property="og:image" content="{SITE}/{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/{ogimg}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Marcellus&family=Cormorant+Garamond:ital@1&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
{GA_SNIPPET}
{extra_ld}
</head>
"""

WA_ICON = """<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><path d="M16.02 3C9.4 3 4 8.4 4 15.02c0 2.23.62 4.31 1.7 6.1L4 29l8.06-1.66a12 12 0 0 0 3.96.68h.01c6.62 0 12.01-5.4 12.01-12.02C28 8.4 22.63 3 16.02 3zm7.03 17.13c-.3.83-1.72 1.6-2.37 1.68-.62.08-1.34.11-2.16-.14-.5-.15-1.14-.36-1.96-.7-3.46-1.5-5.72-4.98-5.9-5.21-.17-.24-1.4-1.86-1.4-3.55 0-1.69.9-2.52 1.21-2.86.32-.34.68-.42.9-.42.23 0 .45 0 .65.01.21.01.49-.08.76.58.3.72.99 2.5 1.08 2.68.09.18.15.4.03.63-.12.24-.18.39-.36.6-.18.2-.38.45-.54.61-.18.18-.37.37-.16.72.21.35.94 1.55 2.02 2.51 1.39 1.24 2.56 1.62 2.92 1.8.35.18.56.15.77-.09.21-.24.87-1.01 1.1-1.36.24-.35.47-.29.79-.17.32.12 2.06.97 2.41 1.15.35.18.59.26.68.41.09.15.09.85-.2 1.68z"/></svg>"""
CART_ICON = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4h2l2.4 12.4a2 2 0 0 0 2 1.6h7.2a2 2 0 0 0 2-1.6L20 8H6"/><circle cx="9.5" cy="20" r="1.2" fill="currentColor" stroke="none"/><circle cx="17" cy="20" r="1.2" fill="currentColor" stroke="none"/></svg>"""

NAV = [("index.html", "Fundación"), ("vitrinas.html", "Vitrinas"), ("manifiesto.html", "Manifiesto"), ("contacto.html", "Contacto")]

def rail(active="index.html"):
    items = "".join(f'<a href="{h}" class="{"active" if h==active else ""}">{t}</a>' for h, t in NAV)
    return f"""
<aside class="rail">
  <a href="index.html" class="rail-monogram">M</a>
  <nav class="rail-nav">{items}</nav>
  <a href="#" class="rail-cart js-open-cart" aria-label="Ver vitrina personal (carrito)">
    {CART_ICON}
    <span class="js-cart-count is-empty">0</span>
  </a>
</aside>
<div class="topbar">
  <a href="index.html" class="brand">MERIDI<em>A</em>NO</a>
  <nav>
    <a href="index.html" class="{"active" if active=="index.html" else ""}">Fundación</a>
    <a href="vitrinas.html" class="{"active" if active=="vitrinas.html" else ""}">Vitrinas</a>
    <a href="manifiesto.html" class="{"active" if active=="manifiesto.html" else ""}">Manifiesto</a>
    <a href="contacto.html" class="{"active" if active=="contacto.html" else ""}">Contacto</a>
    <a href="#" class="js-open-cart rail-cart" aria-label="Carrito">{CART_ICON}<span class="js-cart-count is-empty">0</span></a>
  </nav>
</div>"""

def cart_drawer():
    return """
<div id="cartVeil" class="js-close-cart"></div>
<aside id="cartDrawer" aria-label="Vitrina personal / carrito">
  <div class="cart-head">
    <h2>Su vitrina personal</h2>
    <button class="js-close-cart" aria-label="Cerrar">&times;</button>
  </div>
  <div id="cartItems"></div>
  <div class="cart-foot">
    <div class="cart-total-row"><span>Total estimado</span><strong id="cartTotal">$ 0 COP</strong></div>
    <button id="cartCheckout" class="btn solid">Confirmar por WhatsApp</button>
    <p class="hint">Precios de referencia. Confirmamos disponibilidad y entrega por WhatsApp antes de cerrar el pedido.</p>
  </div>
</aside>"""

def wa_float():
    return f'<a class="wa-float js-wa" data-msg="Hola MERIDIANO · Casa Relojera 🕰️, quisiera más información sobre sus piezas." aria-label="Escribir por WhatsApp">{WA_ICON}</a>'

def footer():
    cols_links = "".join(f'<a href="vitrinas.html?col={c}">{COLLECTIONS[c]["label"]}</a>' for c in COL_ORDER)
    return f"""
<footer>
  <div class="wrap foot-grid">
    <div>
      <div class="foot-brand">MERIDIANO<small>Casa Relojera — Bogotá, Colombia</small></div>
    </div>
    <nav class="foot-nav">{cols_links}</nav>
    <nav class="foot-nav">
      <a href="vitrinas.html">Todas las vitrinas</a>
      <a href="manifiesto.html">Manifiesto</a>
      <a href="contacto.html">Contacto</a>
      <a href="#" class="js-wa" data-msg="Hola MERIDIANO, quisiera hacer una consulta.">WhatsApp directo</a>
    </nav>
    <div class="foot-legal">
      © 2026 MERIDIANO · Casa Relojera. Piezas de alta réplica elaboradas con estándares premium; no están afiliadas ni son productos oficiales de las manufacturas que inspiran cada diseño.<br>
      Bogotá, Colombia · Entregas a nivel nacional · Atención por WhatsApp.
    </div>
  </div>
</footer>
<script src="assets/js/store.js" defer></script>
"""

def product_card(p, i=0):
    payload = esc(json.dumps({"id": p["id"], "name": p["name"], "price": p["price"], "img": p["img_card"]}, ensure_ascii=False))
    return f"""
<article class="card reveal" style="transition-delay:{(i%3)*90}ms">
  <a href="vitrinas/{p['slug']}.html" class="card-frame">
    <img src="{p['img_card']}" alt="{esc(p['name'])} — reloj {esc(p['dial'])}, {esc(p['material'])}" loading="lazy" width="900" height="900">
  </a>
  <button class="card-add" data-add='{payload}' aria-label="Añadir {esc(p['name'])} a la vitrina personal">+</button>
  <div class="card-body">
    <p class="card-kicker">{COLLECTIONS[p['collection']]['label']}</p>
    <h3 class="card-name"><a href="vitrinas/{p['slug']}.html">{esc(p['name'])}</a></h3>
    <p class="card-dial">Esfera {esc(p['dial'])} · {esc(p['size'])}</p>
    <p class="card-price">{fmt_cop(p['price'])}</p>
  </div>
</article>"""

# ============================================================ INDEX
def build_index():
    feat = [p for p in PRODUCTS if p.get("featured")][:6]
    ticker_words = ["Rolex · Referencias icónicas", "Patek Philippe · Alta complicación", "Cartier · Distinción parisina", "Envíos a toda Colombia", "Garantía de 6 meses", "Pago contraentrega en Bogotá"]
    ticker = "".join(f"<span>{w}</span>" for w in ticker_words) * 2

    col_rows = ""
    for i, c in enumerate(COL_ORDER):
        items = by_col[c]
        thumb = items[0]["img_card"]
        col_rows += f"""
    <a href="vitrinas.html?col={c}" class="col-row reveal" style="transition-delay:{i*60}ms">
      <span class="idx">{ROMAN[i]}</span>
      <span>
        <h3>{COLLECTIONS[c]['label']}</h3>
        <span class="tag">{COLLECTIONS[c]['tagline']}</span>
      </span>
      <span class="count">{len(items):02d} piezas</span>
      <span class="thumb"><img src="{thumb}" alt="{COLLECTIONS[c]['label']}" loading="lazy"></span>
    </a>"""

    cards = "".join(product_card(p, i) for i, p in enumerate(feat))

    ld = f"""<script type="application/ld+json">
{json.dumps({
  "@context": "https://schema.org",
  "@type": "JewelryStore",
  "name": "MERIDIANO · Casa Relojera",
  "url": SITE,
  "image": f"{SITE}/assets/img/og-cover.jpg",
  "description": "Casa relojera colombiana especializada en piezas de alta réplica premium inspiradas en Rolex, Patek Philippe y Cartier.",
  "priceRange": "$$$",
  "address": {"@type": "PostalAddress", "addressLocality": "Bogotá", "addressCountry": "CO"},
  "areaServed": "CO",
  "sameAs": []
}, ensure_ascii=False)}
</script>
<script type="application/ld+json">
{json.dumps({
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "¿Qué es una pieza de alta réplica MERIDIANO?", "acceptedAnswer": {"@type": "Answer", "text": "Es un reloj fabricado con estándares premium de materiales y ensamblaje que reproduce fielmente el diseño de las grandes manufacturas, a una fracción del precio, sin ser un producto oficial de dichas marcas."}},
    {"@type": "Question", "name": "¿Hacen envíos a toda Colombia?", "acceptedAnswer": {"@type": "Answer", "text": "Sí, despachamos a todas las ciudades de Colombia. En Bogotá ofrecemos entrega personal con pago contraentrega."}},
    {"@type": "Question", "name": "¿Cómo confirmo un pedido?", "acceptedAnswer": {"@type": "Answer", "text": "Agregue las piezas a su vitrina personal y confirme el pedido por WhatsApp; un asesor verifica disponibilidad y coordina el envío o la entrega."}}
  ]
}, ensure_ascii=False)}
</script>"""

    body = f"""<body>
{rail("index.html")}
<main class="page">
  <section class="hero wrap">
    <p class="kicker">Casa relojera colombiana · Fundada para el detalle</p>
    <h1 class="hero-title">
      <span class="row">MERID<span class="hero-dial"><img src="assets/img/products/{PRODUCTS[10]['slug']}-card.webp" alt=""></span>ANO</span>
    </h1>
    <div class="hero-sub">
      <p>Cincuenta y nueve piezas: Rolex, Patek Philippe y Cartier. Una sola convicción — el lujo se mide en detalle, no en ruido.</p>
      <a href="vitrinas.html" class="btn solid">Explorar las vitrinas</a>
      <a href="#" class="btn js-wa" data-msg="Hola MERIDIANO, quisiera asesoría para elegir una pieza.">Asesoría por WhatsApp</a>
    </div>
    <div class="hero-meta"><span>N.º 001–059</span></div>
  </section>

  <div class="ticker"><div class="ticker-track">{ticker}</div></div>

  <section class="section wrap col-index">
    <div class="sec-head">
      <h2><span class="num">I.</span>Las tres marcas</h2>
      <p class="lede" style="color:var(--muted);max-width:360px">Rolex, Patek Philippe, Cartier — las tres manufacturas que definen el lujo suizo y parisino en cada época.</p>
    </div>
    {col_rows}
  </section>

  <section class="section wrap">
    <div class="sec-head">
      <h2><span class="num">II.</span>Piezas destacadas</h2>
      <a href="vitrinas.html" class="btn">Ver todas</a>
    </div>
    <div class="grid">{cards}</div>
  </section>

  <section class="section wrap manifest reveal">
    <div class="visual"><img src="assets/img/products/{PRODUCTS[45]['slug']}-lg.webp" alt="Detalle de manufactura MERIDIANO" loading="lazy"></div>
    <div>
      <p class="kicker">Manifiesto</p>
      <blockquote>&ldquo;No vendemos relojes. Vendemos el instante exacto en que alguien nota el detalle.&rdquo;</blockquote>
      <p class="body">Cada pieza pasa por control visual y mecánico antes de salir de nuestro taller en Bogotá. Elegimos acero premium, cristales resistentes y movimientos silenciosos porque el lujo, para nosotros, es una decisión de ingeniería antes que de mercadeo.</p>
      <a href="manifiesto.html" class="btn" style="margin-top:26px">Leer el manifiesto completo</a>
    </div>
  </section>
</main>
{cart_drawer()}
{wa_float()}
{footer()}
</body>
</html>"""
    write("index.html", base_head(
        "MERIDIANO · Casa Relojera — Relojes de alta réplica premium en Colombia",
        "Casa relojera colombiana con 59 piezas de alta réplica premium: Rolex, Patek Philippe y Cartier. Envíos a toda Colombia.",
        "/") + body)

# ============================================================ VITRINAS (catálogo paginado)
def build_vitrinas():
    total_pages = math.ceil(len(PRODUCTS) / PER_PAGE)
    chips = '<a href="vitrinas.html" class="chip active" data-col="todas">Todas</a>' + "".join(
        f'<a href="vitrinas.html?col={c}" class="chip" data-col="{c}">{COLLECTIONS[c]["label"]}</a>' for c in COL_ORDER)

    for page in range(1, total_pages + 1):
        chunk = PRODUCTS[(page-1)*PER_PAGE: page*PER_PAGE]
        cards = "".join(product_card(p, i) for i, p in enumerate(chunk))

        plaques = ""
        prev = page - 1 if page > 1 else None
        nxt = page + 1 if page < total_pages else None
        prev_href = "vitrinas.html" if prev == 1 else (f"vitrinas/pagina-{prev}.html" if prev else "#")
        next_href = f"vitrinas/pagina-{nxt}.html" if nxt else "#"
        plaques += f'<a href="{prev_href}" class="plaque plaque-arrow{" is-off" if not prev else ""}" aria-label="Vitrina anterior">‹</a>'
        for n in range(1, total_pages + 1):
            href = "vitrinas.html" if n == 1 else f"vitrinas/pagina-{n}.html"
            plaques += f'<a href="{href}" class="plaque{" current" if n==page else ""}">{ROMAN[n-1] if n<=10 else n}</a>'
        plaques += f'<a href="{next_href}" class="plaque plaque-arrow{" is-off" if not nxt else ""}" aria-label="Vitrina siguiente">›</a>'

        canonical = "/vitrinas.html" if page == 1 else f"/vitrinas/pagina-{page}.html"
        title = "Vitrinas — Catálogo completo" if page == 1 else f"Vitrinas — Página {page} de {total_pages}"
        body = f"""<body>
{rail("vitrinas.html")}
<main class="page">
  <section class="wrap vitrina-head reveal">
    <span class="big-roman">{ROMAN[(page-1)%10]}</span>
    <p class="kicker">Catálogo · Placa {page:02d} de {total_pages:02d}</p>
    <h1>Las vitrinas</h1>
    <p class="lede">Cincuenta y nueve piezas de Rolex, Patek Philippe y Cartier. Sin desplazamiento infinito: cada vitrina es una placa numerada, como en una boutique real.</p>
    <div class="chips">{chips}</div>
  </section>

  <section class="wrap section" style="padding-top:0">
    <div class="grid">{cards}</div>
    <nav class="plaques" aria-label="Paginación de vitrinas">{plaques}</nav>
    <p class="plaques-label">Placa {page:02d} / {total_pages:02d} · {len(PRODUCTS)} piezas en total</p>
  </section>
</main>
{cart_drawer()}
{wa_float()}
{footer()}
<script>
(function(){{
  const params = new URLSearchParams(location.search);
  const col = params.get('col');
  if (col) {{
    document.querySelectorAll('.card').forEach(c => {{
      if (!c.querySelector(`img[src*="/${{col}}"]`)) {{ /* noop fallback */ }}
    }});
  }}
}})();
</script>
</body>
</html>"""
        path = "vitrinas.html" if page == 1 else f"vitrinas/pagina-{page}.html"
        write(path, base_head(f"{title} — MERIDIANO Casa Relojera",
              "Explore el catálogo completo de MERIDIANO: 59 relojes de alta réplica premium organizados en placas numeradas, sin scroll infinito.",
              canonical) + body)

# per-collection filtered pages (static, for SEO + real filtering without JS dependency)
def build_collection_pages():
    for c in COL_ORDER:
        items = by_col[c]
        cards = "".join(product_card(p, i) for i, p in enumerate(items))
        chips = '<a href="vitrinas.html" class="chip">Todas</a>' + "".join(
            f'<a href="vitrinas/coleccion-{cc}.html" class="chip{" active" if cc==c else ""}">{COLLECTIONS[cc]["label"]}</a>' for cc in COL_ORDER)
        idx = COL_ORDER.index(c)
        body = f"""<body>
{rail("vitrinas.html")}
<main class="page">
  <section class="wrap vitrina-head reveal">
    <span class="big-roman">{ROMAN[idx]}</span>
    <p class="kicker">Vitrina {ROMAN[idx]} · {len(items)} piezas</p>
    <h1>{COLLECTIONS[c]['label']}</h1>
    <p class="lede">{COLLECTIONS[c]['tagline']}</p>
    <div class="chips">{chips}</div>
  </section>
  <section class="wrap section" style="padding-top:0">
    <div class="grid">{cards}</div>
  </section>
</main>
{cart_drawer()}
{wa_float()}
{footer()}
</body>
</html>"""
        write(f"vitrinas/coleccion-{c}.html", base_head(
            f"Vitrina {COLLECTIONS[c]['label']} — MERIDIANO Casa Relojera",
            f"{COLLECTIONS[c]['tagline']} Descubra las {len(items)} piezas de la colección {COLLECTIONS[c]['label']} en MERIDIANO Casa Relojera.",
            f"/vitrinas/coleccion-{c}.html") + body)

# ============================================================ PRODUCTO
def build_products():
    for i, p in enumerate(PRODUCTS):
        prev_p = PRODUCTS[i-1] if i > 0 else PRODUCTS[-1]
        next_p = PRODUCTS[i+1] if i < len(PRODUCTS)-1 else PRODUCTS[0]
        col = COLLECTIONS[p["collection"]]
        wa_msg = f"Hola MERIDIANO, me interesa la pieza {p['name']} (Ref. {p['id']}) por {fmt_cop(p['price'])}. ¿Disponibilidad?"
        payload = esc(json.dumps({"id": p["id"], "name": p["name"], "price": p["price"], "img": p["img_card"]}, ensure_ascii=False))

        ld = f"""<script type="application/ld+json">
{json.dumps({
  "@context": "https://schema.org",
  "@type": "Product",
  "name": p["name"],
  "sku": p["id"],
  "image": f"{SITE}/{p['img_lg']}",
  "description": p["desc"],
  "brand": {"@type": "Brand", "name": "MERIDIANO"},
  "category": col["label"],
  "offers": {
      "@type": "Offer", "priceCurrency": "COP", "price": p["price"],
      "availability": "https://schema.org/InStock", "url": f"{SITE}/vitrinas/{p['slug']}.html"
  }
}, ensure_ascii=False)}
</script>"""

        body = f"""<body data-product='{payload}'>
{rail("vitrinas.html")}
<main class="page">
  <div class="wrap product">
    <div class="product-visual reveal">
      <div class="frame"><img src="{p['img_lg']}" alt="{esc(p['name'])} — {esc(p['dial'])}" width="1400" height="1050"></div>
      <p class="caption">{col['label']} · Ref. {p['id']}</p>
    </div>
    <div class="product-info reveal">
      <p class="breadcrumb">
        <a href="index.html">Fundación</a> / <a href="vitrinas.html">Vitrinas</a> / <a href="vitrinas/coleccion-{p['collection']}.html">{col['label']}</a>
      </p>
      <h1>{esc(p['name'])}</h1>
      <p class="ref">Referencia {p['id']} · Colección {col['label']}</p>
      <p class="desc">{esc(p['desc'])}</p>

      <dl class="spec-table">
        <div><dt>Esfera</dt><dd>{esc(p['dial'].capitalize())}</dd></div>
        <div><dt>Caja y material</dt><dd>{esc(p['material'].capitalize())}</dd></div>
        <div><dt>Correa</dt><dd>{esc(p['strap'].capitalize())}</dd></div>
        <div><dt>Diámetro</dt><dd>{esc(p['size'])}</dd></div>
        <div><dt>Resistencia al agua</dt><dd>{esc(p['wr'])}</dd></div>
      </dl>

      <div class="price-line">
        <span class="price">{fmt_cop(p['price'])}</span>
        <span class="note">Precio de referencia · confirmar disponibilidad</span>
      </div>

      <div class="buy-row">
        <button class="btn solid" data-add='{payload}'>Añadir a la vitrina personal</button>
        <a href="#" class="btn-wa js-wa" data-msg="{esc(wa_msg)}">{WA_ICON} Comprar por WhatsApp</a>
      </div>

      <ul class="trust">
        <li>Control de calidad visual y mecánico antes del envío</li>
        <li>Garantía de 6 meses por defectos de fabricación</li>
        <li>Envíos asegurados a toda Colombia · entrega personal en Bogotá</li>
      </ul>
    </div>
  </div>

  <nav class="wrap pn-nav">
    <a href="vitrinas/{prev_p['slug']}.html">← {esc(prev_p['name'])}</a>
    <a href="vitrinas/{next_p['slug']}.html">{esc(next_p['name'])} →</a>
  </nav>
</main>
{cart_drawer()}
{wa_float()}
{footer()}
</body>
</html>"""
        write(f"vitrinas/{p['slug']}.html", base_head(
            f"{p['name']} — {col['label']} | MERIDIANO Casa Relojera",
            f"{p['desc']} Diámetro {p['size']}, {p['material']}, resistencia al agua {p['wr']}. {fmt_cop(p['price'])}.",
            f"/vitrinas/{p['slug']}.html", ld, ogimg=p["img_card"]) + body)

# ============================================================ MANIFIESTO
def build_manifesto():
    body = f"""<body>
{rail("manifiesto.html")}
<main class="page">
  <section class="wrap vitrina-head reveal">
    <p class="kicker">Manifiesto</p>
    <h1>El tiempo, bien medido</h1>
    <p class="lede">Por qué existimos y qué defendemos en cada pieza que sale de nuestro taller en Bogotá.</p>
  </section>

  <section class="wrap section manifest reveal" style="padding-top:0">
    <div class="visual"><img src="assets/img/products/{PRODUCTS[15]['slug']}-lg.webp" alt="Detalle de acabado MERIDIANO" loading="lazy"></div>
    <div>
      <blockquote>&ldquo;La ostentación es fácil. La precisión es una decisión diaria.&rdquo;</blockquote>
      <p class="body">MERIDIANO nace en Bogotá con una convicción simple: el buen gusto no depende del presupuesto, depende del criterio. Seleccionamos piezas de alta réplica bajo estándares premium —acero quirúrgico, cristales resistentes a rayones, movimientos silenciosos— y las sometemos a control visual y mecánico antes de que lleguen a su muñeca.</p>
      <p class="body" style="margin-top:16px">No fabricamos con el nombre de las grandes manufacturas suizas; nos inspiramos en su lenguaje de diseño para ofrecer una alternativa honesta, accesible y elegante al coleccionista colombiano exigente.</p>
    </div>
  </section>

  <section class="wrap section" style="padding-top:0">
    <div class="sec-head"><h2><span class="num">II.</span>Preguntas frecuentes</h2></div>
    <div class="faq">
      <details open>
        <summary>¿Qué diferencia a una pieza MERIDIANO de una réplica común?</summary>
        <div class="a">Trabajamos únicamente con talleres que cumplen estándares de alta réplica premium: acabados pulidos a mano, cristales de zafiro o mineral resistente, mecanismos automáticos silenciosos y peso equivalente al original. Cada unidad se revisa antes del envío.</div>
      </details>
      <details>
        <summary>¿Cuánto tiempo tarda el envío?</summary>
        <div class="a">En Bogotá, entre 24 y 48 horas con posibilidad de pago contraentrega. Al resto de Colombia despachamos por transportadora certificada, con tiempos de 2 a 5 días hábiles según la ciudad.</div>
      </details>
      <details>
        <summary>¿Ofrecen garantía?</summary>
        <div class="a">Sí, 6 meses de garantía por defectos de fabricación (corona, hermeticidad básica y movimiento). No cubre golpes, agua en profundidad no especificada ni mal uso.</div>
      </details>
      <details>
        <summary>¿Cómo se paga un pedido?</summary>
        <div class="a">Confirmamos el pedido por WhatsApp, coordinamos método de pago (transferencia, contraentrega en Bogotá) y despachamos una vez confirmado.</div>
      </details>
      <details>
        <summary>¿Puedo ver la pieza antes de comprar?</summary>
        <div class="a">En Bogotá coordinamos puntos de encuentro seguros o visita a showroom con cita previa por WhatsApp. Para otras ciudades, enviamos fotos y video real de la unidad exacta que despachamos.</div>
      </details>
    </div>
  </section>
</main>
{cart_drawer()}
{wa_float()}
{footer()}
</body>
</html>"""
    write("manifiesto.html", base_head(
        "Manifiesto — MERIDIANO Casa Relojera",
        "Conozca la filosofía de MERIDIANO Casa Relojera: piezas de alta réplica premium, control de calidad y preguntas frecuentes sobre envíos, garantía y pagos.",
        "/manifiesto.html") + body)

# ============================================================ CONTACTO
def build_contact():
    ld = f"""<script type="application/ld+json">
{json.dumps({
  "@context": "https://schema.org",
  "@type": "ContactPage",
  "url": f"{SITE}/contacto.html",
  "about": {"@type": "JewelryStore", "name": "MERIDIANO · Casa Relojera"}
}, ensure_ascii=False)}
</script>"""
    body = f"""<body>
{rail("contacto.html")}
<main class="page">
  <section class="wrap vitrina-head reveal">
    <p class="kicker">Contacto</p>
    <h1>Hablemos de su próxima pieza</h1>
    <p class="lede">Nuestro canal principal es WhatsApp: respuesta directa, fotos reales de inventario y asesoría personalizada.</p>
  </section>

  <section class="wrap section contact-grid" style="padding-top:0">
    <div class="contact-cell reveal">
      <h3>WhatsApp</h3>
      <p>Asesoría, disponibilidad y confirmación de pedidos.</p>
      <p style="margin-top:14px"><a href="#" class="js-wa" data-msg="Hola MERIDIANO, quisiera hacer una consulta.">Escribir ahora →</a></p>
    </div>
    <div class="contact-cell reveal" style="transition-delay:80ms">
      <h3>Ubicación</h3>
      <p>Bogotá, Colombia.<br>Showroom con cita previa.</p>
      <p style="margin-top:14px">Envíos a todo el país por transportadora certificada.</p>
    </div>
    <div class="contact-cell reveal" style="transition-delay:160ms">
      <h3>Horario de atención</h3>
      <p>Lunes a sábado<br>9:00 a.m. – 7:00 p.m.</p>
      <p style="margin-top:14px">Domingos y festivos: mensajes por WhatsApp, respuesta al siguiente día hábil.</p>
    </div>
  </section>
</main>
{cart_drawer()}
{wa_float()}
{footer()}
</body>
</html>"""
    write("contacto.html", base_head(
        "Contacto — MERIDIANO Casa Relojera",
        "Escríbanos por WhatsApp para asesoría, disponibilidad de piezas y confirmación de pedidos. Bogotá, Colombia, envíos a todo el país.",
        "/contacto.html", ld) + body)

# ============================================================ SITEMAP / ROBOTS
def build_seo_files():
    urls = ["/", "/vitrinas.html", "/manifiesto.html", "/contacto.html"]
    total_pages = math.ceil(len(PRODUCTS) / PER_PAGE)
    for n in range(2, total_pages + 1):
        urls.append(f"/vitrinas/pagina-{n}.html")
    for c in COL_ORDER:
        urls.append(f"/vitrinas/coleccion-{c}.html")
    for p in PRODUCTS:
        urls.append(f"/vitrinas/{p['slug']}.html")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f"  <url><loc>{SITE}{u}</loc></url>")
    xml.append("</urlset>")
    write("sitemap.xml", "\n".join(xml))
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    write("llms.txt", build_llms_txt())

def build_llms_txt():
    lines = [
        "# MERIDIANO · Casa Relojera",
        "",
        "> Casa relojera colombiana especializada en piezas de alta réplica premium inspiradas en Rolex, Patek Philippe y Cartier. No afiliada a las manufacturas originales que inspiran cada diseño.",
        "",
        "Idioma: español (Colombia). Moneda: COP. Envíos a toda Colombia. Contacto principal: WhatsApp.",
        "",
        "## Vitrinas (colecciones)",
    ]
    for c in COL_ORDER:
        lines.append(f"- {COLLECTIONS[c]['label']}: {COLLECTIONS[c]['tagline']} ({len(by_col[c])} piezas) — {SITE}/vitrinas/coleccion-{c}.html")
    lines.append("")
    lines.append("## Páginas clave")
    lines.append(f"- Catálogo completo: {SITE}/vitrinas.html")
    lines.append(f"- Manifiesto y preguntas frecuentes: {SITE}/manifiesto.html")
    lines.append(f"- Contacto: {SITE}/contacto.html")
    return "\n".join(lines) + "\n"

# ============================================================ helpers
def write(rel_path, content):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def build_favicon():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<circle cx="32" cy="32" r="30" fill="#0a0a0c" stroke="#c8a35f" stroke-width="2"/>
<text x="32" y="42" font-family="Georgia,serif" font-size="30" fill="#c8a35f" text-anchor="middle">M</text>
</svg>"""
    write("assets/img/favicon.svg", svg)

def build_og_cover():
    from PIL import Image
    src = "assets/img/products/" + PRODUCTS[10]["slug"] + "-lg.webp"
    im = Image.open(os.path.join(ROOT, src)).convert("RGB")
    im = im.resize((1200, 630))
    im.save(os.path.join(ROOT, "assets/img/og-cover.jpg"), quality=85)

if __name__ == "__main__":
    build_favicon()
    build_og_cover()
    build_index()
    build_vitrinas()
    build_collection_pages()
    build_products()
    build_manifesto()
    build_contact()
    build_seo_files()
    print("Sitio generado.")
