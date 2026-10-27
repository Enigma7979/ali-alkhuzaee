'use strict';
(()=>{
 let lang=new URLSearchParams(location.search).get('lang')||'en';if(!['en','ar','ru'].includes(lang))lang='en';
 const edition=document.getElementById('edition');const checkout=document.querySelector('[data-checkout]');let availability=null;
 function localize(next){lang=['en','ar','ru'].includes(next)?next:'en';/* Preview images and their alt text follow the page language (zth-deck.js, site.js). */if(edition)edition.value=lang;updateCheckout()}
 document.addEventListener('ali:language',e=>localize(e.detail.lang));localize(lang);
 function updateCheckout(){if(!checkout||!availability?.available)return;checkout.disabled=false;const labels=availability.mode==='live'?{en:'Continue to secure checkout',ar:'متابعة إلى الدفع الآمن',ru:'Перейти к безопасной оплате'}:{en:'Test checkout — no real purchase',ar:'دفع تجريبي — ليس شراءً حقيقيًا',ru:'Тестовая оплата — не настоящая покупка'};checkout.textContent=labels[lang];document.querySelector('.checkout-status').textContent=availability.mode==='live'?{en:'One selected PDF edition. No account required.',ar:'نسخة PDF واحدة مختارة دون حساب.',ru:'Один выбранный PDF. Аккаунт не нужен.'}[lang]:{en:'Sandbox mode. No live payment.',ar:'وضع تجريبي دون دفع حي.',ru:'Песочница. Не настоящая оплата.'}[lang]}
 /* The store runs on its own origin (data-store-origin on <body>, empty = same origin). */const store=document.body.dataset.storeOrigin||'';
 if(checkout){fetch(store+'/store/availability/',{credentials:'same-origin'}).then(r=>r.ok?r.json():null).then(data=>{availability=data;updateCheckout()}).catch(()=>{});checkout.addEventListener('click',()=>{if(!checkout.disabled&&availability?.available)location.assign(store+'/store/checkout/?lang='+edition.value)})}
})();
