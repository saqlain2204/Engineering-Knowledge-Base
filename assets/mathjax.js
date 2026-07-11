window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    tags: 'ams'
  },
  startup: {
    pageReady: function () {
      return MathJax.startup.defaultPageReady().then(function () {
        document.querySelectorAll('details').forEach(function (el) {
          el.addEventListener('toggle', function () {
            if (el.open) {
              MathJax.typesetPromise([el]);
            }
          });
        });
      });
    }
  }
};

(function () {
  if (document.getElementById('MathJax-script')) {
    return;
  }
  var script = document.createElement('script');
  script.id = 'MathJax-script';
  script.async = true;
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
  document.head.appendChild(script);
})();
