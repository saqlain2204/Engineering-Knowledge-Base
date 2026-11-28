(function () {
  'use strict';

  var script = document.currentScript;
  if (!script) return;

  var indexData = null;
  var MIN_SCORE = 0.42;

  function loadIndex() {
    if (window.__SEARCH_INDEX__) {
      return Promise.resolve(window.__SEARCH_INDEX__);
    }

    return new Promise(function (resolve) {
      var indexScript = document.createElement('script');
      indexScript.src = siteRootPrefix() + 'assets/search-index.js';
      indexScript.onload = function () {
        resolve(window.__SEARCH_INDEX__ || { pages: [] });
      };
      indexScript.onerror = function () {
        fetch(siteRootPrefix() + 'assets/search-index.json')
          .then(function (r) {
            return r.ok ? r.json() : { pages: [] };
          })
          .then(resolve)
          .catch(function () {
            resolve({ pages: [] });
          });
      };
      document.head.appendChild(indexScript);
    });
  }

  var indexPromise = loadIndex().then(function (data) {
    indexData = data;
    return data;
  });

  function siteRootPrefix() {
    if (window.__EK_SITE_ROOT__) {
      return window.__EK_SITE_ROOT__();
    }
    var link = document.querySelector('link[rel="stylesheet"][href*="styles.css"]');
    if (!link) return './';
    return link.getAttribute('href').replace(/styles\.css(\?.*)?$/, '');
  }

  function toRelativeUrl(pathFromRoot) {
    return siteRootPrefix() + pathFromRoot.replace(/^\//, '');
  }

  function normalize(s) {
    return (s || '')
      .toLowerCase()
      .replace(/&amp;/g, ' and ')
      .replace(/[^a-z0-9\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function tokenize(query) {
    return normalize(query)
      .split(' ')
      .filter(function (t) {
        return t.length >= 2;
      });
  }

  function levenshtein(a, b, limit) {
    if (a === b) return 0;
    if (!a.length) return b.length;
    if (!b.length) return a.length;
    if (Math.abs(a.length - b.length) > limit) return limit + 1;

    var prev = new Array(b.length + 1);
    var curr = new Array(b.length + 1);
    var i;
    var j;

    for (j = 0; j <= b.length; j++) prev[j] = j;

    for (i = 1; i <= a.length; i++) {
      curr[0] = i;
      var rowMin = i;
      for (j = 1; j <= b.length; j++) {
        var cost = a[i - 1] === b[j - 1] ? 0 : 1;
        curr[j] = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost);
        if (curr[j] < rowMin) rowMin = curr[j];
      }
      if (rowMin > limit) return limit + 1;
      var tmp = prev;
      prev = curr;
      curr = tmp;
    }
    return prev[b.length];
  }

  function maxEditDistance(token) {
    if (token.length <= 3) return 1;
    if (token.length <= 5) return 2;
    return Math.max(2, Math.floor(token.length * 0.35));
  }

  function acronymScore(token, words) {
    if (token.length < 2 || words.length < 2) return 0;
    var wi = 0;
    var matched = 0;
    for (var c = 0; c < token.length; c++) {
      while (wi < words.length && words[wi][0] !== token[c]) wi++;
      if (wi >= words.length) return 0;
      matched++;
      wi++;
    }
    return matched === token.length ? 0.78 : 0;
  }

  function subsequenceScore(token, compact) {
    var ni = 0;
    for (var i = 0; i < compact.length && ni < token.length; i++) {
      if (compact[i] === token[ni]) ni++;
    }
    if (ni !== token.length) return 0;
    return Math.min(0.72, (token.length / compact.length) * 2);
  }

  function fuzzyTokenScore(token, corpus, words, compact) {
    if (!token) return 0;
    if (corpus.indexOf(token) !== -1) return 1;

    var w;
    var dist;
    var limit = maxEditDistance(token);

    for (w = 0; w < words.length; w++) {
      // Word contains the query token ("dead" in "deadlock"), or the token contains a
      // long-enough word. Short words like "a" or "to" must not match: otherwise any title
      // containing "a" scored highly for every query that has the letter "a" in it.
      if (words[w].indexOf(token) !== -1 ||
          (words[w].length >= 4 && words[w].length * 2 >= token.length && token.indexOf(words[w]) !== -1)) {
        return 0.93;
      }
      dist = levenshtein(token, words[w], limit);
      if (dist <= limit) {
        return 0.88 - dist * 0.08;
      }
    }

    var sub = subsequenceScore(token, compact);
    if (sub > 0) return sub;

    return acronymScore(token, words);
  }

  function fuzzyScore(query, text, weights) {
    var corpus = normalize(text);
    if (!corpus) return 0;

    var tokens = tokenize(query);
    if (!tokens.length) return 0;

    var words = corpus.split(' ').filter(Boolean);
    var compact = corpus.replace(/\s+/g, '');
    var tokenSum = 0;
    var t;

    for (t = 0; t < tokens.length; t++) {
      tokenSum += fuzzyTokenScore(tokens[t], corpus, words, compact);
    }

    var avg = tokenSum / tokens.length;
    var phrase = tokens.join(' ');
    var phraseBoost = 0;

    if (phrase.length >= 3) {
      if (corpus.indexOf(phrase) !== -1) {
        phraseBoost = 0.35;
      } else if (tokens.length > 1 && subsequenceScore(phrase, compact) > 0) {
        // For one-word queries the phrase is the token itself, which was already scored;
        // boosting it again let loose letter matches (e.g. "etag" in "pretraining") win.
        phraseBoost = 0.2;
      }
    }

    return Math.min(1, avg + phraseBoost) * (weights || 1);
  }

  function pageHeadings() {
    var items = [];
    var nodes = document.querySelectorAll('main h2[id], main section[id] > h2, .article h2[id], .article section[id] > h2');
    nodes.forEach(function (h2) {
      var section = h2.closest('section[id]');
      var id = section ? section.id : h2.id;
      if (!id) return;
      // ignore the "#" section link that site.js appends to headings
      var label = h2.textContent.replace(/^\d+\.\s*/, '').replace(/\s*#$/, '').trim();
      items.push({ id: id, label: label, text: label });
    });

    document.querySelectorAll('main details summary, .article details summary').forEach(function (summary, i) {
      var details = summary.parentElement;
      if (!details || !details.closest('main, .article')) return;
      var id = details.id;
      if (!id) {
        id = 'search-q-' + i;
        details.id = id;
      }
      var label = summary.textContent.trim();
      items.push({ id: id, label: label, text: label });
    });

    return items;
  }

  function scorePage(page, query) {
    var score = 0;
    score = Math.max(score, fuzzyScore(query, page.title, 1.4));
    score = Math.max(score, fuzzyScore(query, page.description, 1.1));
    score = Math.max(score, fuzzyScore(query, page.text, 1));

    (page.headings || []).forEach(function (h) {
      score = Math.max(score, fuzzyScore(query, h, 1.05));
    });

    (page.keywords || []).forEach(function (k) {
      score = Math.max(score, fuzzyScore(query, k, 1.2));
    });
    // multi-word queries such as "precision recall" can match across two keywords
    if (page.keywords && page.keywords.length > 1 && tokenize(query).length > 1) {
      score = Math.max(score, fuzzyScore(query, page.keywords.join(' '), 1.1));
    }

    return score + topicBonus(page, query);
  }

  // Many pages tie at the top score because the query appears somewhere in their long
  // body text (and "lora" is inside "exploration"). Break ties in favour of pages that are
  // *about* the query: each query word found as a whole word in the title, description,
  // headings or keywords adds a little.
  function topicBonus(page, query) {
    var tokens = tokenize(query);
    if (!tokens.length) return 0;
    if (!page._metaWords) {
      var meta = [page.title, page.description]
        .concat(page.headings || [], page.keywords || [])
        .join(' ');
      page._metaWords = {};
      normalize(meta).split(' ').forEach(function (w) {
        if (w) page._metaWords[w] = true;
      });
    }
    var hits = 0;
    tokens.forEach(function (t) {
      if (page._metaWords[t]) hits++;
    });
    return 0.2 * hits / tokens.length;
  }

  function searchPages(query) {
    if (!indexData || !query) return [];
    if (tokenize(query).length === 0 && normalize(query).length < 2) return [];

    return indexData.pages
      .map(function (p) {
        return { page: p, score: scorePage(p, query) };
      })
      .filter(function (x) {
        return x.score >= MIN_SCORE;
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .slice(0, 12)
      .map(function (x) {
        return x.page;
      });
  }

  function searchOnPage(query) {
    if (tokenize(query).length === 0 && normalize(query).length < 2) return [];
    return pageHeadings()
      .map(function (h) {
        return { item: h, score: fuzzyScore(query, h.text, 1) };
      })
      .filter(function (x) {
        return x.score >= MIN_SCORE;
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .map(function (x) {
        return x.item;
      });
  }

  function badgeLabel(type) {
    if (type === 'learn') return 'Learn';
    if (type === 'research') return 'Research';
    if (type === 'hub') return 'Hub';
    if (type === 'lab') return 'Lab';
    return 'Page';
  }

  function mountSearch() {
    var header = document.querySelector('header');
    if (!header || document.getElementById('site-search')) return;

    var wrap = document.createElement('div');
    wrap.className = 'site-search';
    wrap.id = 'site-search';
    wrap.innerHTML =
      '<label class="site-search-label" for="site-search-input">Search</label>' +
      '<div class="site-search-field">' +
      '<input type="search" id="site-search-input" class="site-search-input" placeholder="Search topics and pages…" autocomplete="off" spellcheck="false" aria-controls="site-search-results" aria-expanded="false">' +
      '<div id="site-search-results" class="site-search-results" aria-label="Search results" hidden></div>' +
      '</div>';

    var heroCta = header.querySelector('.hero-cta');
    if (heroCta && heroCta.parentNode === header) header.insertBefore(wrap, heroCta.nextSibling);
    else header.appendChild(wrap);

    var input = wrap.querySelector('#site-search-input');
    var results = wrap.querySelector('#site-search-results');
    input.setAttribute('aria-keyshortcuts', '/');
    if (window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      input.placeholder = 'Search topics, pages, sections (press / to focus)\u2026';
    }
    var indexFailed = !indexData || !indexData.pages || indexData.pages.length === 0;

    function render(query) {
      var tokens = tokenize(query);
      if (tokens.length === 0 && normalize(query).length < 2) {
        results.hidden = true;
        input.setAttribute('aria-expanded', 'false');
        results.innerHTML = '';
        return;
      }

      var local = searchOnPage(query);
      var pages = searchPages(query);
      var html = '';

      if (local.length) {
        html += '<div class="site-search-group"><p class="site-search-group-title">On this page</p><ul>';
        local.forEach(function (item) {
          html +=
            '<li><a class="site-search-hit site-search-hit-local" href="#' +
            item.id +
            '">' +
            escapeHtml(item.label) +
            '</a></li>';
        });
        html += '</ul></div>';
      }

      if (pages.length) {
        html += '<div class="site-search-group"><p class="site-search-group-title">Pages</p><ul>';
        pages.forEach(function (page) {
          html +=
            '<li><a class="site-search-hit" href="' +
            escapeHtml(toRelativeUrl(page.path)) +
            '">' +
            '<span class="site-search-hit-title">' +
            escapeHtml(page.title) +
            '</span>' +
            '<span class="site-search-hit-badge">' +
            badgeLabel(page.type) +
            '</span>' +
            (page.description
              ? '<span class="site-search-hit-desc">' + escapeHtml(page.description) + '</span>'
              : '') +
            '</a></li>';
        });
        html += '</ul></div>';
      }

      if (!html) {
        if (indexFailed) {
          html =
            '<p class="site-search-empty">Search index not loaded. Open the site via a local server or GitHub Pages, or rebuild with <code>scripts/build-search-index.ps1</code>.</p>';
        } else {
          html = '<p class="site-search-empty">No results for "' + escapeHtml(query) + '". Try shorter words or alternate spellings.</p>';
        }
      }

      results.innerHTML = html;
      results.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function escapeHtml(str) {
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    input.addEventListener('input', function () {
      render(input.value);
    });

    input.addEventListener('focus', function () {
      if (tokenize(input.value).length || normalize(input.value).length >= 2) render(input.value);
    });

    document.addEventListener('click', function (e) {
      if (!wrap.contains(e.target)) {
        results.hidden = true;
        input.setAttribute('aria-expanded', 'false');
      }
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        input.value = '';
        results.hidden = true;
        input.setAttribute('aria-expanded', 'false');
        input.blur();
      } else if (e.key === 'ArrowDown' && !results.hidden) {
        // Arrow keys move from the box into the result list
        var first = results.querySelector('a.site-search-hit');
        if (first) {
          e.preventDefault();
          first.focus();
        }
      }
    });

    // Up/Down move between results; Up from the first one, or Escape, returns to the box
    results.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp' && e.key !== 'Escape') return;
      var hits = Array.prototype.slice.call(results.querySelectorAll('a.site-search-hit'));
      var i = hits.indexOf(document.activeElement);
      if (i === -1) return;
      e.preventDefault();
      if (e.key === 'Escape') {
        input.focus(); // focus first: the box's focus handler re-opens the results
        results.hidden = true;
        input.setAttribute('aria-expanded', 'false');
      } else if (e.key === 'ArrowDown') {
        hits[Math.min(i + 1, hits.length - 1)].focus();
      } else if (i === 0) {
        input.focus();
      } else {
        hits[i - 1].focus();
      }
    });

    // Press "/" anywhere (when not typing in a field) to jump to the search box
    document.addEventListener('keydown', function (e) {
      if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey || e.defaultPrevented) return;
      var el = document.activeElement;
      var tag = el && el.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (el && el.isContentEditable)) return;
      e.preventDefault();
      input.focus();
      input.select();
    });

    results.addEventListener('click', function (e) {
      var link = e.target.closest('a');
      if (!link) return;
      var href = link.getAttribute('href');
      if (href.charAt(0) === '#') {
        results.hidden = true;
        input.setAttribute('aria-expanded', 'false');
        var target = document.querySelector(href);
        if (target && target.tagName === 'DETAILS') {
          target.open = true;
        }
      }
    });
  }

  indexPromise.then(mountSearch);
})();
