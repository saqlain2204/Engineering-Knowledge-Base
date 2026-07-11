(function () {
  'use strict';

  function stylesheetBase() {
    var link = document.querySelector('link[rel="stylesheet"][href*="styles.css"]');
    if (!link) return './';
    return link.getAttribute('href').replace(/styles\.css(\?.*)?$/, '');
  }

  function isSubjectOnlyDeployment() {
    var path = decodeURIComponent(window.location.pathname).replace(/\\/g, '/');
    if (/\/Interview-Preparations\//.test(path) || /\/Engineering-Knowledge-Base\//.test(path)) {
      return false;
    }
    return /\/AI Engineer\/(learn|interview|research)\//.test(path);
  }

  function siteRootPrefix() {
    var base = stylesheetBase();
    if (isSubjectOnlyDeployment() && (base.match(/\.\.\//g) || []).length >= 3) {
      return base.replace(/^\.\.\//, '');
    }
    return base;
  }

  function stripRelativePrefix(href) {
    var rest = href;
    while (rest.indexOf('../') === 0) {
      rest = rest.slice(3);
    }
    while (rest.indexOf('./') === 0) {
      rest = rest.slice(2);
    }
    return rest;
  }

  window.__EK_SITE_ROOT__ = siteRootPrefix;

  // Only rewrite links when browsing via file:// protocol.
  // When served over HTTP/HTTPS (Vercel, GitHub Pages, local server, etc.)
  // all relative paths in the HTML files are already correct.
  if (window.location.protocol !== 'file:') {
    return;
  }

  function fixNavigationLinks() {
    var base = siteRootPrefix();

    // Only rewrite anchor links in subject-only file:// deployments
    if (isSubjectOnlyDeployment()) {
      document.querySelectorAll('a[href]').forEach(function (anchor) {
        var href = anchor.getAttribute('href');
        if (!href || /^(https?:|mailto:|#)/.test(href)) {
          return;
        }
        if (href.indexOf('../') === 0 || href.indexOf('./') === 0) {
          anchor.setAttribute('href', base + stripRelativePrefix(href));
        }
      });

      document.querySelectorAll('link[rel="stylesheet"][href*="styles.css"]').forEach(function (link) {
        var href = link.getAttribute('href');
        if (href && href.indexOf('../') === 0) {
          link.setAttribute('href', base + 'styles.css');
        }
      });

      document.querySelectorAll('link[rel="icon"][href*="assets/"]').forEach(function (link) {
        var href = link.getAttribute('href');
        if (href && href.indexOf('../') === 0) {
          link.setAttribute('href', base + stripRelativePrefix(href));
        }
      });

      document.querySelectorAll('script[src*="assets/"]').forEach(function (script) {
        var src = script.getAttribute('src');
        if (src && src.indexOf('../') === 0) {
          script.setAttribute('src', base + stripRelativePrefix(src));
        }
      });
    }
  }

  if (document.body) {
    fixNavigationLinks();
  } else {
    document.addEventListener('DOMContentLoaded', fixNavigationLinks);
  }
})();
