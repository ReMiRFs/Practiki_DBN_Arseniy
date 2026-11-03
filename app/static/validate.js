(function () {
  const rules = {
    login:     v => /^[A-Za-z0-9]{6,}$/.test(v) || 'Логин: только латиница и цифры, не менее 6 символов',
    password:  v => v.length >= 8 || 'Пароль должен содержать не менее 8 символов',
    full_name: v => /^[А-Яа-яЁё\- ]+$/.test(v) && v.trim() !== '' || 'ФИО: только кириллица, пробелы и дефис',
    phone:     v => /^8\(\d{3}\)\d{3}-\d{2}-\d{2}$/.test(v) || 'Телефон в формате 8(XXX)XXX-XX-XX',
    email:     v => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v) || 'Введите email в формате name@example.ru',
    event_id:  v => v !== '' || 'Выберите мероприятие из списка',
    payment_method: v => v !== '' || 'Выберите способ оплаты',
    hall:      v => v !== '' || 'Выберите помещение',
    rating:    v => v !== '' || 'Поставьте оценку от 1 до 5',
    text:      v => v.trim().length >= 10 || 'Отзыв должен содержать не менее 10 символов',
  };

  function check(el) {
    const rule = rules[el.name];
    if (!rule) return true;
    const res = rule(el.value);
    const box = el.closest('.field');
    const err = box && box.querySelector('.field__error');
    const ok = res === true;
    if (box) box.classList.toggle('field--error', !ok);
    if (err) err.textContent = ok ? '' : res;
    return ok;
  }

  document.querySelectorAll('form[data-validate]').forEach(form => {
    form.querySelectorAll('input, select, textarea').forEach(el => {
      el.addEventListener('blur', () => check(el));
      el.addEventListener('input', () => { if (el.closest('.field--error')) check(el); });
    });
    form.addEventListener('submit', e => {
      let firstBad = null;
      form.querySelectorAll('input, select, textarea').forEach(el => {
        if (!check(el) && !firstBad) firstBad = el;
      });
      if (firstBad) { e.preventDefault(); firstBad.focus(); }
    });
  });
})();
