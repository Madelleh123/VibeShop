const storeForm = document.getElementById('storeForm');
const uploadForm = document.getElementById('uploadForm');
const uploadSection = document.getElementById('upload-section');
const storeStatus = document.getElementById('storeStatus');
const uploadStatus = document.getElementById('uploadStatus');
const storeInfo = document.getElementById('storeInfo');
const preview = document.getElementById('preview');
const productsList = document.getElementById('productsList');
const changeStoreBtn = document.getElementById('changeStore');
const sourceFile = document.getElementById('sourceFile');
const sourceUrl = document.getElementById('sourceUrl');
const fileInputGroup = document.getElementById('fileInputGroup');
const urlInputGroup = document.getElementById('urlInputGroup');
const welcomePage = document.getElementById('welcome-page');
const mainContent = document.getElementById('main-content');
const getStartedBtn = document.getElementById('getStartedBtn');
const backToWelcomeBtn = document.getElementById('backToWelcomeBtn');
const homeBtn = document.getElementById('homeBtn');
const storeSuccessActions = document.getElementById('storeSuccessActions');
const addProductBtn = document.getElementById('addProductBtn');
const productSuccessActions = document.getElementById('productSuccessActions');
const addAnotherProductBtn = document.getElementById('addAnotherProductBtn');
const viewProductsBtn = document.getElementById('viewProductsBtn');
const existingStoreCode = document.getElementById('existingStoreCode');
const loadStoreBtn = document.getElementById('loadStoreBtn');
const toggleLoadStore = document.getElementById('toggleLoadStore');
const backToCreate = document.getElementById('backToCreate');
const createStoreFields = document.getElementById('createStoreFields');
const loadStoreFields = document.getElementById('loadStoreFields');

let selectedSource = 'file';
let currentStore = null;
const apiBase = '/api/portal';
const activeStoreKey = 'active_store_code';

function isValidStoreCode(code) {
    return typeof code === 'string' && /^VIBE-[A-Z0-9]{5}$/.test(code.trim());
}

function getActiveStoreCode() {
    try {
        const code = localStorage.getItem(activeStoreKey);
        return isValidStoreCode(code) ? code.trim() : null;
    } catch (err) {
        return null;
    }
}

function saveActiveStoreCode(storeCode) {
    try {
        localStorage.setItem(activeStoreKey, storeCode);
    } catch (err) {
        console.warn('Unable to save active store code', err);
    }
}

function clearActiveStoreCode() {
    try {
        localStorage.removeItem(activeStoreKey);
    } catch (err) {
        console.warn('Unable to clear active store code', err);
    }
}

function showPortalScreen() {
    welcomePage.classList.add('hidden');
    mainContent.classList.remove('hidden');
    if (homeBtn) homeBtn.style.display = 'inline-flex';
}

function showWelcomeScreen() {
    mainContent.classList.add('hidden');
    welcomePage.classList.remove('hidden');
    if (homeBtn) homeBtn.style.display = 'none';
}

function setStatus(element, role, msg) {
    element.className = `status ${role}`;
    element.textContent = msg;
    element.style.display = 'block';
    if (role === 'success') {
        setTimeout(() => { element.style.display = 'none'; }, 4000);
    }
}

function hideStatus(element) {
    if (!element) return;
    element.style.display = 'none';
}

function showUploadSection(storeName, storeCode) {
    currentStore = { name: storeName, code: storeCode };
    uploadSection.style.display = 'block';
    document.getElementById('store-section').style.display = 'none';
    if (storeInfo) {
        const codeDisplay = storeCode ? ` (Code: ${storeCode})` : '';
        storeInfo.textContent = `Managing store: ${storeName}${codeDisplay}`;
    }
    hideStatus(storeStatus);
    hideStatus(uploadStatus);
    if (storeSuccessActions) storeSuccessActions.style.display = 'none';
    if (productSuccessActions) productSuccessActions.style.display = 'none';
    productsList.innerHTML = `<div class="no-products">Loading products…</div>`;
    loadProducts();
}

function showStoreForm() {
    currentStore = null;
    uploadSection.style.display = 'none';
    document.getElementById('store-section').style.display = 'block';
    document.getElementById('shopName').value = '';
    document.getElementById('phoneNumber').value = '';
    document.getElementById('location').value = '';
    const activeCode = getActiveStoreCode();
    if (existingStoreCode) existingStoreCode.value = activeCode || '';
    if (storeInfo) {
        storeInfo.textContent = activeCode ? `Saved store code available: ${activeCode}` : '';
    }
    // Reset to create mode
    if (createStoreFields) createStoreFields.style.display = 'block';
    if (loadStoreFields) loadStoreFields.style.display = 'none';
    hideStatus(storeStatus);
    hideStatus(uploadStatus);
    if (storeSuccessActions) storeSuccessActions.style.display = 'none';
    if (productSuccessActions) productSuccessActions.style.display = 'none';
}

function resetToStore() {
    currentStore = null;
    uploadSection.style.display = 'none';
    document.getElementById('store-section').style.display = 'block';
    uploadForm.reset();
    preview.innerHTML = '';
    productsList.innerHTML = '';
    if (storeInfo) storeInfo.textContent = '';
    hideStatus(uploadStatus);
    if (storeSuccessActions) storeSuccessActions.style.display = 'none';
    if (productSuccessActions) productSuccessActions.style.display = 'none';
}

function validatePhoneNumber(value) {
    if (!value.startsWith('+')) return false;
    const digits = value.slice(1);
    return /^\d{9,}$/.test(digits);
}

function renderNoProducts() {
    productsList.innerHTML = `
        <div class="no-products">
            <div class="empty-icon">📦</div>
            <h3>You don't have any products yet</h3>
            <p>Add your first product to start selling on VibeShop!</p>
            <button class="btn-primary" type="button" id="focusProductForm">Add Your First Product</button>
        </div>`;
    const focusButton = document.getElementById('focusProductForm');
    if (focusButton) {
        focusButton.addEventListener('click', () => {
            document.getElementById('productName').focus();
            document.getElementById('productName').scrollIntoView({ behavior: 'smooth' });
        });
    }
}

function renderProducts(products) {
    let html = '';
    products.forEach(p => {
        const img = p.image_url || '/portal/no-image.png';
        const desc = p.description || 'No description';
        html += `
            <div class="product-card">
                <img src="${img}" alt="${p.name}" class="product-image" onerror="this.src='/portal/no-image.png'">
                <div class="product-info">
                    <h3>${p.name}</h3>
                    <div class="product-price">${p.price} UGX</div>
                    <div class="product-description">${desc}</div>
                    <small style="color: #666; font-size: 12px;">Store Code: ${currentStore?.code || 'N/A'}</small>
                </div>
                <div class="product-actions">
                    <button class="btn-danger" type="button" data-product-id="${p.product_id}">Delete</button>
                </div>
            </div>`;
    });
    productsList.innerHTML = html;
    document.querySelectorAll('.product-actions button[data-product-id]').forEach((button) => {
        button.addEventListener('click', () => deleteProduct(button.dataset.productId));
    });
}

async function loadProducts() {
    if (!currentStore || !currentStore.code) return;
    productsList.innerHTML = '<div class="no-products">Loading products…</div>';
    try {
        const resp = await fetch(`${apiBase}/products?store_code=${encodeURIComponent(currentStore.code)}`);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.message || 'Failed to load products');
        const products = Array.isArray(data.products) ? data.products : [];
        if (products.length === 0) {
            renderNoProducts();
            return;
        }
        renderProducts(products);
    } catch (err) {
        productsList.innerHTML = `<div class="no-products">⚠️ ${err.message}</div>`;
    }
}

async function deleteProduct(productId) {
    if (!confirm('Delete this product?')) return;
    try {
        const resp = await fetch(`${apiBase}/delete-product`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        const data = await resp.json();
        if (!resp.ok || data.status !== 'success') {
            alert(`Delete failed: ${data.message}`);
            return;
        }
        setStatus(uploadStatus, 'success', 'Product deleted');
        loadProducts();
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

if (sourceFile) {
    sourceFile.addEventListener('click', (e) => {
        e.preventDefault();
        selectedSource = 'file';
        sourceFile.classList.add('active');
        sourceUrl.classList.remove('active');
        fileInputGroup.classList.remove('hidden');
        urlInputGroup.classList.add('hidden');
    });
}
if (sourceUrl) {
    sourceUrl.addEventListener('click', (e) => {
        e.preventDefault();
        selectedSource = 'url';
        sourceUrl.classList.add('active');
        sourceFile.classList.remove('active');
        fileInputGroup.classList.add('hidden');
        urlInputGroup.classList.remove('hidden');
    });
}

async function fetchStoreData(storeCode) {
    try {
        const resp = await fetch(`/store/${encodeURIComponent(storeCode)}`);
        const data = await resp.json();
        if (!resp.ok || data.status !== 'success') return null;
        return data.store || null;
    } catch (err) {
        return null;
    }
}

function setButtonState(button, disabled) {
    if (!button) return;
    button.disabled = disabled;
    button.style.opacity = disabled ? '0.6' : '1';
}

window.addEventListener('DOMContentLoaded', async () => {
    showWelcomeScreen();
    if (getStartedBtn) getStartedBtn.addEventListener('click', showPortalScreen);
    if (backToWelcomeBtn) backToWelcomeBtn.addEventListener('click', showWelcomeScreen);
    if (homeBtn) homeBtn.addEventListener('click', showWelcomeScreen);
    if (changeStoreBtn) changeStoreBtn.addEventListener('click', showStoreForm);
    if (toggleLoadStore) toggleLoadStore.addEventListener('click', (e) => {
        e.preventDefault();
        if (createStoreFields) createStoreFields.style.display = 'none';
        if (loadStoreFields) loadStoreFields.style.display = 'block';
    });
    if (backToCreate) backToCreate.addEventListener('click', () => {
        if (createStoreFields) createStoreFields.style.display = 'block';
        if (loadStoreFields) loadStoreFields.style.display = 'none';
    });
    if (loadStoreBtn) loadStoreBtn.addEventListener('click', async () => {
        hideStatus(storeStatus);
        const code = existingStoreCode?.value.trim().toUpperCase();
        if (!isValidStoreCode(code)) {
            setStatus(storeStatus, 'error', '⚠️ Enter a valid store code like VIBE-ABCDE');
            return;
        }
        setStatus(storeStatus, 'info', '⏳ Looking up store...');
        setButtonState(loadStoreBtn, true);
        const store = await fetchStoreData(code);
        setButtonState(loadStoreBtn, false);
        if (!store) {
            setStatus(storeStatus, 'error', '❌ Store code not found. Please check the code and try again.');
            return;
        }
        saveActiveStoreCode(code);
        showPortalScreen();
        showUploadSection(store.name, code);
    });
    const activeCode = getActiveStoreCode();
    if (activeCode) {
        const store = await fetchStoreData(activeCode);
        if (store) {
            showPortalScreen();
            showUploadSection(store.name, activeCode);
            return;
        }
        clearActiveStoreCode();
        setStatus(storeStatus, 'error', '⚠️ Saved store code is invalid. Please enter a store code or create a new store.');
        showStoreForm();
        return;
    }
});


if (storeForm) {
    storeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideStatus(storeStatus);
        const submitButton = storeForm.querySelector('button[type="submit"]');
        const name = document.getElementById('shopName').value.trim();
        const phone = document.getElementById('phoneNumber').value.trim();
        const location = document.getElementById('location').value.trim();
        if (!name || !phone || !location) {
            setStatus(storeStatus, 'error', '⚠️ Please fill in all required fields (Store Name, Phone Number, and Location)');
            return;
        }
        if (!validatePhoneNumber(phone)) {
            setStatus(storeStatus, 'error', '⚠️ Please enter a valid international phone number: + followed by at least 9 digits');
            return;
        }
        setButtonState(submitButton, true);
        setStatus(storeStatus, 'info', '⏳ Creating store...');
        try {
            const fd = new FormData();
            fd.append('name', name);
            fd.append('phone_number', phone);
            fd.append('location', location);
            const resp = await fetch(`${apiBase}/create-store`, { method: 'POST', body: fd });
            const data = await resp.json();
            if (!resp.ok || data.status !== 'success') {
                const errorMsg = data.message || 'Store creation failed';
                if (errorMsg.includes('Database not available')) {
                    setStatus(storeStatus, 'error', `❌ ${errorMsg}\n\nSee DATABASE_SETUP.md in project root for configuration instructions.`);
                } else {
                    setStatus(storeStatus, 'error', `❌ ${errorMsg}`);
                }
                setButtonState(submitButton, false);
                return;
            }
            const storeCode = data.store_code;
            setStatus(storeStatus, 'success', `🎉 Store created successfully!\n\nYour Store Code: ${storeCode}`);
            saveActiveStoreCode(storeCode);
            if (storeSuccessActions) storeSuccessActions.style.display = 'flex';
            if (addProductBtn) {
                addProductBtn.onclick = () => showUploadSection(name, storeCode);
            }
            showUploadSection(name, storeCode);
        } catch (err) {
            setStatus(storeStatus, 'error', `❌ Error: ${err.message}`);
        } finally {
            setButtonState(submitButton, false);
        }
    });
}

if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideStatus(uploadStatus);
        const submitButton = uploadForm.querySelector('button[type="submit"]');
        if (!currentStore || !currentStore.code) {
            setStatus(uploadStatus, 'error', 'No active store selected');
            return;
        }
        const productName = document.getElementById('productName').value.trim();
        const productPrice = document.getElementById('productPrice').value.trim();
        const productDesc = document.getElementById('productDescription').value.trim();
        if (!productName || !productPrice) {
            setStatus(uploadStatus, 'error', '⚠️ Please enter both product name and price');
            return;
        }
        const formData = new FormData();
        formData.append('store_code', currentStore.code);
        formData.append('name', productName);
        formData.append('price', Number(productPrice));
        if (productDesc) formData.append('description', productDesc);
        if (selectedSource === 'file') {
            const imageFile = document.getElementById('productImage').files[0];
            if (!imageFile) {
                setStatus(uploadStatus, 'error', '⚠️ Please select an image file from your device');
                return;
            }
            formData.append('image', imageFile);
            const imgURL = URL.createObjectURL(imageFile);
            preview.innerHTML = `<img src="${imgURL}" alt="Preview" />`;
        } else {
            const imageUrl = document.getElementById('productImageUrl').value.trim();
            if (!imageUrl) {
                setStatus(uploadStatus, 'error', '⚠️ Please enter a valid image URL (e.g., https://example.com/image.jpg)');
                return;
            }
            formData.append('image_url', imageUrl);
            preview.innerHTML = `<img src="${imageUrl}" alt="Preview" />`;
        }
        setButtonState(submitButton, true);
        setStatus(uploadStatus, 'info', '⏳ Adding product...');
        try {
            const resp = await fetch(`${apiBase}/upload-product`, { method: 'POST', body: formData });
            const data = await resp.json();
            if (!resp.ok || data.status !== 'success') {
                setStatus(uploadStatus, 'error', `❌ ${data.message || 'Upload failed'}`);
                return;
            }
            setStatus(uploadStatus, 'success', '🎉 Product added successfully!');
            uploadForm.reset();
            preview.innerHTML = '';
            loadProducts();
            if (productSuccessActions) productSuccessActions.style.display = 'flex';
            if (addAnotherProductBtn) {
                addAnotherProductBtn.onclick = () => {
                    productSuccessActions.style.display = 'none';
                    hideStatus(uploadStatus);
                    document.getElementById('productName').focus();
                };
            }
            if (viewProductsBtn) {
                viewProductsBtn.onclick = () => {
                    productSuccessActions.style.display = 'none';
                    hideStatus(uploadStatus);
                    loadProducts();
                    document.getElementById('productsList').scrollIntoView({behavior: 'smooth'});
                };
            }
        } catch (err) {
            setStatus(uploadStatus, 'error', `❌ Error: ${err.message}`);
        } finally {
            setButtonState(submitButton, false);
        }
    });
}
