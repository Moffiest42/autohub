// ---------- 1. Переключение темы (доп. интерактивность №1) ----------
const themeBtn = document.getElementById('theme-toggle');
if (themeBtn) {
  if (localStorage.getItem('theme') === 'dark') document.body.classList.add('dark');
  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  });
}

// ---------- 2. Поиск и табы каталога (доп. интерактивность №2) ----------
const searchInput = document.getElementById('catalog-search');
const tabs = document.querySelectorAll('.tab');

function filterCards() {
  const query = (searchInput?.value || '').toLowerCase().trim();
  const activeSection = document.querySelector('.card-grid:not(.hidden)');
  if (!activeSection) return;
  let visible = 0;
  activeSection.querySelectorAll('.card').forEach(card => {
    const match = card.dataset.name.includes(query);
    card.classList.toggle('hidden', !match);
    if (match) visible++;
  });
  document.getElementById('no-results')?.classList.toggle('hidden', visible > 0);
}
searchInput?.addEventListener('input', filterCards);
tabs.forEach(tab => tab.addEventListener('click', () => {
  tabs.forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  document.querySelectorAll('.card-grid').forEach(s =>
    s.classList.toggle('hidden', s.id !== tab.dataset.tab));
  filterCards();
}));

// ---------- 3. Показ/скрытие пароля (доп. интерактивность №3) ----------
document.querySelectorAll('.toggle-password').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    input.type = input.type === 'password' ? 'text' : 'password';
  });
});

// ---------- 4. Клиентская валидация регистрации ----------
const form = document.getElementById('register-form');

function setError(id, message) {
  const input = document.getElementById(id);
  const errorEl = document.getElementById(id + '-error');
  if (errorEl) errorEl.textContent = message;
  input?.classList.toggle('invalid', Boolean(message));
}

if (form) {
  form.addEventListener('submit', (event) => {
    event.preventDefault(); // не даём форме отправиться до проверки
    let ok = true;
    const value = id => document.getElementById(id).value.trim();

    // обязательность всех полей
    ['fullname', 'email', 'login', 'password', 'password2'].forEach(id => {
      if (!value(id)) { setError(id, 'Заполните это поле'); ok = false; }
      else setError(id, '');
    });

    // формат email
    const email = value('email');
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('email', 'Некорректный email, пример: ivan@mail.ru'); ok = false;
    }
    // длина пароля
    const pass = document.getElementById('password').value;
    if (pass && pass.length < 8) {
      setError('password', 'Пароль должен быть не короче 8 символов'); ok = false;
    }
    // совпадение паролей
    const pass2 = document.getElementById('password2').value;
    if (pass2 && pass !== pass2) {
      setError('password2', 'Пароли не совпадают'); ok = false;
    }

    document.getElementById('form-success').classList.toggle('hidden', !ok);
    // при ошибках форма НЕ считается отправленной; пользователь исправляет и жмёт снова
  });
}