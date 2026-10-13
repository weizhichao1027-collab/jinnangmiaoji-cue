/* Static HTML is authoritative. Preserve links from the former ?lang= site. */
(function () {
  'use strict';
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      var menu = document.querySelector('.language-menu[open]');
      if (menu) {
        menu.removeAttribute('open');
        menu.querySelector('summary').focus();
      }
    }
  });
  var locales = ['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko', 'es', 'fr', 'de', 'pt-BR', 'ru', 'ar', 'hi', 'id'];
  var url = new URL(window.location.href);
  var tag = url.searchParams.get('lang');
  if (!tag) return;
  var lower = tag.trim().replace(/_/g, '-').toLowerCase();
  var code = locales.find(function (locale) { return locale.toLowerCase() === lower; });
  if (!code) {
    if (/^zh-(hant|tw|hk|mo)/.test(lower)) code = 'zh-Hant';
    else if (/^zh/.test(lower)) code = 'zh-Hans';
    else if (/^pt/.test(lower)) code = 'pt-BR';
    else code = locales.find(function (locale) { return locale === lower.split('-')[0]; }) || 'en';
  }
  var base = document.body.dataset.base;
  var page = document.body.dataset.page;
  var file = page === 'home' ? '' : page + '.html';
  if (!['home', 'support', 'privacy', 'terms'].includes(page)) return;
  url.pathname = base + (code === 'zh-Hans' ? '' : code + '/') + file;
  url.searchParams.delete('lang');
  window.location.replace(url.href);
}());
