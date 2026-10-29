(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.querySelectorAll('.event, .card').forEach((el, i) => el.style.setProperty('--i', Math.min(i, 8)));

  document.querySelectorAll('.stars').forEach(box => {
    box.innerHTML = [...box.textContent.trim()].map((ch, i) => `<span style="--s:${i}">${ch}</span>`).join('');
  });

  document.addEventListener('click', e => {
    const a = e.target.closest('a[href]');
    if (!a || reduce || e.ctrlKey || e.metaKey || e.shiftKey || a.target === '_blank') return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin || url.href === location.href) return;
    e.preventDefault();
    document.body.classList.add('is-leaving');
    setTimeout(() => { location.href = url.href; }, 170);
  });
  window.addEventListener('pageshow', () => document.body.classList.remove('is-leaving'));

  document.addEventListener('pointerdown', e => {
    const btn = e.target.closest('.btn');
    if (!btn || reduce) return;
    const r = btn.getBoundingClientRect(), size = Math.max(r.width, r.height);
    const s = document.createElement('span');
    s.className = 'ripple';
    s.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - r.left - size / 2}px;top:${e.clientY - r.top - size / 2}px`;
    btn.appendChild(s);
    s.addEventListener('animationend', () => s.remove());
  });

  function shake(field) {
    field.classList.remove('shake'); void field.offsetWidth; field.classList.add('shake');
    field.addEventListener('animationend', () => field.classList.remove('shake'), { once: true });
  }
  document.querySelectorAll('.field--error').forEach(shake);
  document.querySelectorAll('form[data-validate]').forEach(form =>
    form.addEventListener('submit', () => setTimeout(() =>
      form.querySelectorAll('.field--error').forEach(shake), 0)));

  document.querySelectorAll('.alert--success').forEach(al => setTimeout(() => {
    al.classList.add('is-hiding');
    al.addEventListener('transitionend', () => al.remove(), { once: true });
  }, 4000));
})();
