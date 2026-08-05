// ── BACKGROUND STARS ──
const bgCanvas = document.getElementById('bg-canvas');
if(bgCanvas){
  const bgCtx = bgCanvas.getContext('2d');
  let stars = [];
  function resizeBg(){ bgCanvas.width=window.innerWidth; bgCanvas.height=window.innerHeight; }
  function initStars(){
    stars=[];
    for(let i=0;i<120;i++) stars.push({x:Math.random()*bgCanvas.width,y:Math.random()*bgCanvas.height,r:Math.random()*1.5+0.3,speed:Math.random()*0.3+0.05,opacity:Math.random()*0.6+0.1});
  }
  function drawStars(){
    bgCtx.clearRect(0,0,bgCanvas.width,bgCanvas.height);
    stars.forEach(s=>{ bgCtx.beginPath();bgCtx.arc(s.x,s.y,s.r,0,Math.PI*2);bgCtx.fillStyle=`rgba(0,245,255,${s.opacity})`;bgCtx.fill();s.y+=s.speed;if(s.y>bgCanvas.height){s.y=0;s.x=Math.random()*bgCanvas.width;} });
    requestAnimationFrame(drawStars);
  }
  resizeBg(); initStars(); drawStars();
  window.addEventListener('resize',()=>{resizeBg();initStars();});
}

// ── HERO CANVAS ──
const pc = document.getElementById('product-canvas');
if(pc){
  const c = pc.getContext('2d');
  pc.width=520; pc.height=480;

  const items=[
    {label:'iPhone 15 Pro',price:'₹1,59,900',src:'/static/images/products/iphone-15-pro-max-natural-titanium-desktop-detail-1-Format-488.avif'},
    {label:'MacBook Air M3',price:'₹1,34,900',src:'/static/images/products/JunC8uNKpvguyZnZ.webp'},
    {label:'Sony WH-1000XM5',price:'₹26,990',src:'/static/images/products/pngtree-isolated-of-sony-wh-1000xm5-wireless-headphones-front-view-featuring-a-png-image_11941302.png'},
    {label:'Apple Watch 9',price:'₹41,900',src:'/static/images/products/apple-watch-series-9-gps-45mm-mr973hn-a-left-view.webp'},
    {label:'PlayStation 5',price:'₹54,990',src:'/static/images/products/ps5.jpg'},
    {label:'Samsung S24 Ultra',price:'₹1,29,999',src:'static/images/products/Samsung-Galaxy-S24-Ultra-Titanium-Violet-Smartphone-transparent-PNG-image-jpg.jpg'},
  ];

  const loadedImgs = items.map(item=>{
    const img=new Image(); img.src=item.src; return img;
  });

  const total = items.length;
  const radius = 165;
  let rotY = 0;
  let floatAng = 0;

  function roundRect(ctx,x,y,w,h,r){
    ctx.beginPath();ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);
    ctx.arcTo(x+w,y,x+w,y+r,r);ctx.lineTo(x+w,y+h-r);
    ctx.arcTo(x+w,y+h,x+w-r,y+h,r);ctx.lineTo(x+r,y+h);
    ctx.arcTo(x,y+h,x,y+h-r,r);ctx.lineTo(x,y+r);
    ctx.arcTo(x,y,x+r,y,r);ctx.closePath();
  }

  function draw(){
    c.clearRect(0,0,480,480);
    const cx=240, cy=300;
    floatAng += 0.008;
    rotY += 0.012;

    // Ground glow
    const glow=c.createRadialGradient(cx,cy+130,10,cx,cy+130,160);
    glow.addColorStop(0,'rgba(0,245,255,0.12)');
    glow.addColorStop(1,'transparent');
    c.fillStyle=glow; c.fillRect(0,0,480,480);

    // Ground ellipse
    c.beginPath();c.ellipse(cx,cy+130,140,30,0,0,Math.PI*2);
    c.strokeStyle='rgba(0,245,255,0.15)';c.lineWidth=1;c.stroke();

    // Calculate all card positions in 3D
    const cards = items.map((item,i)=>{
      const angle = (i/total)*Math.PI*2 + rotY;
      const x3d = Math.sin(angle)*radius;
      const z3d = Math.cos(angle)*radius;
      const scale = (z3d+radius)/(radius*2)*0.55+0.45;
      const screenX = cx + x3d*(480/(480-z3d*0.3));
      const screenY = cy + Math.sin(floatAng+i)*8;
      return {item, screenX, screenY, scale, z3d, i};
    });

    // Sort back to front
    cards.sort((a,b)=>a.z3d-b.z3d);

    cards.forEach(({item,screenX,screenY,scale,z3d,i})=>{
      const w=165*scale, h=200*scale;
      const x=screenX-w/2, y=screenY-h/2;
      const alpha = (z3d+radius)/(radius*2)*0.6+0.4;

      // Card shadow
      c.save();
      c.globalAlpha=alpha*0.4;
      c.beginPath();c.ellipse(screenX,screenY+h/2+6*scale,w*0.4,8*scale,0,0,Math.PI*2);
      c.fillStyle='rgba(0,0,0,0.6)';c.fill();
      c.restore();

      // Card body
      c.save();
      c.globalAlpha=alpha;
      const grad=c.createLinearGradient(x,y,x+w,y+h);
      grad.addColorStop(0,'rgba(13,21,38,0.97)');
      grad.addColorStop(1,'rgba(20,35,65,0.97)');
      c.shadowColor='rgba(0,245,255,0.4)';
      c.shadowBlur=15*scale;
      c.fillStyle=grad;
      roundRect(c,x,y,w,h,14*scale);c.fill();
      c.shadowBlur=0;

      // Card border glow (brighter for front cards)
      const borderAlpha = z3d>0 ? 0.8 : 0.3;
      c.strokeStyle=`rgba(0,245,255,${borderAlpha})`;
      c.lineWidth=1.5*scale;
      roundRect(c,x,y,w,h,14*scale);c.stroke();

      // Product image
      const img=loadedImgs[i];
      const imgSize=140*scale;
      const imgX=screenX-imgSize/2;
      const imgY=y+15*scale;
      if(img.complete && img.naturalWidth>0){
        c.save();
        roundRect(c,imgX,imgY,imgSize,imgSize,8*scale);
        c.clip();
        c.drawImage(img,imgX,imgY,imgSize,imgSize);
        c.restore();
      } else {
        c.fillStyle='rgba(0,245,255,0.1)';
        roundRect(c,imgX,imgY,imgSize,imgSize,8*scale);
        c.fill();
      }

      // Product name
      c.font=`bold ${14*scale}px sans-serif`;
      c.fillStyle='#e2e8f0';
      c.textAlign='center';
      c.textBaseline='middle';
      const maxW = w-10;
      let label = item.label;
      if(c.measureText(label).width>maxW) label=label.substring(0,14)+'...';
      c.fillText(label, screenX, y+h*0.72);

      // Price
      c.font=`bold ${14*scale}px monospace`;
      c.fillStyle='#09e6ab';
      c.fillText(item.price, screenX, y+h*0.88);

      c.restore();
    });

    requestAnimationFrame(draw);
  }
  draw();
}

// ── PRODUCT RENDERING ──
let activeFilter = 'All';
let allProducts = [];

function renderProducts(){
  const grid = document.getElementById('prod-grid');
  if(!grid) return;
  const filtered = activeFilter==='All' ? allProducts : allProducts.filter(p=>p.category===activeFilter);
  if(filtered.length === 0){
    grid.innerHTML = '<p style="color:var(--muted);text-align:center;grid-column:1/-1;padding:3rem;">No products found.</p>';
    return;
  }
  grid.innerHTML = filtered.map(p=>`
    <div class="prod-card" onclick="window.location.href='/product/${p.id}'">
      <div class="prod-img-wrap">
        <img src="${p.image_url}" alt="${p.name}" onerror="this.style.display='none'">
        ${p.badge ? `<div class="prod-badge">${p.badge}</div>` : ''}
        <div class="prod-wishlist" onclick="event.stopPropagation();this.textContent=this.textContent==='♡'?'♥':'♡';this.style.color=this.textContent==='♥'?'#ef4444':'';">♡</div>
        <div class="quick-view-overlay">
          <button class="quick-view-btn" onclick="event.stopPropagation();openQuickView(${p.id})">
            ⚡ Quick View
          </button>
        </div>
      </div>
      <div class="prod-body">
        <div class="prod-brand">${p.brand}</div>
        <div class="prod-name">${p.name}</div>
        <div class="prod-rating">
          <span class="stars">${'★'.repeat(Math.floor(p.rating))}${'☆'.repeat(5-Math.floor(p.rating))}</span>
          <span style="color:var(--neon);font-weight:700;">${p.rating}</span>
          <span class="rating-count">(${Number(p.reviews).toLocaleString('en-IN')})</span>
        </div>
        <div class="prod-price-row">
          <span class="prod-price">₹${Math.floor(p.price).toLocaleString('en-IN')}</span>
          <span class="prod-old">₹${Math.floor(p.old_price).toLocaleString('en-IN')}</span>
          <span class="prod-discount">${p.discount}% off</span>
        </div>
        <div class="emi-tag">No Cost EMI from ₹${Number(p.emi).toLocaleString('en-IN')}/mo</div>
        <div class="prod-actions">
          <button class="add-cart-btn" onclick="addToCart(${p.id}, this)">Add to Cart</button>
          <button class="buy-now-btn">Buy Now</button>
        </div>
      </div>
    </div>
  `).join('');
}

function setFilter(f, btn){
  activeFilter = f;
  document.querySelectorAll('.filter-tab').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderProducts();
}

function filterProducts(cat){
  activeFilter = cat;
  document.getElementById('products')?.scrollIntoView({behavior:'smooth'});
  renderProducts();
}

// ── LOAD PRODUCTS FROM API ──
fetch('/api/products')
  .then(r => r.json())
  .then(data => {
    allProducts = data;
    renderProducts();
  })
  .catch(err => console.error('Failed to load products:', err));

// ── CART ──
function addToCart(productId, btn){
  const orig = btn ? btn.textContent : '';
  if(btn){ btn.textContent='Adding...'; btn.disabled=true; }
  fetch(`/add-to-cart/${productId}`, {method:'POST'})
    .then(r=>{ if(r.status===401){window.location.href='/login';return null;} return r.json(); })
    .then(data=>{
      if(!data) return;
      updateCartCount(data.cart_count);
      if(btn){ btn.textContent='✓ Added!'; btn.style.background='linear-gradient(135deg,#4ade80,#16a34a)'; }
      const fc=document.getElementById('float-cart');
      if(fc){fc.style.transform='scale(1.3)';setTimeout(()=>fc.style.transform='',300);}
      setTimeout(()=>{ if(btn){btn.textContent=orig;btn.style.background='';btn.disabled=false;} },1500);
    });
}

function updateCartCount(count){
  const fc=document.getElementById('float-count');
  const cb=document.getElementById('cart-nav-btn');
  if(fc) fc.textContent=count;
  if(cb) cb.textContent=`🛒 Cart (${count})`;
}

// ── SEARCH ──
function doSearch(){
  const q=document.getElementById('nav-search')?.value.trim();
  if(!q) return;
  fetch(`/api/products?search=${encodeURIComponent(q)}`)
    .then(r=>r.json())
    .then(data=>{ allProducts=data; activeFilter='All'; renderProducts(); document.getElementById('products')?.scrollIntoView({behavior:'smooth'}); });
}
document.getElementById('nav-search')?.addEventListener('keydown',e=>{ if(e.key==='Enter') doSearch(); });

// ── TIMER ──
let secs=8*3600+45*60;
setInterval(()=>{
  if(secs<=0) return; secs--;
  const h=Math.floor(secs/3600),m=Math.floor((secs%3600)/60),s=secs%60;
  const th=document.getElementById('t-h'),tm=document.getElementById('t-m'),ts=document.getElementById('t-s');
  if(th) th.textContent=String(h).padStart(2,'0');
  if(tm) tm.textContent=String(m).padStart(2,'0');
  if(ts) ts.textContent=String(s).padStart(2,'0');
},1000);

// ── FADE UP ANIMATION ──
const obs=new IntersectionObserver(entries=>entries.forEach(e=>{ if(e.isIntersecting) e.target.classList.add('visible'); }),{threshold:.1});
document.querySelectorAll('.fade-up').forEach(el=>obs.observe(el));

// ── AUTO DISMISS FLASH ──
setTimeout(()=>document.querySelectorAll('.flash').forEach(f=>{f.style.opacity='0';setTimeout(()=>f.remove(),500);}),4000);
// ── QUICK VIEW ──
function openQuickView(productId) {
  const p = allProducts.find(x => x.id === productId);
  if (!p) return;

  document.getElementById('qv-img').src         = p.image_url;
  document.getElementById('qv-brand').textContent = p.brand;
  document.getElementById('qv-name').textContent  = p.name;
  document.getElementById('qv-rating').textContent = '★'.repeat(Math.floor(p.rating)) + '☆'.repeat(5 - Math.floor(p.rating));
  document.getElementById('qv-rcount').textContent = `${p.rating} (${Number(p.reviews).toLocaleString('en-IN')} reviews)`;
  document.getElementById('qv-price').textContent  = '₹' + Math.floor(p.price).toLocaleString('en-IN');
  document.getElementById('qv-old').textContent    = '₹' + Math.floor(p.old_price).toLocaleString('en-IN');
  document.getElementById('qv-disc').textContent   = p.discount + '% off';
  document.getElementById('qv-emi').textContent    = `No Cost EMI from ₹${Number(p.emi).toLocaleString('en-IN')}/mo`;
  document.getElementById('qv-desc').textContent   = p.description || 'Premium quality product.';
  document.getElementById('qv-stock').textContent  = p.stock > 0 ? `✅ In Stock (${p.stock} units)` : '❌ Out of Stock';
  document.getElementById('qv-cart-btn').onclick   = () => { addToCart(p.id, document.getElementById('qv-cart-btn')); };
  document.getElementById('qv-detail-btn').href    = `/product/${p.id}`;

  document.getElementById('quick-view-modal').classList.add('qv-open');
  document.body.style.overflow = 'hidden';
}

function closeQuickView() {
  document.getElementById('quick-view-modal').classList.remove('qv-open');
  document.body.style.overflow = '';
}

// close on backdrop click
document.getElementById('quick-view-modal').addEventListener('click', function(e) {
  if (e.target === this) closeQuickView();
});

// close on Escape key
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeQuickView(); });