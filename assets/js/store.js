/* ============================================================
   MERIDIANO · Casa Relojera — motor de tienda
   Carrito (localStorage) · WhatsApp · GA4 · micro-interacciones
   ------------------------------------------------------------
   CONFIGURACIÓN: edite únicamente este bloque.
   ============================================================ */
const MERIDIANO = {
  // Número de WhatsApp en formato internacional SIN "+" ni espacios.
  // Ejemplo Colombia: 57 + número celular de 10 dígitos.
  whatsapp: '573001234567',            // ← CAMBIAR por el número real
  nombreTienda: 'MERIDIANO · Casa Relojera',
  moneda: 'COP'
};

/* ---------- utilidades ---------- */
const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];

const fmtCOP = n => '$ ' + new Intl.NumberFormat('es-CO').format(n) + ' COP';

function safeGtag() {
  if (typeof window.gtag === 'function') window.gtag.apply(null, arguments);
}

function waLink(msg) {
  return 'https://wa.me/' + MERIDIANO.whatsapp + '?text=' + encodeURIComponent(msg);
}

/* ---------- carrito ---------- */
const CART_KEY = 'meridiano_cart_v1';

function getCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}
function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  renderCartBadge();
  renderCartDrawer();
}
function addToCart(item) {
  const cart = getCart();
  const found = cart.find(i => i.id === item.id);
  if (found) found.qty += 1; else cart.push({ ...item, qty: 1 });
  saveCart(cart);
  toast('Añadida a su vitrina personal: ' + item.name);
  safeGtag('event', 'add_to_cart', {
    currency: MERIDIANO.moneda, value: item.price,
    items: [{ item_id: item.id, item_name: item.name, price: item.price, quantity: 1 }]
  });
  openCart();
}
function setQty(id, qty) {
  let cart = getCart();
  const it = cart.find(i => i.id === id);
  if (!it) return;
  it.qty = qty;
  if (it.qty <= 0) cart = cart.filter(i => i.id !== id);
  saveCart(cart);
}
function cartTotal(cart) { return cart.reduce((s, i) => s + i.price * i.qty, 0); }
function cartCount(cart) { return cart.reduce((s, i) => s + i.qty, 0); }

/* ---------- UI: badge, drawer, toast ---------- */
function renderCartBadge() {
  const n = cartCount(getCart());
  $$('.js-cart-count').forEach(el => {
    el.textContent = n;
    el.classList.toggle('is-empty', n === 0);
  });
}

function renderCartDrawer() {
  const list = $('#cartItems');
  if (!list) return;
  const cart = getCart();
  if (!cart.length) {
    list.innerHTML = '<p class="cart-empty">Su vitrina personal está vacía.<br>Recorra nuestras vitrinas y elija su próxima pieza.</p>';
  } else {
    list.innerHTML = cart.map(i => `
      <div class="cart-item">
        <img src="${i.img}" alt="${i.name}" loading="lazy">
        <div class="cart-item-info">
          <p class="cart-item-name">${i.name}</p>
          <p class="cart-item-ref">Ref. ${i.id}</p>
          <p class="cart-item-price">${fmtCOP(i.price)}</p>
        </div>
        <div class="cart-item-qty">
          <button aria-label="Restar" data-qty="${i.id}|${i.qty - 1}">−</button>
          <span>${i.qty}</span>
          <button aria-label="Sumar" data-qty="${i.id}|${i.qty + 1}">+</button>
        </div>
      </div>`).join('');
  }
  const totalEl = $('#cartTotal');
  if (totalEl) totalEl.textContent = fmtCOP(cartTotal(cart));
  const checkout = $('#cartCheckout');
  if (checkout) checkout.classList.toggle('is-disabled', !cart.length);
}

function openCart() { $('#cartDrawer')?.classList.add('open'); $('#cartVeil')?.classList.add('open'); }
function closeCart() { $('#cartDrawer')?.classList.remove('open'); $('#cartVeil')?.classList.remove('open'); }

let toastTimer;
function toast(msg) {
  let t = $('#toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
}

/* ---------- pedido por WhatsApp ---------- */
function checkoutWhatsApp() {
  const cart = getCart();
  if (!cart.length) return;
  const lines = cart.map(i => `• ${i.name} (Ref. ${i.id}) × ${i.qty} — ${fmtCOP(i.price * i.qty)}`);
  const msg = `Hola ${MERIDIANO.nombreTienda} 🕰️\n\nQuiero confirmar este pedido:\n\n${lines.join('\n')}\n\nTotal: ${fmtCOP(cartTotal(cart))}\n\n¿Disponibilidad y entrega?`;
  safeGtag('event', 'begin_checkout', {
    currency: MERIDIANO.moneda, value: cartTotal(cart),
    items: cart.map(i => ({ item_id: i.id, item_name: i.name, price: i.price, quantity: i.qty }))
  });
  window.open(waLink(msg), '_blank', 'noopener');
}

/* ---------- inicialización ---------- */
document.addEventListener('DOMContentLoaded', () => {
  renderCartBadge();
  renderCartDrawer();

  /* enlaces directos de WhatsApp (botón flotante, producto, contacto) */
  $$('.js-wa').forEach(a => {
    const msg = a.dataset.msg || 'Hola, vengo del sitio web de ' + MERIDIANO.nombreTienda + '. Quisiera más información.';
    a.href = waLink(msg);
    a.target = '_blank';
    a.rel = 'noopener';
    a.addEventListener('click', () => {
      safeGtag('event', 'contact_whatsapp', { link_text: a.dataset.msg ? 'producto' : 'general' });
    });
  });

  /* delegación de clics */
  document.addEventListener('click', e => {
    const add = e.target.closest('[data-add]');
    if (add) {
      e.preventDefault();
      addToCart(JSON.parse(add.dataset.add));
      return;
    }
    const qty = e.target.closest('[data-qty]');
    if (qty) {
      const [id, n] = qty.dataset.qty.split('|');
      setQty(id, parseInt(n, 10));
      return;
    }
    if (e.target.closest('.js-open-cart')) { e.preventDefault(); openCart(); }
    if (e.target.closest('.js-close-cart')) { e.preventDefault(); closeCart(); }
    if (e.target.closest('#cartCheckout')) { e.preventDefault(); checkoutWhatsApp(); }
  });

  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeCart(); });

  /* aparición al hacer scroll */
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    $$('.reveal').forEach(el => io.observe(el));
  } else {
    $$('.reveal').forEach(el => el.classList.add('in'));
  }

  /* GA4: vista de producto */
  const pv = document.body.dataset.product;
  if (pv) {
    try {
      const p = JSON.parse(pv);
      safeGtag('event', 'view_item', {
        currency: MERIDIANO.moneda, value: p.price,
        items: [{ item_id: p.id, item_name: p.name, price: p.price }]
      });
    } catch {}
  }
});
