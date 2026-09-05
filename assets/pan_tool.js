(function () {
  var VIEWPORT_ID = 'ri-img-viewport';
  var INNER_ID    = 'ri-img-inner';

  // Debe coincidir con los niveles de ri_zoom_nivel en state.py (índices 0-8)
  var SCALES = [0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5];

  var panX = 0, panY = 0;
  var spaceDown = false;
  var isPanning = false;
  var startX, startY;
  var imageObserver = null;
  var zoomObserver  = null;
  var wheelSetup    = false;

  function vp()    { return document.getElementById(VIEWPORT_ID); }
  function inner() { return document.getElementById(INNER_ID); }

  function applyPan() {
    var el = inner();
    if (!el) return;
    el.style.transform = 'translate(' + panX + 'px, ' + panY + 'px)';
  }

  // Resetea el pan al cambiar de imagen
  window.resetPan = function () {
    panX = panY = 0;
    applyPan();
  };

  // ── Zoom: escala el pan para preservar el centro visible ─────────────────────
  // Cuando data-zoom-nivel cambia, MutationObserver provee el valor anterior.
  // panX_new = panX_old × (S_new / S_old) mantiene el mismo punto de la imagen
  // en el centro del viewport.

  function setupZoomObserver(vpEl) {
    if (zoomObserver) return;
    zoomObserver = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.attributeName !== 'data-zoom-nivel') return;
        var oldNivel = parseInt(m.oldValue !== null ? m.oldValue : '2', 10);
        var newNivel = parseInt(vpEl.getAttribute('data-zoom-nivel') || '2', 10);
        if (isNaN(oldNivel)) oldNivel = 2;
        if (isNaN(newNivel)) newNivel = 2;
        var sOld = SCALES[oldNivel] || 1;
        var sNew = SCALES[newNivel] || 1;
        panX = panX * sNew / sOld;
        panY = panY * sNew / sOld;
        applyPan();
      });
    });
    zoomObserver.observe(vpEl, {
      attributes: true,
      attributeFilter: ['data-zoom-nivel'],
      attributeOldValue: true,
    });
  }

  // ── Wheel → zoom (simula click en botones de Reflex) ─────────────────────────

  function setupWheel() {
    if (wheelSetup) return;
    var el = vp();
    if (!el) return;
    el.addEventListener('wheel', function (e) {
      e.preventDefault();
      var dir = e.deltaY < 0 ? 'in' : 'out';
      var btn = document.querySelector('[data-zoom-dir="' + dir + '"]');
      if (btn) btn.click();
    }, { passive: false });
    setupZoomObserver(el);
    wheelSetup = true;
  }

  // ── Detectar cambio de imagen → reset pan ─────────────────────────────────────

  function attachImageObserver(el) {
    imageObserver = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].attributeName === 'data-image-id') {
          window.resetPan();
          break;
        }
      }
    });
    imageObserver.observe(el, { attributes: true, attributeFilter: ['data-image-id'] });
  }

  // ── Toast inmediato al seleccionar archivos ──────────────────────────────────

  var _uploadToastEl  = null;
  var _uploadFileInp  = null;

  function _mostrarToastSubida() {
    if (_uploadToastEl) return;
    _uploadToastEl = document.createElement('div');
    _uploadToastEl.style.cssText = 'position:fixed;top:16px;right:16px;z-index:99999;' +
      'background:#ea580c;color:#fff;padding:10px 16px;border-radius:6px;' +
      'font-size:14px;font-weight:500;box-shadow:0 4px 12px rgba(0,0,0,.3);' +
      'opacity:1;transition:opacity .3s ease;pointer-events:none;';
    _uploadToastEl.textContent = 'Espere un momento';
    document.body.appendChild(_uploadToastEl);
    setTimeout(function () {
      if (!_uploadToastEl) return;
      _uploadToastEl.style.opacity = '0';
      setTimeout(function () {
        if (_uploadToastEl && _uploadToastEl.parentNode) {
          _uploadToastEl.parentNode.removeChild(_uploadToastEl);
        }
        _uploadToastEl = null;
      }, 300);
    }, 4000);
  }

  function _attachUploadListener() {
    var upDiv = document.getElementById('up_resultados');
    if (!upDiv) { _uploadFileInp = null; return; }
    var inp = upDiv.querySelector('input[type=file]');
    if (!inp || inp === _uploadFileInp) return;
    _uploadFileInp = inp;
    inp.addEventListener('change', function (e) {
      if (e.target.files && e.target.files.length > 0) _mostrarToastSubida();
    });
  }

  // Observa body para detectar cuándo los elementos aparecen en el DOM
  var bodyObserver = new MutationObserver(function () {
    setupWheel();
    var el = inner();
    if (el && !imageObserver) {
      attachImageObserver(el);
    } else if (!el && imageObserver) {
      imageObserver.disconnect();
      imageObserver = null;
      panX = panY = 0;
    }
    _attachUploadListener();
  });
  bodyObserver.observe(document.body, { childList: true, subtree: true });

  // Intento inmediato por si los elementos ya existen al cargar el script
  setupWheel();
  _attachUploadListener();
  var existing = inner();
  if (existing) attachImageObserver(existing);

  // ── Spacebar + drag pan ───────────────────────────────────────────────────────

  document.addEventListener('keydown', function (e) {
    if (e.code !== 'Space') return;
    if (e.target.matches('input, textarea, [contenteditable="true"]')) return;
    e.preventDefault();
    spaceDown = true;
    window._panSpaceDown = true;
    var el = vp();
    if (el) el.style.cursor = 'grab';
  });

  document.addEventListener('keyup', function (e) {
    if (e.code !== 'Space') return;
    spaceDown = false;
    window._panSpaceDown = false;
    isPanning = false;
    var el = vp();
    if (el) el.style.cursor = '';
  });

  document.addEventListener('mousedown', function (e) {
    if (!spaceDown) return;
    var el = vp();
    if (!el || !el.contains(e.target)) return;
    isPanning = true;
    startX = e.clientX;
    startY = e.clientY;
    el.style.cursor = 'grabbing';
    e.preventDefault();
  });

  document.addEventListener('mousemove', function (e) {
    if (!isPanning) return;
    panX += e.clientX - startX;
    panY += e.clientY - startY;
    startX = e.clientX;
    startY = e.clientY;
    applyPan();
  });

  document.addEventListener('mouseup', function () {
    if (!isPanning) return;
    isPanning = false;
    var el = vp();
    if (el && spaceDown) el.style.cursor = 'grab';
  });
}());
