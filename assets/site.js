'use strict';
(async()=>{
 const supported=['en','ar','ru'];const kit=document.body.dataset.page==='kit';const path=kit?'/media-kit/':'/';
 const select=document.getElementById('language');const menu=document.querySelector('.menu-toggle');const nav=document.getElementById('main-nav');
 let translations={},kitCopy={},data={work:[],metrics:[]},current='en';
 const resolve=(obj,key)=>key.split('.').reduce((v,k)=>v?.[k],obj);
 function closeMenu(){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label',translations[current]?.menu||'Open navigation')}
 menu.addEventListener('click',()=>{const opened=menu.getAttribute('aria-expanded')!=='true';nav.classList.toggle('open',opened);menu.setAttribute('aria-expanded',String(opened));menu.setAttribute('aria-label',translations[current]?.[opened?'closeMenu':'menu']||'Navigation')});
 nav.addEventListener('click',e=>{if(e.target.closest('a'))closeMenu()});document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();menu.focus()}});
 try{
  const files=await Promise.all(['/assets/translations.json?v=premium-3','/media-kit/data.json?v=premium-3',...(kit?['/media-kit/translations.json?v=premium-3']:[])].map(async url=>{const r=await fetch(url);if(!r.ok)throw Error(url);return r.json()}));
  [translations,data]=files;if(kit)kitCopy=files[2];
 }catch{document.documentElement.dataset.translationError='true';return}
 function setLanguage(lang,updateUrl=true){
  if(!supported.includes(lang))lang='en';current=lang;const c={...translations[lang]};if(kit)for(const key of ['eyebrow','hero','name','intro','cta','whyLabel','why','whyIntro','whyCards','formatsLabel','formatsTitle','formatsIntro','formats','statsLabel','statsTitle','statsIntro'])c[key]=kitCopy[lang][key];
  document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';select.value=lang;
  document.querySelectorAll('[data-i18n]').forEach(el=>{const value=c[el.dataset.i18n];if(typeof value==='string')el.textContent=value});
  document.querySelectorAll('[data-array]').forEach(el=>{const value=resolve(c,el.dataset.array);if(typeof value==='string')el.textContent=value});
  document.querySelectorAll('[data-alt]').forEach(el=>el.alt=c[el.dataset.alt]||'Ali Alkhuzaee');
  document.querySelectorAll('[data-label]').forEach(el=>el.setAttribute('aria-label',c[el.dataset.label]||''));
  document.querySelectorAll('[data-video-title]').forEach(el=>{const v=data.work[Number(el.dataset.videoTitle)];if(v)el.textContent=v.title[lang]||v.title.en});
  document.querySelectorAll('[data-language-route]').forEach(el=>{const u=new URL(el.getAttribute('href'),location.href);u.searchParams.set('lang',lang);el.setAttribute('href',u.pathname+u.search+u.hash)});
  const title=kit?({en:'Media Kit | Ali Alkhuzaee — Brand Partnerships',ar:'الملف الإعلامي | علي الخزاعي — الشراكات التجارية',ru:'Медиакит | Али Альхузаи — Партнёрство с брендами'}[lang]):({en:'Ali Alkhuzaee | Technology, Made Human.',ar:'علي الخزاعي | تقنية أقرب، بفهم أبسط',ru:'Али Альхузаи | Технологии ближе к человеку'}[lang]);
  document.title=title;document.querySelector('meta[property="og:title"]').content=title;const description=translations[lang][kit?'seoKit':'seoHome'];document.querySelector('meta[name="description"]').content=description;document.querySelector('meta[property="og:description"]').content=description;
  const canonical='https://alialkhuzaee.com'+path+(lang==='en'?'':'?lang='+lang);document.querySelector('link[rel="canonical"]').href=canonical;document.querySelector('meta[property="og:url"]').content=canonical;
  if(updateUrl){const u=new URL(location.href);u.searchParams.set('lang',lang);history.replaceState(null,'',u)}
  try{localStorage.setItem('ali-language',lang)}catch{}
  renderMetrics(lang);closeMenu();
 }
 function renderMetrics(lang){if(!kit)return;const list=(data.metrics||[]).filter(m=>m.value!==undefined&&m.value!==null&&m.value!==''&&m.asOf&&m.source&&m.label);const container=document.getElementById('metrics');container.replaceChildren();for(const m of list){const card=document.createElement('article');card.className='metric';const label=document.createElement('span');label.textContent=typeof m.label==='string'?m.label:(m.label[lang]||m.label.en);const value=document.createElement('b');value.textContent=String(m.value);const date=document.createElement('small');date.textContent=m.asOf;card.append(label,value,date);container.append(card)}document.getElementById('audience').hidden=!list.length}
 let lang=new URLSearchParams(location.search).get('lang');if(!lang){try{lang=localStorage.getItem('ali-language')}catch{}}setLanguage(lang||'en',Boolean(lang));select.addEventListener('change',e=>setLanguage(e.target.value));document.getElementById('year').textContent=new Date().getFullYear();
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 if(!reduced.matches&&'IntersectionObserver'in window){document.documentElement.classList.add('js-motion');const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target)}}),{threshold:.06});document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));}
 const hero=document.querySelector('.hero-visual');if(!reduced.matches&&matchMedia('(pointer:fine) and (min-width:901px)').matches){let pending=false;hero.addEventListener('pointermove',e=>{if(pending)return;pending=true;requestAnimationFrame(()=>{const box=hero.getBoundingClientRect();hero.style.setProperty('--px',((e.clientX-box.left)/box.width-.5)*18+'px');hero.style.setProperty('--py',((e.clientY-box.top)/box.height-.5)*14+'px');pending=false})});hero.addEventListener('pointerleave',()=>{hero.style.setProperty('--px','0px');hero.style.setProperty('--py','0px')})}
 let scrolling=false;addEventListener('scroll',()=>{if(scrolling||reduced.matches)return;scrolling=true;requestAnimationFrame(()=>{const height=document.documentElement.scrollHeight-innerHeight;document.documentElement.style.setProperty('--progress',height>0?String(scrollY/height):'0');scrolling=false})},{passive:true});
})();
