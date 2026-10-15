// Dynamic bits shared by every page: the runoff countdown and the mobile menu.
(function () {
  'use strict';
  var el = document.getElementById('vv-countdown');
  if (el) {
    var now = new Date();
    var today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    var target = Date.UTC(2026, 9, 25); // 25 October 2026 (2nd round)
    var d = Math.round((target - today) / 86400000);
    el.innerHTML =
      d > 1 ? 'Faltam <b>' + d + ' dias</b>' :
      d === 1 ? 'Falta <b>1 dia</b>' :
      d === 0 ? 'É <b>hoje</b>' :
      '<b>Segundo turno encerrado</b>';
  }
  var burger = document.querySelector('.vv-burger');
  var nav = document.getElementById('vv-nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('vv-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('.nav')) {
        nav.classList.remove('vv-open');
        burger.setAttribute('aria-expanded', 'false');
      }
    });
  }
})();
