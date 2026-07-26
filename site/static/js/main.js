// Botón "copiar" para cada bloque de código
document.querySelectorAll('.post-body pre').forEach(function (pre) {
  var btn = document.createElement('button');
  btn.className = 'copy-btn';
  btn.type = 'button';
  btn.textContent = 'copiar';
  btn.setAttribute('aria-label', 'Copiar bloque de código');
  pre.appendChild(btn);

  btn.addEventListener('click', function () {
    var code = pre.querySelector('code');
    var text = code ? code.innerText : pre.innerText;
    navigator.clipboard.writeText(text).then(function () {
      btn.textContent = 'copiado ✓';
      setTimeout(function () { btn.textContent = 'copiar'; }, 1600);
    }).catch(function () {
      btn.textContent = 'error';
    });
  });
});
