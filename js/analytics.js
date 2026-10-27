/* ===== АНАЛИТИКА =====
  Впиши номера счётчиков в кавычки и сохрани файл. Пустое значение = счётчик не подключается.
  yandexMetrika: номер счётчика Яндекс Метрики, например '98765432'
  googleAnalytics: ID потока GA4, например 'G-ABC123XYZ'
  vkPixel: ID пикселя VK Рекламы (Top@Mail.ru), например '3456789'
  Цели для всех трёх: call (нажал на телефон), whatsapp, telegram, max. */
window.SITE_ANALYTICS={yandexMetrika:'109492064',googleAnalytics:'',vkPixel:''};
(function(c,w,d){
  // счётчики работают только на настоящем домене, чтобы превью и тесты не портили статистику
  if(!/(^|\.)(xn--80af6aaljmg\.art|фотограф\.art)$/.test(location.hostname)){w.siteGoal=function(){};return;}
  var add=function(s){var e=d.createElement('script');e.async=1;e.src=s;d.head.appendChild(e);};
  if(c.yandexMetrika){
    w.ym=w.ym||function(){(w.ym.a=w.ym.a||[]).push(arguments)};w.ym.l=1*new Date();
    add('https://mc.yandex.ru/metrika/tag.js');
    w.ym(+c.yandexMetrika,'init',{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});
  }
  if(c.googleAnalytics){
    w.dataLayer=w.dataLayer||[];w.gtag=function(){w.dataLayer.push(arguments)};
    w.gtag('js',new Date());w.gtag('config',c.googleAnalytics);
    add('https://www.googletagmanager.com/gtag/js?id='+c.googleAnalytics);
  }
  if(c.vkPixel){
    w._tmr=w._tmr||[];w._tmr.push({id:String(c.vkPixel),type:'pageView',start:(new Date()).getTime()});
    add('https://top-fwz1.mail.ru/js/code.js');
  }
  w.siteGoal=function(g){
    try{if(c.yandexMetrika&&w.ym)w.ym(+c.yandexMetrika,'reachGoal',g)}catch(e){}
    try{if(c.googleAnalytics&&w.gtag)w.gtag('event','generate_lead',{method:g})}catch(e){}
    try{if(c.vkPixel&&w._tmr)w._tmr.push({type:'reachGoal',id:String(c.vkPixel),goal:g})}catch(e){}
  };
})(window.SITE_ANALYTICS,window,document);
