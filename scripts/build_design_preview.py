"""Build the Stage B design preview.

python scripts/build_design_preview.py            -> design-preview/copy.js (served with the branch)
python scripts/build_design_preview.py OUT.html [ARTIFACT.html]
  OUT.html: one self-contained offline HTML file (images inlined; the YouTube thumbnail still loads when online)
  ARTIFACT.html: the same page body for a sandboxed review host that blocks third-party images and iframes

Approved site wording comes from the shared EN/AR/RU translation files; only new UI strings live here.
"""
from pathlib import Path
import base64,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
SITE=json.loads((ROOT/'assets/translations.json').read_text())
KIT=json.loads((ROOT/'media-kit/translations.json').read_text())
PROD=json.loads((ROOT/'assets/products/translations.json').read_text())
DATA=json.loads((ROOT/'media-kit/data.json').read_text())
REUSE=['heroEyebrow','heroLine1','heroLine2','heroIntro','explore','workWithMe','credential','founder','location','workLabel','workTitle','workAccent','workIntro','workTopics','watch','playVideo','openYouTube','videoPlayer','navAbout','navWork','navProducts','navPartnerships','languages']
KIT_REUSE={'kitEyebrow':'eyebrow','kitHero':'hero','kitName':'name','kitLead':'lead','kitIntro':'intro','kitRole':'role','kitCta':'cta','kitPdf':'pdf','kitPdfNote':'pdfNote','pill1':'pill1','pill2':'pill2','pill3':'pill3'}
PROD_REUSE=['productTitle','productIntro','launchPrice','oneTime','checkoutPending','editionNotice']
NEW={
'en':dict(
 previewBar='Design preview · Stage B · not the live website',samples='Samples',
 s1='Homepage hero',s2='Homepage section: selected work',s3='Featured Short card',s4='Media Kit introduction',s5='Media Kit metrics',s6='Digital Products',s7='Presentation introduction',s8='Studio lesson',
 rec='REC',frame='9:16 · VERTICAL',focusTag='AI · AUTOMATION · n8n',basedShort='Belgium & Ukraine',worksIn='Works in Arabic, English, Russian & Ukrainian',
 newBadge='New',channelCta='All Shorts on YouTube',
 thumbNote='Preview note: this review page cannot load images from YouTube, so the new card shows its titled fallback. On the website the official YouTube thumbnail loads in its place.',
 cardAnatomy='Click-to-play: nothing loads from YouTube until the visitor taps. Then the privacy-enhanced player opens in 9:16. Sound never starts by itself.',
 factFocus='Content focus',factFocusV='AI, technology, productivity, automation',factFormat='Format',factFormatV='Vertical short-form video',factLang='Content language',factLangV='Arabic-first',factWorks='Works in',factBase='Based in',factChannels='Main channels',
 metricsLabel='AUDIENCE & PERFORMANCE',metricsTitle='Verified numbers only.',metricsIntro='Each figure appears with its platform, date and source after Ali approves an analytics export. Nothing on this panel is estimated.',
 mFollowers='Followers',mViews='Views · last 30 days',mEng='Engagement rate',mCountries='Top countries',mAge='Main age range',pending='Awaiting verified export',asOf='As of',source='Source',
 verifiedLinks='Verified channel links',metricsHow='To publish this panel: send one dated screenshot or export per platform (Instagram, TikTok, YouTube). Each value is stored with its date and source in data.json.',
 productsLabel='DIGITAL PRODUCTS',freeDeck='Free interactive presentation',freeDeckMeta='16 sections · no sign-up · AR / EN / RU',
 inside1='10 chapters',inside2='50 original hooks',inside3='30 adaptable AI prompts',inside4='15 tool profiles',inside5='30-day practice plan',
 editionsLabel='PDF edition',editionsV='Arabic · English · Russian. You choose one.',checkoutBtn='Checkout opens after review',ctaDeck='Explore the free presentation',ctaPages='See real pages',coverCaption='Actual cover of the current review edition',
 deckEyebrow='FREE INTERACTIVE GUIDE · 16 SECTIONS',deckLead='Plan, film, light, record and edit short videos with your phone and free AI tools, then follow a 30-day practice plan.',chipFree='Free',chipNoSignup='No sign-up',chipLangs='AR · EN · RU',deckStart='Start',
 sectionsLabel='Sections',builtAfter='Built after approval',prev='Previous section',next='Next section',swipeHint='Swipe or use ← → keys',
 toc=['Cinematic introduction','Who this guide is for','Common problems','Content creation workflow','Affordable home studio','Camera position & posture','Lighting techniques','Sound & microphones','Product photography','Powerful hooks','Free & freemium AI tools','Ready-to-use AI prompts','Video editing','Thirty-day action plan','Genuine PDF preview','What you receive'],
 studioTitle='An affordable home studio',studioLead='Spend first on whatever fixes your biggest problem: shaky framing, unclear sound or flat light. Choose a budget level to see what it adds.',
 tier1='€0–€20',tier1Name='Use what you have',tier1Items=['Your current phone','A window as key light','White card or foam board as reflector','Phone clamp or simple tripod'],tier1Tip='Face the window at about 45°. Never film with the window behind you.',
 tier2='€40–€80',tier2Name='Stable picture, clear voice',tier2Items=['Stable tripod at eye level','Lavalier or compact wireless mic','Small LED panel for cloudy days'],tier2Tip='Sound usually improves a video more than a new camera. Test the microphone first.',
 tier3='€100–€180',tier3Name='Controlled light',tier3Items=['Softbox as soft key light','Desk microphone on a boom arm','RGB light for background depth'],tier3Tip='Keep the RGB light on the background. Your face stays lit by the neutral key light.',
 budgetNote='Illustrative budget ranges for planning. They are not current verified retail prices.',
 plotCaption='Illustration: lighting plot, top view. Not a photograph.',
 pWindow='Window',pKey='Key light · softbox',pFill='Fill · reflector',pPhone='Phone on tripod',pEye='lens at eye level',pYou='You',pDesk='Desk',pMic='Mic on boom arm',pLaptop='Laptop',pRgb='RGB background light',pLav='Lavalier mic',pLed='Small LED panel',pCable='Cables taped down',pWall='Back wall ≥ 1 m',pDist='1–1.5 m'),
'ar':dict(
 previewBar='معاينة التصميم · المرحلة B · ليست الموقع المنشور',samples='العينات',
 s1='واجهة الصفحة الرئيسية',s2='قسم من الرئيسية: أعمال مختارة',s3='بطاقة فيديو Shorts المميزة',s4='مقدمة الملف الإعلامي',s5='أرقام الملف الإعلامي',s6='المنتجات الرقمية',s7='مقدمة العرض التفاعلي',s8='درس الاستوديو',
 rec='تسجيل',frame='9:16 · عمودي',focusTag='AI · أتمتة · n8n',basedShort='بلجيكا وأوكرانيا',worksIn='أعمل بالعربية والإنجليزية والروسية والأوكرانية',
 newBadge='جديد',channelCta='كل الفيديوهات على YouTube',
 thumbNote='ملاحظة المعاينة: صفحة المراجعة هذه لا تستطيع تحميل الصور من YouTube، لذلك تظهر البطاقة الجديدة بعنوانها البديل. على الموقع تظهر الصورة المصغرة الرسمية من YouTube مكانها.',
 cardAnatomy='تشغيل عند الضغط: لا يُحمَّل شيء من YouTube حتى يضغط الزائر. بعدها يفتح المشغل المحسّن للخصوصية بمقاس 9:16، ولا يبدأ الصوت وحده أبدًا.',
 factFocus='محور المحتوى',factFocusV='الذكاء الاصطناعي، التقنية، الإنتاجية، الأتمتة',factFormat='الصيغة',factFormatV='فيديو قصير عمودي',factLang='لغة المحتوى',factLangV='العربية أولًا',factWorks='لغات العمل',factBase='مكان الإقامة',factChannels='المنصات الأساسية',
 metricsLabel='الجمهور والأداء',metricsTitle='أرقام موثّقة فقط.',metricsIntro='يظهر كل رقم مع المنصة والتاريخ والمصدر بعد أن يعتمد علي ملف إحصائيات. لا يوجد في هذه اللوحة أي تقدير.',
 mFollowers='المتابعون',mViews='المشاهدات · آخر 30 يومًا',mEng='معدل التفاعل',mCountries='أبرز الدول',mAge='الفئة العمرية الأساسية',pending='بانتظار بيانات موثّقة',asOf='بتاريخ',source='المصدر',
 verifiedLinks='روابط الحسابات الموثّقة',metricsHow='لنشر هذه اللوحة: أرسل لقطة شاشة أو ملف تصدير مؤرخًا لكل منصة (Instagram وTikTok وYouTube). يُحفظ كل رقم مع تاريخه ومصدره في data.json.',
 productsLabel='المنتجات الرقمية',freeDeck='عرض تفاعلي مجاني',freeDeckMeta='16 قسمًا · دون تسجيل · عربي / إنجليزي / روسي',
 inside1='10 فصول',inside2='50 افتتاحية أصلية',inside3='30 طلبًا قابلًا للتعديل للذكاء الاصطناعي',inside4='15 بطاقة تعريف بأداة',inside5='خطة تدريب لثلاثين يومًا',
 editionsLabel='نسخة PDF',editionsV='العربية · الإنجليزية · الروسية. تختار نسخة واحدة.',checkoutBtn='يُفتح الدفع بعد المراجعة',ctaDeck='استكشف العرض المجاني',ctaPages='شاهد صفحات حقيقية',coverCaption='الغلاف الفعلي لنسخة المراجعة الحالية',
 deckEyebrow='دليل تفاعلي مجاني · 16 قسمًا',deckLead='خطّط وصوّر وأضئ وسجّل وحرّر فيديوهات قصيرة بهاتفك وأدوات ذكاء اصطناعي مجانية، ثم اتبع خطة تدريب لثلاثين يومًا.',chipFree='مجاني',chipNoSignup='دون تسجيل',chipLangs='عربي · إنجليزي · روسي',deckStart='ابدأ',
 sectionsLabel='الأقسام',builtAfter='يُبنى بعد الموافقة',prev='القسم السابق',next='القسم التالي',swipeHint='اسحب أو استخدم مفاتيح ← →',
 toc=['مقدمة سينمائية','لمن هذا الدليل','المشكلات الشائعة','مراحل صناعة المحتوى','استوديو منزلي اقتصادي','وضعية الكاميرا والجلوس','تقنيات الإضاءة','الصوت والميكروفونات','تصوير المنتجات','افتتاحيات قوية','أدوات ذكاء اصطناعي مجانية وشبه مجانية','طلبات جاهزة للذكاء الاصطناعي','المونتاج','خطة عمل لثلاثين يومًا','معاينة حقيقية لملف PDF','ماذا تحصل عليه'],
 studioTitle='استوديو منزلي اقتصادي',studioLead='اصرف أولًا على ما يحل مشكلتك الأكبر: صورة مهتزة أو صوت غير واضح أو إضاءة باهتة. اختر الميزانية لترى ما تضيفه.',
 tier1='€0–€20',tier1Name='استخدم ما تملكه',tier1Items=['هاتفك الحالي','نافذة كمصدر ضوء رئيسي','ورق أبيض أو لوح فوم كعاكس','حامل هاتف أو ترايبود بسيط'],tier1Tip='اجعل النافذة أمامك بزاوية 45° تقريبًا، ولا تصوّر والنافذة خلفك.',
 tier2='€40–€80',tier2Name='صورة ثابتة وصوت واضح',tier2Items=['ترايبود ثابت بمستوى العين','ميكروفون مشبك أو لاسلكي صغير','إضاءة LED صغيرة للأيام الغائمة'],tier2Tip='تحسين الصوت يرفع جودة الفيديو غالبًا أكثر من كاميرا جديدة. جرّب الميكروفون أولًا.',
 tier3='€100–€180',tier3Name='إضاءة تحت السيطرة',tier3Items=['سوفت بوكس كضوء رئيسي ناعم','ميكروفون مكتبي على ذراع','إضاءة RGB لعمق الخلفية'],tier3Tip='اترك إضاءة RGB على الخلفية فقط، ويبقى وجهك تحت الضوء الرئيسي المحايد.',
 budgetNote='نطاقات ميزانية توضيحية للتخطيط، وليست أسعارًا حالية موثّقة في المتاجر.',
 plotCaption='رسم توضيحي: مخطط إضاءة من الأعلى. ليس صورة فوتوغرافية.',
 pWindow='نافذة',pKey='ضوء رئيسي · سوفت بوكس',pFill='ضوء مالئ · عاكس',pPhone='الهاتف على ترايبود',pEye='العدسة بمستوى العين',pYou='أنت',pDesk='المكتب',pMic='ميكروفون على ذراع',pLaptop='لابتوب',pRgb='إضاءة RGB للخلفية',pLav='ميكروفون مشبك',pLed='لوحة LED صغيرة',pCable='أسلاك مثبتة بشريط',pWall='الجدار الخلفي ≥ 1 م',pDist='1–1.5 م'),
'ru':dict(
 previewBar='Предпросмотр дизайна · этап B · не опубликованный сайт',samples='Образцы',
 s1='Первый экран главной',s2='Раздел главной: избранные работы',s3='Карточка нового Short',s4='Вступление медиакита',s5='Показатели медиакита',s6='Цифровые продукты',s7='Вступление презентации',s8='Урок о студии',
 rec='REC',frame='9:16 · ВЕРТИКАЛЬ',focusTag='ИИ · АВТОМАТИЗАЦИЯ · n8n',basedShort='Бельгия и Украина',worksIn='Работаю на арабском, английском, русском и украинском',
 newBadge='Новое',channelCta='Все Shorts на YouTube',
 thumbNote='Примечание: эта страница предпросмотра не может загружать изображения с YouTube, поэтому новая карточка показывает запасную обложку с названием. На сайте на её месте загрузится официальная обложка YouTube.',
 cardAnatomy='Запуск по нажатию: ничего не загружается с YouTube, пока посетитель не нажмёт. Затем открывается плеер с повышенной конфиденциальностью в формате 9:16. Звук сам не включается.',
 factFocus='Тематика',factFocusV='ИИ, технологии, продуктивность, автоматизация',factFormat='Формат',factFormatV='Короткие вертикальные видео',factLang='Язык контента',factLangV='Прежде всего арабский',factWorks='Рабочие языки',factBase='Базируюсь',factChannels='Основные платформы',
 metricsLabel='АУДИТОРИЯ И ПОКАЗАТЕЛИ',metricsTitle='Только проверенные цифры.',metricsIntro='Каждый показатель появится с платформой, датой и источником после того, как Али утвердит выгрузку статистики. На этой панели нет оценок.',
 mFollowers='Подписчики',mViews='Просмотры · 30 дней',mEng='Вовлечённость',mCountries='Основные страны',mAge='Основной возраст',pending='Ожидает проверенных данных',asOf='На дату',source='Источник',
 verifiedLinks='Проверенные ссылки на каналы',metricsHow='Чтобы опубликовать панель: пришлите датированный скриншот или выгрузку для каждой платформы (Instagram, TikTok, YouTube). Каждое значение хранится с датой и источником в data.json.',
 productsLabel='ЦИФРОВЫЕ ПРОДУКТЫ',freeDeck='Бесплатная интерактивная презентация',freeDeckMeta='16 разделов · без регистрации · AR / EN / RU',
 inside1='10 глав',inside2='50 оригинальных хуков',inside3='30 адаптируемых ИИ-запросов',inside4='15 профилей инструментов',inside5='План практики на 30 дней',
 editionsLabel='PDF-издание',editionsV='Арабский · английский · русский. Вы выбираете одно.',checkoutBtn='Оплата откроется после проверки',ctaDeck='Открыть бесплатную презентацию',ctaPages='Настоящие страницы',coverCaption='Настоящая обложка текущего издания для проверки',
 deckEyebrow='БЕСПЛАТНОЕ ИНТЕРАКТИВНОЕ РУКОВОДСТВО · 16 РАЗДЕЛОВ',deckLead='Планируйте, снимайте, ставьте свет, записывайте звук и монтируйте короткие видео на телефон с бесплатными ИИ-инструментами, а затем следуйте плану на 30 дней.',chipFree='Бесплатно',chipNoSignup='Без регистрации',chipLangs='AR · EN · RU',deckStart='Начать',
 sectionsLabel='Разделы',builtAfter='После одобрения',prev='Предыдущий раздел',next='Следующий раздел',swipeHint='Листайте или используйте ← →',
 toc=['Кинематографичное вступление','Для кого это руководство','Частые проблемы','Процесс создания контента','Бюджетная домашняя студия','Камера и посадка','Техники освещения','Звук и микрофоны','Предметная съёмка','Сильные хуки','Бесплатные и freemium ИИ-инструменты','Готовые ИИ-запросы','Монтаж видео','План на тридцать дней','Настоящие страницы PDF','Что вы получаете'],
 studioTitle='Бюджетная домашняя студия',studioLead='Сначала вкладывайтесь в то, что решает главную проблему: дрожащий кадр, неразборчивый звук или плоский свет. Выберите бюджет, чтобы увидеть, что он добавляет.',
 tier1='€0–€20',tier1Name='То, что уже есть',tier1Items=['Ваш телефон','Окно как основной свет','Белый картон или пенокартон как отражатель','Держатель или простой штатив'],tier1Tip='Повернитесь к окну примерно на 45°. Не снимайте спиной к окну.',
 tier2='€40–€80',tier2Name='Стабильный кадр, чистый голос',tier2Items=['Устойчивый штатив на уровне глаз','Петличка или компактный беспроводной микрофон','Небольшая LED-панель для пасмурных дней'],tier2Tip='Звук обычно улучшает видео сильнее новой камеры. Сначала проверьте микрофон.',
 tier3='€100–€180',tier3Name='Управляемый свет',tier3Items=['Софтбокс как мягкий основной свет','Настольный микрофон на пантографе','RGB-свет для глубины фона'],tier3Tip='Держите RGB-свет на фоне. Лицо освещает нейтральный основной свет.',
 budgetNote='Иллюстративные бюджеты для планирования, а не проверенные текущие цены в магазинах.',
 plotCaption='Иллюстрация: схема света, вид сверху. Не фотография.',
 pWindow='Окно',pKey='Основной свет · софтбокс',pFill='Заполняющий · отражатель',pPhone='Телефон на штативе',pEye='объектив на уровне глаз',pYou='Вы',pDesk='Стол',pMic='Микрофон на пантографе',pLaptop='Ноутбук',pRgb='RGB-свет фона',pLav='Петличный микрофон',pLed='Небольшая LED-панель',pCable='Кабели закреплены',pWall='Стена ≥ 1 м',pDist='1–1,5 м')}
def copy():
 out={}
 for l in ['en','ar','ru']:
  c={k:SITE[l][k] for k in REUSE}
  c.update({k:KIT[l][v] for k,v in KIT_REUSE.items()})
  c.update({k:PROD[l][k] for k in PROD_REUSE})
  c['videos']=[{'title':v['title'][l],'description':v.get('description',{}).get(l,'')} for v in DATA['work']]
  c.update(NEW[l]);out[l]=c
 return out
def main():
 js='window.PREVIEW_COPY='+json.dumps(copy(),ensure_ascii=False)+';\n'
 (ROOT/'design-preview/copy.js').write_text(js)
 if len(sys.argv)<2:return
 html=(ROOT/'design-preview/index.html').read_text()
 html=html.replace('<link rel="stylesheet" href="/assets/v2/ds.css">','<style>'+(ROOT/'assets/v2/ds.css').read_text()+'</style>')
 html=html.replace('<script src="copy.js"></script>','<script>'+js+'</script>')
 html=html.replace('<script src="/assets/v2/ds.js"></script>','<script>'+(ROOT/'assets/v2/ds.js').read_text()+'</script>')
 def inline(m):
  path=ROOT/m.group(2).lstrip('/').split('?')[0];mime='image/webp' if path.suffix=='.webp' else 'image/jpeg'
  return m.group(1)+'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()+m.group(3)
 html=re.sub(r'((?:src|data-src-[a-z]{2})=")(/assets/[^"]+\.(?:webp|jpe?g))(")',inline,html)
 offline=html.replace('<script>window.PREVIEW_COPY','<script>window.PV_STANDALONE=true;</script><script>window.PREVIEW_COPY',1)
 Path(sys.argv[1]).write_text(offline);print('wrote',sys.argv[1],len(offline)//1024,'KB')
 if len(sys.argv)>2:
  head=re.search(r'<head>(.*)</head>',html,re.S).group(1)
  head=re.sub(r'<meta (charset|name="viewport")[^>]*>','',head)
  body=re.search(r'<body[^>]*>(.*)</body>',html,re.S).group(1)
  art=head.strip()+'\n'+body.replace('<script>window.PREVIEW_COPY','<script>window.PV_STANDALONE=true;window.PV_NO_REMOTE=true;</script><script>window.PREVIEW_COPY',1)
  Path(sys.argv[2]).write_text(art);print('wrote',sys.argv[2],len(art)//1024,'KB')
if __name__=='__main__':main()
