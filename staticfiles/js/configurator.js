// Конфигуратор ПК: динамическое добавление/удаление компонентов, обновление сборки

// --- SVG-иконки для sidebar ---
const CATEGORY_ICONS = {
  'Видеокарта': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="10" rx="2"/><circle cx="7.5" cy="12" r="1.5"/><circle cx="16.5" cy="12" r="1.5"/></svg>`,
  'Процессор': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/></svg>`,
  'Материнская плата': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h10v10H7z"/></svg>`,
  'Накопитель': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="4" y="7" width="16" height="10" rx="2"/><path d="M8 11h8v2H8z"/></svg>`,
  'Корпус': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9 7h6"/></svg>`,
  'Оперативная память': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="10" rx="2"/><path d="M7 10h2v4H7zM15 10h2v4h-2z"/></svg>`,
  'Система охлаждения': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.07-7.07l-1.41 1.41M6.34 17.66l-1.41 1.41m12.02 0l-1.41-1.41M6.34 6.34L4.93 4.93"/></svg>`,
  'Блок питания': `<svg class="w-6 h-6 mr-2 text-[#7a85ff] dark:text-[#7a85ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="10" rx="2"/><path d="M7 12h2v2H7zM15 12h2v2h-2z"/></svg>`,
};

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `mb-4 p-4 rounded-lg shadow-lg transition-all duration-300 ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`;
  toast.textContent = message;
  const container = document.getElementById('toast-container');
  container.appendChild(toast);
  setTimeout(() => toast.classList.add('opacity-0'), 2500);
  setTimeout(() => toast.remove(), 3000);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let selectedCategoryId = null;
let lastSavedBuildId = null;
let allCategories = [];
let allProducts = [];
let currentFilters = {};

// Загрузка категорий с иконками
async function loadCategories() {
  const res = await fetch('/pcbuilder/api/categories/');
  const data = await res.json();
  allCategories = data.categories;
  const list = document.getElementById('category-list');
  list.innerHTML = '';
  data.categories.forEach(cat => {
    const li = document.createElement('li');
    li.innerHTML = `<button class="w-full flex items-center px-4 py-3 rounded-xl transition-colors font-medium text-lg ${selectedCategoryId === cat.id ? 'bg-[#7a85ff] text-white' : 'text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-[#23283a]'}" data-id="${cat.id}">
      ${(CATEGORY_ICONS[cat.name] || '<span class=\'w-6 h-6 mr-2\'>🖥️</span>')}
      <span>${cat.name}</span>
    </button>`;
    li.querySelector('button').onclick = () => {
      selectedCategoryId = cat.id;
      loadCategories();
      loadProducts(cat.id);
    };
    list.appendChild(li);
  });
}

// Загрузка товаров категории
async function loadProducts(categoryId) {
  const res = await fetch(`/pcbuilder/api/products/?category=${categoryId}`);
  const data = await res.json();
  allProducts = data.products;
  renderFilters(data.products);
  renderProducts(data.products);
}

// Рендер фильтров по спецификациям
function renderFilters(products) {
  // Пример: ищем уникальные значения для фильтров
  const filter1 = document.getElementById('filter-1');
  const filter2 = document.getElementById('filter-2');
  filter1.innerHTML = '<option value="">Производитель</option>';
  filter2.innerHTML = '<option value="">Объем памяти</option>';
  const brands = new Set();
  const memory = new Set();
  products.forEach(prod => {
    prod.specs.forEach(s => {
      if (s.specification__name.toLowerCase().includes('производитель')) brands.add(s.value);
      if (s.specification__name.toLowerCase().includes('объем')) memory.add(s.value);
    });
  });
  brands.forEach(b => filter1.innerHTML += `<option value="${b}">${b}</option>`);
  memory.forEach(m => filter2.innerHTML += `<option value="${m}">${m}</option>`);
  filter1.onchange = () => applyFilters();
  filter2.onchange = () => applyFilters();
}

function applyFilters() {
  const brand = document.getElementById('filter-1').value;
  const memory = document.getElementById('filter-2').value;
  let filtered = allProducts;
  if (brand) filtered = filtered.filter(prod => prod.specs.some(s => s.value === brand));
  if (memory) filtered = filtered.filter(prod => prod.specs.some(s => s.value === memory));
  renderProducts(filtered);
}

// Рендер карточек товаров
function renderProducts(products) {
  const list = document.getElementById('products-list');
  list.innerHTML = '';
  if (!products.length) {
    list.innerHTML = '<div class="text-gray-500 dark:text-gray-400 text-center col-span-2">Нет товаров</div>';
    return;
  }
  products.forEach(prod => {
    const card = document.createElement('div');
    card.className = 'flex flex-col h-[400px] bg-gray-100 dark:bg-[#181C27] rounded-2xl p-6 shadow relative';
    card.innerHTML = `
      <div class="w-full h-[160px] bg-gray-200 dark:bg-[#23283a] flex items-center justify-center rounded-xl text-3xl text-[#b0b0b0] dark:text-[#7a8599] font-bold mb-4">300 × 200</div>
      <div class="flex-1 flex flex-col gap-1 overflow-hidden">
        <div class="text-lg font-bold text-gray-900 dark:text-white truncate" title="${prod.name}">${prod.name}</div>
        <div class="text-[#7a85ff] text-base font-semibold mb-1">${prod.price} ₽</div>
        <div class="flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-300 mb-1 max-h-[60px] overflow-y-auto">
          ${(prod.specs || []).map(s => `<span class="truncate"><span class="font-medium">${s.specification__name}:</span> ${s.value}${s.specification__unit ? ' ' + s.specification__unit : ''}</span>`).join('')}
        </div>
      </div>
      <button class="absolute bottom-6 left-6 right-6 px-6 py-2 rounded-xl text-base font-bold transition-colors ${prod.is_selected ? 'bg-[#7a85ff] text-white cursor-not-allowed' : 'bg-[#7a85ff] hover:bg-[#4b1bb3] text-white'} select-product-btn" data-id="${prod.id}" ${prod.is_selected ? 'disabled' : ''}>${prod.is_selected ? 'Выбрано' : 'Выбрать'}</button>
    `;
    card.querySelector('.select-product-btn').onclick = () => addToBuild(prod.id);
    list.appendChild(card);
  });
}

// Загрузка сборки
async function loadBuild() {
  const res = await fetch('/pcbuilder/api/build/');
  const data = await res.json();
  const list = document.getElementById('build-list');
  const total = document.getElementById('build-total');
  list.innerHTML = '';
  if (!data.components.length) {
    list.innerHTML = '<div class="text-gray-500 dark:text-gray-400 text-center">Добавьте компоненты</div>';
    total.textContent = '0 ₽';
    return;
  }
  data.components.forEach(comp => {
    const div = document.createElement('div');
    div.className = 'flex justify-between items-center border border-[#7a85ff] rounded-xl px-4 py-3';
    div.innerHTML = `
      <div>
        <div class="text-gray-400 text-sm font-semibold mb-1">${comp.category_name}</div>
        <div class="text-base font-bold text-white">${comp.product_name}</div>
      </div>
      <div class="flex flex-col items-end">
        <span class="font-bold text-[#7a85ff] text-lg">${comp.price} ₽</span>
        <button class="remove-btn text-red-500 hover:text-red-700 text-xl" title="Удалить" data-id="${comp.product_id}">&times;</button>
      </div>
    `;
    div.querySelector('.remove-btn').onclick = () => removeFromBuild(comp.product_id);
    list.appendChild(div);
  });
  total.textContent = data.total + ' ₽';
}

// Добавить компонент в сборку
async function addToBuild(productId) {
  const res = await fetch('/pcbuilder/api/build/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ product_id: productId })
  });
  const data = await res.json();
  if (data.success) {
    showToast('Компонент добавлен');
    loadBuild();
    loadProducts(selectedCategoryId);
  } else {
    showToast(data.error || 'Ошибка', 'error');
  }
}

// Удалить компонент из сборки
async function removeFromBuild(productId) {
  const res = await fetch('/pcbuilder/api/build/remove/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ product_id: productId })
  });
  const data = await res.json();
  if (data.success) {
    showToast('Компонент удалён');
    loadBuild();
    loadProducts(selectedCategoryId);
  } else {
    showToast(data.error || 'Ошибка', 'error');
  }
}

// Сохранить сборку
async function saveBuild() {
  const res = await fetch('/pcbuilder/api/build/save/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ name: 'Моя сборка' })
  });
  const data = await res.json();
  if (data.success) {
    showToast('Сборка сохранена!');
    lastSavedBuildId = data.build_id;
  } else {
    showToast(data.error || 'Ошибка', 'error');
  }
}

// Добавить сборку в корзину
async function addBuildToCart() {
  if (!lastSavedBuildId) {
    showToast('Сначала сохраните сборку', 'error');
    return;
  }
  const res = await fetch('/pcbuilder/api/build/add_to_cart/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ build_id: lastSavedBuildId })
  });
  const data = await res.json();
  if (data.success) {
    showToast('Сборка добавлена в корзину!');
  } else {
    showToast(data.error || 'Ошибка', 'error');
  }
}

// Получить параметр из URL
function getUrlParam(name) {
  const url = new URL(window.location.href);
  return url.searchParams.get(name);
}

// Загрузить сохранённую конфигурацию и подставить в сборку
async function loadSavedConfigAndApply(configId) {
  console.log('Попытка автозагрузки конфигурации:', configId);
  // Получаем все сохранённые сборки пользователя
  const res = await fetch('/pcbuilder/api/builds/');
  const data = await res.json();
  console.log('Ответ /pcbuilder/api/builds/:', data);
  if (!data.success) return;

  const config = (data.configurations || []).find(c => c.id == configId || c.id == +configId);
  console.log('Найдена конфигурация:', config);
  if (!config) {
    showToast('Конфигурация не найдена', 'error');
    return;
  }

  // Очищаем текущую сборку
  const buildRes = await fetch('/pcbuilder/api/build/');
  const buildData = await buildRes.json();
  for (const comp of buildData.components) {
    console.log('Удаляем компонент:', comp.product_id);
    await fetch('/pcbuilder/api/build/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ product_id: comp.product_id })
    });
  }

  // Добавляем компоненты из сохранённой конфигурации
  for (const comp of config.components) {
    console.log('Добавляем компонент:', comp.product_id);
    await fetch('/pcbuilder/api/build/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ product_id: comp.product_id })
    });
  }

  showToast('Конфигурация загружена!');
  loadBuild();

  // Сбросить параметр load_config из URL
  const url = new URL(window.location.href);
  url.searchParams.delete('load_config');
  window.history.replaceState({}, document.title, url.pathname + url.search);
  console.log('Параметр load_config удалён из URL');
}

// При загрузке страницы — если есть load_config, подгружаем конфиг
const origDomContentLoaded = window.onload;
window.addEventListener('DOMContentLoaded', async () => {
  loadCategories();
  loadBuild();
  document.getElementById('save-build-btn').onclick = saveBuild;
  document.getElementById('add-to-cart-btn').onclick = addBuildToCart;

  const configId = getUrlParam('load_config');
  if (configId) {
    await loadSavedConfigAndApply(configId);
  }
  if (typeof origDomContentLoaded === 'function') origDomContentLoaded();
}); 