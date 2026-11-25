// ================= Страница «Онлайн-запись» =================
const bookingForm = document.getElementById('booking-form');
if (bookingForm) {
  const SERVICES = [
    { id: 'computer-diagnostics', title: 'Компьютерная диагностика', price: 1800, duration: 45, mechanic: 'Максим Крылов' },
    { id: 'engine-diagnostics', title: 'Диагностика двигателя', price: 1500, duration: 60, mechanic: 'Андрей Соколов' },
    { id: 'oil-change', title: 'Замена масла и фильтров', price: 900, duration: 40, mechanic: 'Игорь Лебедев' },
    { id: 'ac-refill', title: 'Заправка кондиционера', price: 2500, duration: 60, mechanic: 'Игорь Лебедев' },
    { id: 'brake-repair', title: 'Ремонт тормозной системы', price: 3000, duration: 90, mechanic: 'Сергей Волков' },
    { id: 'suspension-repair', title: 'Ремонт подвески', price: 4500, duration: 120, mechanic: 'Андрей Соколов' },
    { id: 'timing-belt', title: 'Замена ремня ГРМ', price: 6000, duration: 180, mechanic: 'Сергей Волков' },
    { id: 'tire-service', title: 'Шиномонтаж и балансировка', price: 2200, duration: 50, mechanic: 'Дмитрий Орлов' },
  ];

  const serviceSelect = document.getElementById('booking-service');
  const dateInput = document.getElementById('booking-date');
  const slotGrid = document.getElementById('slot-grid');
  const carInput = document.getElementById('booking-car');
  const phoneInput = document.getElementById('booking-phone');
  const agreeInput = document.getElementById('booking-agree');
  const summary = document.getElementById('booking-summary');
  const successPanel = document.getElementById('booking-success');
  let selectedSlot = null;

  SERVICES.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = `${s.title} — ${s.price.toLocaleString('ru-RU')} ₽`;
    serviceSelect.appendChild(opt);
  });

  // Предвыбор услуги из каталога: booking.html?service=oil-change
  const preset = new URLSearchParams(location.search).get('service');
  if (preset && SERVICES.some(s => s.id === preset)) serviceSelect.value = preset;

  const now = new Date();
  const todayISO = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  dateInput.min = todayISO;

  const fmtPrice = n => n.toLocaleString('ru-RU') + ' ₽';
  const currentService = () => SERVICES.find(s => s.id === serviceSelect.value) || null;
  const fmtDate = iso => new Date(iso + 'T00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', weekday: 'short' });

  function renderSlots() {
    slotGrid.innerHTML = '';
    selectedSlot = null;
    if (!dateInput.value) {
      slotGrid.innerHTML = '<p class="slot-hint">Сначала выберите дату визита</p>';
      return;
    }
    const seed = dateInput.value.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
    for (let h = 9; h <= 18; h++) {
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
        selectedSlot = time;
        setError('booking-time', '');
        updateSummary();
      });
      slotGrid.appendChild(btn);
    }
  }

  function updateSummary() {
    const s = currentService();
    document.getElementById('sum-service').textContent = s ? s.title : '—';
    document.getElementById('sum-mechanic').textContent = s ? s.mechanic : '—';
    document.getElementById('sum-duration').textContent = s ? `≈ ${s.duration} мин` : '—';
    document.getElementById('sum-date').textContent = dateInput.value ? fmtDate(dateInput.value) : '—';
    document.getElementById('sum-time').textContent = selectedSlot || '—';
    document.getElementById('sum-car').textContent = carInput.value.trim() || '—';
    document.getElementById('sum-price').textContent = s ? fmtPrice(s.price) : '0 ₽';
    summary.classList.remove('pulse');
    void summary.offsetWidth;
    summary.classList.add('pulse');
  }

  function renderLastBooking() {
    const box = document.getElementById('last-booking');
    try {
      const raw = localStorage.getItem('autofix_last_booking');
      if (!raw) { box.classList.add('hidden'); return; }
      const b = JSON.parse(raw);
      box.classList.remove('hidden');
      box.innerHTML = `
        <h3>Последняя заявка</h3>
        <p class="lb-num">№ ${b.num} <span class="card-badge">Новая</span></p>
        <p>${b.service}</p>
        <p class="card-meta">${b.date} в ${b.time} · ${b.car}</p>
        <p class="card-price">${b.price}</p>`;
    } catch {
      localStorage.removeItem('autofix_last_booking');
      box.classList.add('hidden');
    }
  }

  serviceSelect.addEventListener('change', () => { setError('booking-service', ''); updateSummary(); });
  dateInput.addEventListener('change', () => { setError('booking-date', ''); renderSlots(); updateSummary(); });
  carInput.addEventListener('input', () => { setError('booking-car', ''); updateSummary(); });
  phoneInput.addEventListener('input', () => setError('booking-phone', ''));
  agreeInput.addEventListener('change', () => setError('booking-agree', ''));

  bookingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    let ok = true;
    const s = currentService();
    if (!s) { setError('booking-service', 'Выберите услугу'); ok = false; }
    if (!dateInput.value) { setError('booking-date', 'Выберите дату'); ok = false; }
    else if (dateInput.value < todayISO) { setError('booking-date', 'Эта дата уже прошла'); ok = false; }
    if (!selectedSlot) { setError('booking-time', 'Выберите свободное время'); ok = false; }
    if (carInput.value.trim().length < 3) { setError('booking-car', 'Укажите марку, модель и год'); ok = false; }
    const digits = phoneInput.value.replace(/\D/g, '');
    if (!(digits.length === 11 && (digits[0] === '7' || digits[0] === '8'))) {
      setError('booking-phone', 'Формат: +7 900 123-45-67'); ok = false;
    }
    if (!agreeInput.checked) { setError('booking-agree', 'Нужно согласие на обработку данных'); ok = false; }
    if (!ok) return;

    const booking = {
      num: 'AF-' + String(Date.now()).slice(-6),
      service: s.title,
      mechanic: s.mechanic,
      date: new Date(dateInput.value + 'T00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }),
      time: selectedSlot,
      car: carInput.value.trim(),
      price: fmtPrice(s.price),
    };
    localStorage.setItem('autofix_last_booking', JSON.stringify(booking));
    document.getElementById('success-text').textContent =
      `Заявка № ${booking.num}: ${booking.service}, ${booking.date} в ${booking.time}. Мастер ${booking.mechanic} свяжется с вами для подтверждения.`;
    bookingForm.classList.add('hidden');
    successPanel.classList.remove('hidden');
    renderLastBooking();
    successPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  document.getElementById('book-again').addEventListener('click', () => {
    bookingForm.reset();
    ['booking-service', 'booking-date', 'booking-time', 'booking-car', 'booking-phone', 'booking-agree']
      .forEach(id => setError(id, ''));
    successPanel.classList.add('hidden');
    bookingForm.classList.remove('hidden');
    renderSlots();
    updateSummary();
  });

  renderSlots();
  updateSummary();
  renderLastBooking();
}

// ================= Страница «Контакты» =================
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

const statNums = document.querySelectorAll('.stat-num');
if (statNums.length) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const animate = el => {
    const target = Number(el.dataset.count);
    if (reduce || !('IntersectionObserver' in window)) { el.textContent = target.toLocaleString('ru-RU'); return; }
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