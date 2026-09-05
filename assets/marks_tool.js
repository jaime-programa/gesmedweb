(function () {
  'use strict';

  var VP_ID     = 'ri-img-viewport';
  var INNER_ID  = 'ri-img-inner';
  var CANVAS_ID = 'ri-marks-canvas';
  var PREV_ID   = 'ri-marks-preview-svg';
  var svgNS     = 'http://www.w3.org/2000/svg';

  var tool = { active: '', step: 0, x1: 0, y1: 0 };

  // ── Acceso a elementos ────────────────────────────────────────────────────────
  function vp()     { return document.getElementById(VP_ID); }
  function inner()  { return document.getElementById(INNER_ID); }
  function canvas() { return document.getElementById(CANVAS_ID); }
  function img() {
    var el = inner();
    return el ? el.querySelector('img') : null;
  }

  // ── React fiber: actualiza un <input> oculto y dispara evento ─────────────────
  function setReflexInput(el, value) {
    if (!el) return;
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, String(value));
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }

  // ── Nivel de zoom actual desde el DOM ────────────────────────────────────────
  function getScale() {
    var vpEl = vp();
    var nivel = vpEl ? parseInt(vpEl.getAttribute('data-zoom-nivel') || '1', 10) : 1;
    return [0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5][nivel] || 1;
  }

  // ── Área de contenido de la imagen en espacio PRE-rotación ───────────────────
  //
  // Devuelve { w, h, left, top, cssW, cssH, rotation, scale } donde:
  //   • w, h        = dimensiones del contenido en el CSS box (antes de rotar)
  //   • left, top   = offset del contenido dentro del CSS box (letterboxing)
  //   • cssW, cssH  = tamaño del CSS box de la imagen (offsetWidth/Height, sin transforms)
  //   • rotation    = ángulo en grados leído de data-rotation (0/90/180/270)
  //   • scale       = zoom actual
  //
  // Usa offsetWidth/offsetHeight para obtener las dimensiones del CSS layout SIN
  // que los CSS transforms (rotate, scale) las distorsionen.
  //
  function renderedImageRect() {
    var im = img(), inn = inner();
    if (!im || !inn || !im.naturalWidth) return null;

    var rotation = parseInt(inn.getAttribute('data-rotation') || '0', 10) % 360;
    var scale    = getScale();

    // Layout dimensions of the image CSS box (no CSS-transform effect)
    var cssW = im.offsetWidth, cssH = im.offsetHeight;
    if (!cssW || !cssH) return null;

    // Content area using object-fit:contain (applied BEFORE CSS rotation)
    var nw = im.naturalWidth, nh = im.naturalHeight;
    var na = nw / nh;          // natural aspect ratio
    var ra = cssW / cssH;      // container aspect ratio
    var cW, cH;
    if (na > ra) { cW = cssW; cH = cssW / na; }
    else         { cH = cssH; cW = cssH * na; }

    // Letterbox offset (centered)
    var cLeft = (cssW - cW) / 2;
    var cTop  = (cssH - cH) / 2;

    return { w: cW, h: cH, left: cLeft, top: cTop,
             cssW: cssW, cssH: cssH,
             rotation: rotation, scale: scale };
  }

  // ── Redimensionar canvas y SVG; aplicar mismo transform que la imagen ────────
  //
  // Canvas y SVG se posicionan en el área de contenido PRE-rotación y reciben
  // el mismo CSS transform (rotate + scale) con idéntico transform-origin.
  // Como el centro del área de contenido coincide siempre con el centro del
  // CSS box (por el centrado de object-fit:contain), el pivote de rotación
  // del canvas/SVG coincide exactamente con el de la imagen.
  //
  function setupCanvas() {
    var cv = canvas(), im = img();
    if (!cv || !im || !im.naturalWidth) return;

    var r = renderedImageRect();
    if (!r) return;

    // Resolución interna = dimensiones naturales (espacio de coords de las marcas)
    if (cv.width !== im.naturalWidth || cv.height !== im.naturalHeight) {
      cv.width  = im.naturalWidth;
      cv.height = im.naturalHeight;
    }

    // CSS: posición en espacio pre-rotación + mismo transform que la imagen
    cv.style.left            = r.left + 'px';
    cv.style.top             = r.top  + 'px';
    cv.style.width           = r.w    + 'px';
    cv.style.height          = r.h    + 'px';
    cv.style.transformOrigin = 'center center';
    cv.style.transform       = 'rotate(' + r.rotation + 'deg) scale(' + r.scale + ')';

    // SVG preview: misma lógica
    var sv = document.getElementById(PREV_ID);
    if (sv) {
      sv.style.left            = r.left + 'px';
      sv.style.top             = r.top  + 'px';
      sv.style.width           = r.w    + 'px';
      sv.style.height          = r.h    + 'px';
      sv.style.transformOrigin = 'center center';
      sv.style.transform       = 'rotate(' + r.rotation + 'deg) scale(' + r.scale + ')';
      sv.setAttribute('viewBox', '0 0 ' + im.naturalWidth + ' ' + im.naturalHeight);
      sv.setAttribute('preserveAspectRatio', 'none');
    }

    redrawCanvas();
  }

  // ── Conversión coordenadas navegador → píxeles naturales de imagen ────────────
  //
  // El canvas/imagen tienen transform: rotate(R) scale(S) con pivote en el centro
  // del CSS box (cssW/2, cssH/2) relativo al origen de #ri-img-inner.
  //
  // Inversa: dado click (clientX, clientY) en viewport →
  //   1. Convertir a coords locales de #ri-img-inner
  //   2. Restar pivote → relativo al centro del CSS box
  //   3. Deshacer scale (dividir por S)
  //   4. Deshacer rotación CW de R grados (= girar CCW R grados)
  //   5. Añadir la mitad del área de contenido → coords en CSS del canvas
  //   6. Escalar a píxeles naturales
  //
  function toImgCoords(clientX, clientY) {
    var im = img(), inn = inner();
    if (!im || !im.naturalWidth) return null;

    var r = renderedImageRect();
    if (!r) return null;

    var innRect = inn.getBoundingClientRect();
    var lx = clientX - innRect.left;
    var ly = clientY - innRect.top;

    // Pivote de rotación en coords de #ri-img-inner
    var cx = r.cssW / 2, cy = r.cssH / 2;

    // Relativo al pivote + deshacer escala
    var rx = (lx - cx) / r.scale;
    var ry = (ly - cy) / r.scale;

    // Deshacer rotación CW de R° ≡ rotación CCW de R°
    var rad = r.rotation * Math.PI / 180;
    var cos = Math.cos(rad), sin = Math.sin(rad);
    var urx = cos * rx - sin * ry;
    var ury = sin * rx + cos * ry;

    // Posición dentro del área de contenido del canvas (CSS px)
    var px = urx + r.w / 2;
    var py = ury + r.h / 2;

    // Escalar a píxeles naturales
    var mx = Math.round(px / r.w * im.naturalWidth);
    var my = Math.round(py / r.h * im.naturalHeight);

    if (mx < 0 || my < 0 || mx > im.naturalWidth || my > im.naturalHeight) return null;
    return { x: mx, y: my };
  }

  // ── Dibujo de marcas en el canvas ─────────────────────────────────────────────
  function drawArrow(ctx, fromX, fromY, toX, toY, lw) {
    var headLen = Math.max(lw * 5, 14);
    var angle   = Math.atan2(toY - fromY, toX - fromX);
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6),
               toY - headLen * Math.sin(angle - Math.PI / 6));
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6),
               toY - headLen * Math.sin(angle + Math.PI / 6));
    ctx.stroke();
  }

  function redrawCanvas() {
    var cv = canvas(), el = inner();
    if (!cv || !el) return;
    var ctx = cv.getContext('2d');
    ctx.clearRect(0, 0, cv.width, cv.height);
    var raw = el.getAttribute('data-ri-marcas') || '[]';
    var marks;
    try { marks = JSON.parse(raw); } catch (e) { return; }
    marks.forEach(function (m) {
      var color  = m.color  || '#ff0000';
      var grosor = m.grosor || 2;
      var font   = m.font   || 14;
      ctx.strokeStyle = color;
      ctx.fillStyle   = color;
      ctx.lineWidth   = grosor;
      ctx.lineCap     = 'round';
      ctx.lineJoin    = 'round';
      if (m.tipo_marca === 'c') {
        ctx.beginPath();
        ctx.arc(m.x_centro, m.y_centro, Math.max(m.radio, 1), 0, 2 * Math.PI);
        ctx.stroke();
        if (m.observacion) {
          ctx.font = font + 'px sans-serif';
          ctx.fillText(m.observacion, m.x_centro + m.radio + 4, m.y_centro + 4);
        }
      } else if (m.tipo_marca === 'f') {
        drawArrow(ctx, m.x2, m.y2, m.x_centro, m.y_centro, grosor);
        if (m.observacion) {
          ctx.font = font + 'px sans-serif';
          ctx.fillText(m.observacion, m.x2 + 6, m.y2 - 4);
        }
      } else if (m.tipo_marca === 't') {
        ctx.font = font + 'px sans-serif';
        ctx.fillText(m.observacion || '', m.x_centro, m.y_centro);
      }
    });
  }

  // ── SVG de preview ────────────────────────────────────────────────────────────
  function getPreviewSvg() {
    var el = document.getElementById(PREV_ID);
    if (!el) {
      el = document.createElementNS(svgNS, 'svg');
      el.id = PREV_ID;
      el.style.cssText = 'position:absolute;pointer-events:none;overflow:visible;z-index:10;';
      var inn = inner();
      if (inn) inn.appendChild(el);
    }
    // Sincronizar transform con el canvas
    var im = img(), r = renderedImageRect();
    if (r && im && im.naturalWidth) {
      el.style.left            = r.left + 'px';
      el.style.top             = r.top  + 'px';
      el.style.width           = r.w    + 'px';
      el.style.height          = r.h    + 'px';
      el.style.transformOrigin = 'center center';
      el.style.transform       = 'rotate(' + r.rotation + 'deg) scale(' + r.scale + ')';
      el.setAttribute('viewBox', '0 0 ' + im.naturalWidth + ' ' + im.naturalHeight);
      el.setAttribute('preserveAspectRatio', 'none');
    }
    return el;
  }

  function clearPreview() {
    var el = document.getElementById(PREV_ID);
    if (el) el.innerHTML = '';
  }

  function svgEl(tag, attrs) {
    var el = document.createElementNS(svgNS, tag);
    Object.keys(attrs).forEach(function (k) { el.setAttribute(k, attrs[k]); });
    return el;
  }

  function arrowDefs(id, color) {
    var defs   = document.createElementNS(svgNS, 'defs');
    var marker = svgEl('marker', { id: id, markerWidth: 10, markerHeight: 7, refX: 10, refY: 3.5, orient: 'auto' });
    marker.appendChild(svgEl('polygon', { points: '0 0,10 3.5,0 7', fill: color }));
    defs.appendChild(marker);
    return defs;
  }

  function drawPreviewDot(x, y) {
    var svg = getPreviewSvg();
    svg.innerHTML = '';
    svg.appendChild(svgEl('circle', { cx: x, cy: y, r: 6, fill: '#3b82f6', stroke: 'white', 'stroke-width': 2 }));
  }

  function drawPreviewCircle(cx, cy, r) {
    var svg = getPreviewSvg();
    svg.innerHTML = '';
    svg.appendChild(svgEl('circle', { cx: cx, cy: cy, r: 5, fill: '#3b82f6', stroke: 'white', 'stroke-width': 2 }));
    if (r > 0)
      svg.appendChild(svgEl('circle', { cx: cx, cy: cy, r: r, fill: 'none', stroke: '#3b82f6', 'stroke-width': 2, 'stroke-dasharray': '8 4' }));
  }

  function drawPreviewArrow(x1, y1, x2, y2) {
    var svg = getPreviewSvg();
    svg.innerHTML = '';
    svg.appendChild(arrowDefs('pa', '#3b82f6'));
    svg.appendChild(svgEl('circle', { cx: x1, cy: y1, r: 5, fill: '#3b82f6' }));
    svg.appendChild(svgEl('line', {
      x1: x2, y1: y2, x2: x1, y2: y1,
      stroke: '#3b82f6', 'stroke-width': 2,
      'marker-end': 'url(#pa)', 'stroke-dasharray': '8 4',
    }));
  }

  // ── Enviar marca finalizada a Reflex ──────────────────────────────────────────
  function finalizeMark(payload) {
    clearPreview();
    tool.step = 0;
    var inp = document.querySelector('[data-ri-marca-payload]');
    setReflexInput(inp, JSON.stringify(payload));
    setTimeout(function () {
      var btn = document.querySelector('[data-ri-marca-submit]');
      if (btn) btn.click();
    }, 60);
  }

  // ── Click: colocación de marca ────────────────────────────────────────────────
  document.addEventListener('click', function (e) {
    if (!tool.active) return;
    if (window._panSpaceDown) return;
    var vpEl = vp();
    if (!vpEl || !vpEl.contains(e.target)) return;
    if (e.target.closest('[data-panel-controles]')) return;

    var c = toImgCoords(e.clientX, e.clientY);
    if (!c) return;

    if (tool.active === 't') {
      finalizeMark({ tipo: 't', x1: c.x, y1: c.y, x2: 0, y2: 0, radio: 0 });
      return;
    }

    if (tool.step === 0) {
      tool.x1 = c.x; tool.y1 = c.y; tool.step = 1;
      drawPreviewDot(tool.x1, tool.y1);
    } else {
      if (tool.active === 'c') {
        var dx = c.x - tool.x1, dy = c.y - tool.y1;
        var radio = Math.round(Math.sqrt(dx * dx + dy * dy));
        finalizeMark({ tipo: 'c', x1: tool.x1, y1: tool.y1, x2: 0, y2: 0, radio: radio });
      } else if (tool.active === 'f') {
        finalizeMark({ tipo: 'f', x1: tool.x1, y1: tool.y1, x2: c.x, y2: c.y, radio: 0 });
      }
    }
  }, true);

  // ── Mousemove: preview en vivo ────────────────────────────────────────────────
  document.addEventListener('mousemove', function (e) {
    if (!tool.active || tool.step !== 1 || tool.active === 't') return;
    if (window._panSpaceDown) return;
    var vpEl = vp();
    if (!vpEl || !vpEl.contains(e.target)) return;
    var c = toImgCoords(e.clientX, e.clientY);
    if (!c) return;
    if (tool.active === 'c') {
      var dx = c.x - tool.x1, dy = c.y - tool.y1;
      drawPreviewCircle(tool.x1, tool.y1, Math.round(Math.sqrt(dx * dx + dy * dy)));
    } else if (tool.active === 'f') {
      drawPreviewArrow(tool.x1, tool.y1, c.x, c.y);
    }
  });

  // ── Observers ────────────────────────────────────────────────────────────────
  var toolObserver  = null;
  var marksObserver = null;
  var zoomTimer     = null;
  var rotTimer      = null;

  // Panel árbol: recalcular al terminar la transición de ancho
  document.addEventListener('transitionend', function (e) {
    if (e.target.id === 'ri-arbol-wrapper' && e.propertyName === 'width') {
      setupCanvas();
    }
  });

  function setupToolObserver() {
    var vpEl = vp();
    if (!vpEl || toolObserver) return;
    toolObserver = new MutationObserver(function () {
      var t = vpEl.getAttribute('data-ri-tool') || '';
      if (t !== tool.active) {
        tool.active = t; tool.step = 0; clearPreview();
        vpEl.style.cursor = t ? 'crosshair' : '';
      }
    });
    toolObserver.observe(vpEl, { attributes: true, attributeFilter: ['data-ri-tool'] });
    tool.active = vpEl.getAttribute('data-ri-tool') || '';
  }

  function setupZoomObserver() {
    var vpEl = vp();
    if (!vpEl) return;
    var zoomObs = new MutationObserver(function () {
      clearTimeout(zoomTimer);
      zoomTimer = setTimeout(function () { setupCanvas(); }, 350);
    });
    zoomObs.observe(vpEl, { attributes: true, attributeFilter: ['data-zoom-nivel'] });
  }

  function setupMarksObserver() {
    var innEl = inner();
    if (!innEl || marksObserver) return;
    marksObserver = new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        if (m.attributeName === 'data-ri-marcas') {
          redrawCanvas();
        }
        if (m.attributeName === 'data-image-id') {
          tool.step = 0; clearPreview();
          var im = img();
          if (!im) return;
          var done = function () { setupCanvas(); };
          if (im.complete && im.naturalWidth) done();
          else im.addEventListener('load', done, { once: true });
        }
        if (m.attributeName === 'data-rotation') {
          // Esperar a que la transición CSS de rotación (0.3 s) termine
          clearTimeout(rotTimer);
          rotTimer = setTimeout(function () { setupCanvas(); }, 350);
        }
      });
    });
    marksObserver.observe(innEl, {
      attributes: true,
      attributeFilter: ['data-ri-marcas', 'data-image-id', 'data-rotation'],
    });
  }

  new MutationObserver(function () {
    setupToolObserver();
    setupMarksObserver();
    setupZoomObserver();
    var cv = canvas(), im = img();
    if (cv && im) {
      if (im.complete && im.naturalWidth) setupCanvas();
      else im.addEventListener('load', function () { setupCanvas(); }, { once: true });
    }
  }).observe(document.body, { childList: true, subtree: true });

  setupToolObserver();
  setupMarksObserver();
  setupZoomObserver();
  var _cv = canvas(), _im = img();
  if (_cv && _im) {
    if (_im.complete && _im.naturalWidth) setupCanvas();
    else _im.addEventListener('load', function () { setupCanvas(); }, { once: true });
  }

}());
