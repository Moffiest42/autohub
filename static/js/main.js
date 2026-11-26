// ===== Тема оформления =====
const themeBtn = document.getElementById('theme-toggle');
if (themeBtn) {
  if (localStorage.getItem('theme') === 'dark') document.body.classList.add('dark');
  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  });
}

// ===== Показ / скрытие пароля =====
document.querySelectorAll('.toggle-password').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    if (input) input.type = input.type === 'password' ? 'text' : 'password';
  });
});

// ===== Общие ошибки полей =====
function setError(id, message) {
  const input = document.getElementById(id);
  const errorEl = document.getElementById(id + '-error');
  if (errorEl) errorEl.textContent = message;
  input?.classList.toggle('invalid', Boolean(message));
}

// ===== Онлайн-запись: серверная форма + удобный выбор слота =====
const bookingForm = document.getElementById('booking-form');
if (bookingForm) {
  const serviceSelect = document.getElementById('id_service');
  const hiddenDate = document.getElementById('id_date');
  const hiddenTime = document.getElementById('id_time');
  const datePicker = document.getElementById('booking-date-picker');
  const slotGrid = document.getElementById('slot-grid');
  const carInput = document.getElementById('id_car_info');
  const phoneInput = document.getElementById('id_phone');
  const agreeInput = document.getElementById('booking-agree');
  const summary = document.getElementById('booking-summary');

  const SERVICES = Array.from(serviceSelect.options)
    .filter(o => o.value)
    .map(o => ({
      id: o.value,
      title: o.dataset.title,
      price: Number(o.dataset.price),
      duration: Number(o.dataset.duration),
      mechanic: o.dataset.mechanic,
    }));

  const now = new Date();
  const todayISO = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  datePicker.min = todayISO;

  // Восстановление значений после серверной ошибки валидации
  if (hiddenDate.value) datePicker.value = hiddenDate.value;

  // Предвыбор услуги из каталога: /booking/?service=<id>
  const preset = new URLSearchParams(location.search).get('service');
  if (!serviceSelect.value && preset && SERVICES.some(s => s.id === preset)) {
    serviceSelect.value = preset;
  }

  const fmtPrice = n => n.toLocaleString('ru-RU') + ' ₽';
  const currentService = () => SERVICES.find(s => s.id === serviceSelect.value) || null;
  const fmtDate = iso => new Date(iso + 'T00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', weekday: 'short' });

  function renderSlots() {
    slotGrid.innerHTML = '';
    if (!datePicker.value) {
      slotGrid.innerHTML = '<p class="slot-hint">Сначала выберите дату визита</p>';
      return;
    }
    const day = new Date(datePicker.value + 'T00:00').getDay();
    if (day === 0) {
      slotGrid.innerHTML = '<p class="slot-hint">Воскресенье — выходной. Выберите другой день.</p>';
      return;
    }
    const startH = day === 6 ? 10 : 9;
    const endH = day === 6 ? 16 : 18;
    const seed = datePicker.value.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
    for (let h = startH; h <= endH; h++) {
      const time = `${String(h).padStart(2, '0')}:00`;
      const busy = (h + seed) % 4 === 0;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'slot' + (busy ? ' busy' : '');
      btn.textContent = time;
      btn.disabled = busy;
      if (busy) btn.title = 'Время занято';
      else btn.addEventListener('click', () => {
        slotGrid.querySelectorAll('.slot').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        hiddenTime.value = time;
        setError('booking-time', '');
        updateSummary();
      });
      if (hiddenTime.value === time && !busy) {
        btn.classList.add('selected');
      }
      slotGrid.appendChild(btn);
    }
  }

  function updateSummary() {
    const s = currentService();
    document.getElementById('sum-service').textContent = s ? s.title : '—';
    document.getElementById('sum-mechanic').textContent = s ? s.mechanic : '—';
    document.getElementById('sum-duration').textContent = s ? `≈ ${s.duration} мин` : '—';
    document.getElementById('sum-date').textContent = datePicker.value ? fmtDate(datePicker.value) : '—';
    document.getElementById('sum-time').textContent = hiddenTime.value || '—';
    document.getElementById('sum-car').textContent = carInput.value.trim() || '—';
    document.getElementById('sum-price').textContent = s ? fmtPrice(s.price) : '0 ₽';
    summary.classList.remove('pulse');
    void summary.offsetWidth;
    summary.classList.add('pulse');
  }

  datePicker.addEventListener('change', () => {
    hiddenDate.value = datePicker.value;
    hiddenTime.value = '';
    setError('booking-date', '');
    setError('booking-time', '');
    renderSlots();
    updateSummary();
  });
  serviceSelect.addEventListener('change', () => { setError('booking-service', ''); updateSummary(); });
  carInput.addEventListener('input', () => { setError('booking-car', ''); updateSummary(); });
  phoneInput.addEventListener('input', () => setError('booking-phone', ''));
  agreeInput.addEventListener('change', () => setError('booking-agree', ''));

  bookingForm.addEventListener('submit', (e) => {
    let ok = true;
    if (!serviceSelect.value) { setError('booking-service', 'Выберите услугу'); ok = false; }
    if (!datePicker.value) { setError('booking-date', 'Выберите дату'); ok = false; }
    else if (datePicker.value < todayISO) { setError('booking-date', 'Эта дата уже прошла'); ok = false; }
    if (!hiddenTime.value) { setError('booking-time', 'Выберите свободное время'); ok = false; }
    if (carInput.value.trim().length < 3) { setError('booking-car', 'Укажите марку, модель и год'); ok = false; }
    const digits = phoneInput.value.replace(/\D/g, '');
    if (!(digits.length === 11 && (digits[0] === '7' || digits[0] === '8'))) {
      setError('booking-phone', 'Формат: +7 900 123-45-67'); ok = false;
    }
    if (!agreeInput.checked) { setError('booking-agree', 'Нужно согласие на обработку данных'); ok = false; }
    // При ошибках блокируем отправку; при успехе форма уходит на сервер обычным POST
    if (!ok) e.preventDefault();
  });

  renderSlots();
  updateSummary();
}

// ===== Контакты: график работы =====
const openBadge = document.getElementById('open-badge');
if (openBadge) {
  const now = new Date();
  const day = now.getDay();
  const hour = now.getHours() + now.getMinutes() / 60;
  let open = false, closeAt = '';
  if (day >= 1 && day <= 5 && hour >= 9 && hour < 19) { open = true; closeAt = '19:00'; }
  if (day === 6 && hour >= 10 && hour < 17) { open = true; closeAt = '17:00'; }
  openBadge.textContent = open ? `● Открыто сейчас · до ${closeAt}` : '● Закрыто · Пн–Пт 09–19, Сб 10–17';
  openBadge.classList.add(open ? 'is-open' : 'is-closed');
  document.querySelectorAll('.hours-table tr[data-days]').forEach(r => {
    if (r.dataset.days.split(',').map(Number).includes(day)) r.classList.add('today');
  });
}

// ===== Контакты: счётчики =====
const statNums = document.querySelectorAll('.stat-num');
if (statNums.length) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const animate = el => {
    const target = Number(el.dataset.count);
    if (reduce) { el.textContent = target.toLocaleString('ru-RU'); return; }
    const start = performance.now(), dur = 1200;
    const tick = t => {
      const p = Math.min((t - start) / dur, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString('ru-RU');
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { animate(en.target); io.unobserve(en.target); } });
    }, { threshold: 0.4 });
    statNums.forEach(el => io.observe(el));
  } else {
    statNums.forEach(animate);
  }
}