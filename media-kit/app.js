'use strict';
(async()=>{
 const select=document.getElementById('language');
 let copy,data;
 try{[copy,data]=await Promise.all([fetch('/media-kit/translations.json?v=visible-contact-3langs-1').then(r=>{if(!r.ok)throw Error('translations');return r.json()}),fetch('/media-kit/data.json').then(r=>{if(!r.ok)throw Error('data');return r.json()})]);}catch{return;}
 function setLanguage(lang,updateUrl=false){
  if(!copy[lang])lang='en';const c=copy[lang];
  document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';select.value=lang;
  document.querySelectorAll('[data-i18n]').forEach(el=>{if(c[el.dataset.i18n])el.textContent=c[el.dataset.i18n]});
  document.querySelectorAll('[data-array]').forEach(el=>{const value=el.dataset.array.split('.').reduce((v,k)=>v?.[k],c);if(value)el.textContent=value});
  document.querySelectorAll('[data-work]').forEach(el=>{const work=data.work[Number(el.dataset.work)];el.textContent=work.title[lang]||work.title.en});
  document.title=c.nav+' | Ali Alkhuzaee — '+(lang==='en'?'Brand Partnerships':c.cta);
  document.querySelector('meta[name="description"]').content=c.meta;document.querySelector('meta[property="og:description"]').content=c.meta;document.querySelector('meta[property="og:title"]').content=document.title;
  const canonical='https://alialkhuzaee.com/media-kit/'+(lang==='en'?'':'?lang='+lang);document.querySelector('link[rel="canonical"]').href=canonical;document.querySelector('meta[property="og:url"]').content=canonical;
  document.querySelectorAll('header .brand,header [data-i18n="home"]').forEach(a=>a.href='/?lang='+lang);
  try{localStorage.setItem('ali-language',lang)}catch{}
  if(updateUrl){const url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(null,'',url)}
  renderMetrics(lang);
 }
 function renderMetrics(lang){
  const list=data.metrics.filter(m=>m.value!==undefined&&m.value!==null&&m.value!==''&&m.asOf&&m.source&&m.label);
  const container=document.getElementById('metrics');container.replaceChildren();
  for(const m of list){const card=document.createElement('article');card.className='metric';const label=document.createElement('span');label.textContent=typeof m.label==='string'?m.label:(m.label[lang]||m.label.en);const value=document.createElement('b');value.textContent=String(m.value);const date=document.createElement('small');date.textContent=m.asOf;card.append(label,value,date);container.append(card)}
  document.getElementById('audience').hidden=!list.length;
 }
 let lang=new URLSearchParams(location.search).get('lang');if(!lang){try{lang=localStorage.getItem('ali-language')}catch{}}setLanguage(lang||'en');select.addEventListener('change',e=>setLanguage(e.target.value,true));document.getElementById('year').textContent=new Date().getFullYear();
})();
