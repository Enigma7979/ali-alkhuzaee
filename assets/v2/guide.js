'use strict';
/* Creator Guide samples: budget and lighting tabs that swap real licensed photos, and photographer credits.
   Runs after ds.js (language, deck navigation). Photo paths and credits come from window.GUIDE_PHOTOS. */
(()=>{
 const PHOTOS=window.GUIDE_PHOTOS||{};const COPY=window.PREVIEW_COPY||{};
 const lang=()=>COPY[document.documentElement.lang]?document.documentElement.lang:'ar';
 const c=()=>COPY[lang()]||{};
 const state={tier:0,light:0};

 function credit(name){
  const p=PHOTOS[name];if(!p)return null;const frag=document.createDocumentFragment();
  frag.append((c().gPhotoCredit||'Photo')+': ');
  const a=document.createElement('a');a.href=p.page;a.target='_blank';a.rel='noopener';a.textContent=p.by;a.dir='auto';
  frag.append(a,' / '+p.site);return frag;
 }
 function setPhoto(fig,name){
  const img=fig.querySelector('[data-photo-img]');const p=PHOTOS[name];if(!img||!p)return;
  if(img.dataset.name!==name){const first=!img.dataset.name;img.dataset.name=name;img.src=p.src;img.width=p.w;img.height=p.h;
   if(!first){img.classList.remove('fade');void img.offsetWidth;img.classList.add('fade')}}
  const slot=fig.closest('.slide').querySelector('[data-photo-credit]');if(slot){slot.replaceChildren();const f=credit(name);f&&slot.append(f)}
 }
 function render(){
  const t=c();
  document.querySelectorAll('[data-credit]').forEach(el=>{el.replaceChildren();const f=credit(el.dataset.credit);f&&el.append(f)});
  document.querySelectorAll('[data-tabs]').forEach(group=>{
   const key=group.dataset.tabs;group.querySelectorAll('[data-tab]').forEach(b=>{const on=Number(b.dataset.tab)===state[key];b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1});
   const active=group.querySelector(`[data-tab="${state[key]}"]`);const fig=group.closest('.slide').querySelector(key==='tier'?'[data-tier-photo]':'[data-light-photo]');setPhoto(fig,active.dataset.photo);
  });
  const ul=document.querySelector('[data-tier-list]');ul.replaceChildren();
  ((t.gTierItems||[])[state.tier]||[]).forEach(item=>{const li=document.createElement('li');li.textContent=item;ul.append(li)});
  document.querySelector('[data-tier-tip]').textContent=(t.gTierTips||[])[state.tier]||'';
  const l=(t.gLights||[])[state.light]||['',''];
  document.querySelector('[data-light-name]').textContent=l[0];document.querySelector('[data-light-text]').textContent=l[1];
 }
 document.querySelectorAll('[data-tabs]').forEach(group=>{
  const key=group.dataset.tabs;const tabs=[...group.querySelectorAll('[data-tab]')];
  group.addEventListener('click',e=>{const b=e.target.closest('[data-tab]');if(!b)return;state[key]=Number(b.dataset.tab);render()});
  group.addEventListener('keydown',e=>{
   if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft')return;e.preventDefault();e.stopPropagation();
   const step=(e.key==='ArrowRight')!==(document.documentElement.dir==='rtl')?1:-1;
   state[key]=(state[key]+step+tabs.length)%tabs.length;render();tabs[state[key]].focus();
  });
 });
 /* ds.js re-applies copy on every language change; follow it. */
 document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>render()));
 /* Warm the cache for tab photos so switching is instant. */
 const warm=()=>Object.values(PHOTOS).forEach(p=>{const i=new Image();i.decoding='async';i.src=p.src});
 'requestIdleCallback' in window?requestIdleCallback(warm):setTimeout(warm,1500);
 render();
})();
