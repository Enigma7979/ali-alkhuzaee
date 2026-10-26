'use strict';
/* Design system v2 runtime for the Stage B preview: language switching, click-to-play Shorts,
   presentation navigation (buttons, keys, swipe) and the studio budget selector. No dependencies. */
(()=>{
 const COPY=window.PREVIEW_COPY||{};const LANGS=['ar','en','ru'];
 const standalone=window.PV_STANDALONE===true;
 const get=(obj,path)=>path.split('.').reduce((v,k)=>v==null?v:v[k],obj);
 let lang='ar';
 const fromHash=location.hash.slice(1);
 if(LANGS.includes(fromHash))lang=fromHash;
 else{const q=new URLSearchParams(location.search).get('lang');if(LANGS.includes(q))lang=q;else{try{const s=localStorage.getItem('ali-language')||localStorage.getItem('ali-preview-lang');if(LANGS.includes(s))lang=s}catch(e){}}}

 if(window.PV_NO_REMOTE===true)document.querySelectorAll('img[data-remote]').forEach(img=>img.remove());
 else document.querySelectorAll('[data-standalone-only]').forEach(el=>el.remove());

 function apply(next){
  lang=LANGS.includes(next)?next:'ar';const c=COPY[lang]||{};
  const root=document.documentElement;root.lang=lang;root.dir=lang==='ar'?'rtl':'ltr';
  document.querySelectorAll('[data-t]').forEach(el=>{const v=get(c,el.dataset.t);if(typeof v==='string')el.textContent=v});
  document.querySelectorAll('[data-t-alt]').forEach(el=>{const v=get(c,el.dataset.tAlt);if(typeof v==='string')el.alt=v});
  document.querySelectorAll('[data-t-label]').forEach(el=>{const v=get(c,el.dataset.tLabel);const p=el.dataset.labelPrefix?get(c,el.dataset.labelPrefix)+': ':'';if(typeof v==='string')el.setAttribute('aria-label',p+v)});
  document.querySelectorAll('[data-src-'+lang+']').forEach(el=>{el.src=el.getAttribute('data-src-'+lang)});
  document.querySelectorAll('[data-lang]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===lang)));
  try{localStorage.setItem('ali-preview-lang',lang)}catch(e){}
  renderToc(c);renderTier(c);
 }
 document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>apply(b.dataset.lang)));
 /* On the live site, assets/site.js owns the language and announces each change. */
 document.addEventListener('ali:language',e=>apply(e.detail.lang));

 /* Click-to-play Short: the YouTube player loads only after the visitor asks for it. */
 document.addEventListener('click',e=>{
  const hit=e.target.closest('[data-short-play]');if(!hit||standalone||e.metaKey||e.ctrlKey||e.shiftKey)return;
  const card=hit.closest('[data-embed]');if(!card)return;e.preventDefault();
  const frame=document.createElement('iframe');
  frame.src=card.dataset.embed+'?autoplay=1&playsinline=1&rel=0';
  frame.title=(get(COPY[lang],'videoPlayer')||'Video player: ')+(get(COPY[lang],'videos.2.title')||'');
  frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
  frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
  hit.replaceWith(frame);frame.focus();
 });

 /* Presentation */
 const deck=document.querySelector('[data-deck]');
 const slides=deck?[...deck.querySelectorAll('[data-slide]')]:[];
 const nums=slides.map(s=>Number(s.dataset.slide));let index=0;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 function show(i,focus,dir){
  if(!slides.length)return;index=Math.max(0,Math.min(i,slides.length-1));slides.forEach((s,n)=>{s.hidden=n!==index;s.classList.remove('entering')});
  const active=slides[index];if(!reduced.matches&&dir){active.style.setProperty('--dir',String(dir*(lang==='ar'?-1:1)));void active.offsetWidth;active.classList.add('entering')}
  const n=nums[index];deck.querySelector('[data-count]').textContent=String(n).padStart(2,'0')+' / 16';
  deck.querySelector('[data-progress]').style.width=(n/16*100)+'%';
  deck.querySelector('[data-prev]').disabled=index===0;deck.querySelector('[data-next]').disabled=index===slides.length-1;
  deck.querySelectorAll('[data-toc] button').forEach(b=>b.setAttribute('aria-current',String(Number(b.dataset.goto)===n)));
  if(focus){const h=active.querySelector('h3');h&&h.focus({preventScroll:true})}
 }
 function goNum(n){const i=nums.indexOf(n);if(i>=0)show(i,true,i>index?1:-1)}
 function renderToc(c){
  const ol=deck&&deck.querySelector('[data-toc]');if(!ol)return;ol.replaceChildren();
  (c.toc||[]).forEach((title,i)=>{const n=i+1;const li=document.createElement('li');const b=document.createElement('button');b.type='button';b.dataset.goto=String(n);
   const num=document.createElement('b');num.textContent=String(n).padStart(2,'0');const t=document.createElement('span');t.textContent=title;b.append(num,t);
   if(!nums.includes(n)){b.disabled=true;const em=document.createElement('em');em.textContent=c.builtAfter||'';t.append(em)}
   b.setAttribute('aria-current',String(nums[index]===n));li.append(b);ol.append(li)});
 }
 if(deck){
  deck.querySelector('[data-prev]').addEventListener('click',()=>show(index-1,false,-1));
  deck.querySelector('[data-next]').addEventListener('click',()=>show(index+1,false,1));
  deck.addEventListener('click',e=>{const g=e.target.closest('[data-goto]');if(g&&!g.disabled)goNum(Number(g.dataset.goto))});
  deck.addEventListener('keydown',e=>{if(e.target.closest('input,select,textarea'))return;if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft')return;e.preventDefault();const forward=(e.key==='ArrowRight')!==(lang==='ar');show(index+(forward?1:-1),true,forward?1:-1)});
  const stage=deck.querySelector('[data-stage]');let x0=null,y0=null;
  stage.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse')return;x0=e.clientX;y0=e.clientY});
  stage.addEventListener('pointerup',e=>{if(x0===null)return;const dx=e.clientX-x0,dy=e.clientY-y0;x0=null;if(Math.abs(dx)<50||Math.abs(dx)<Math.abs(dy)*1.4)return;const forward=(dx<0)!==(lang==='ar');show(index+(forward?1:-1),false,forward?1:-1)});
  stage.addEventListener('pointercancel',()=>{x0=null});
 }

 /* Studio budget selector */
 const plot=document.querySelector('[data-plot]');let tier=1;
 function renderTier(c){
  if(!plot)return;plot.dataset.tier=String(tier);
  document.querySelectorAll('.tier-tabs [data-tier]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.tier)===tier)));
  document.querySelectorAll('.legend [data-min]').forEach(li=>li.classList.toggle('off',Number(li.dataset.min)>tier));
  const price=document.querySelector('[data-tier-price]');price.textContent=c['tier'+tier]||'';
  document.querySelector('[data-tier-name]').textContent=c['tier'+tier+'Name']||'';
  document.querySelector('[data-tier-tip]').textContent=c['tier'+tier+'Tip']||'';
  const ul=document.querySelector('[data-tier-items]');ul.replaceChildren();
  for(let t=1;t<=tier;t++)(c['tier'+t+'Items']||[]).forEach(item=>{const li=document.createElement('li');li.textContent=item;ul.append(li)});
 }
 document.querySelectorAll('.tier-tabs [data-tier]').forEach(b=>b.addEventListener('click',()=>{tier=Number(b.dataset.tier);renderTier(COPY[lang]||{})}));

 apply(lang);show(0);
})();
