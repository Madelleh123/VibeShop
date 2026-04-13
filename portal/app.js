const storeForm = document.getElementById('storeForm');
const uploadForm = document.getElementById('uploadForm');
const uploadSection = document.getElementById('upload-section');
const storeStatus = document.getElementById('storeStatus');
const uploadStatus = document.getElementById('uploadStatus');
const storeInfo = document.getElementById('storeInfo');
const preview = document.getElementById('preview');
const productsList = document.getElementById('productsList');
const sourceFile = document.getElementById('sourceFile');
const sourceUrl = document.getElementById('sourceUrl');
const fileInputGroup = document.getElementById('fileInputGroup');
const urlInputGroup = document.getElementById('urlInputGroup');
const welcomePage = document.getElementById('welcome-page');
const mainContent = document.getElementById('main-content');
const getStartedBtn = document.getElementById('getStartedBtn');

let selectedSource = 'file';
let currentStore = null;

const apiBase = '/api/portal';

// --- Welcome Page Handler ---
function showMainContent() {
    welcomePage.classList.add('hidden');
    mainContent.classList.remove('hidden');
}

function showWelcomePage() {
    welcomePage.classList.remove('hidden');
    mainContent.classList.add('hidden');
}

// --- Initialize Page ---
window.addEventListener('DOMContentLoaded', showWelcomePage);

getStartedBtn.addEventListener('click', showMainContent);

const backToWelcomeBtn = document.getElementById('backToWelcomeBtn');
if (backToWelcomeBtn) {
    backToWelcomeBtn.addEventListener('click', showWelcomePage);
}

// --- Status Message Handler ---
function setStatus(element, role, msg) {
    element.className = `status ${role}`;
    element.textContent = msg;
    element.style.display = 'block';
    
    if (role === 'success') {
        setTimeout(() => { element.style.display = 'none'; }, 4000);
    }
}

function hideStatus(element) {
    element.style.display = 'none';
}

// --- Store Display ---
function showUploadSection(storeId, storeName) {
    currentStore = { id: storeId, name: storeName };
    storeInfo.innerHTML = `<strong>Store:</strong> ${storeName} <em>(ID: ${storeId})</em>`;
    uploadSection.style.display = 'block';
    document.getElementById('store-section').style.display = 'none';
    hideStatus(storeStatus);
    hideStatus(uploadStatus);
    loadProducts();
}

function resetToStore() {
    currentStore = null;
    uploadSection.style.display = 'none';
    document.getElementById('store-section').style.display = 'block';
    storeForm.reset();
    uploadForm.reset();
    preview.innerHTML = '';
    productsList.innerHTML = '';
    hideStatus(uploadStatus);
    localStorage.removeItem('vibeshop_store_id');
    localStorage.removeItem('vibeshop_store_name');
}

// --- Product Management ---
async function loadProducts() {
    if (!currentStore) return;
    
    try {
        const resp = await fetch(`${apiBase}/products?store_id=${currentStore.id}`);
        if (!resp.ok) throw new Error('Failed to load products');
        
        const data = await resp.json();
        const products = data.products || [];
        
        if (products.length === 0) {
            productsList.innerHTML = '<div class="no-products">📦 No products yet. Add your first one above!</div>';
            return;
        }
        
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
                    </div>
                    <div class="product-actions">
                        <button class="btn-danger" onclick="deleteProduct(${p.product_id})">Delete</button>
                    </div>
                </div>
            `;
        });
        productsList.innerHTML = html;
    } catch (err) {
        productsList.innerHTML = `<div class="no-products">⚠️ Error loading products: ${err.message}</div>`;
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

// --- Image Source Toggle ---
sourceFile.addEventListener('click', (e) => {
    e.preventDefault();
    selectedSource = 'file';
    sourceFile.classList.add('active');
    sourceUrl.classList.remove('active');
    fileInputGroup.style.display = 'block';
    urlInputGroup.style.display = 'none';
});

sourceUrl.addEventListener('click', (e) => {
    e.preventDefault();
    selectedSource = 'url';
    sourceUrl.classList.add('active');
    sourceFile.classList.remove('active');
    fileInputGroup.style.display = 'none';
    urlInputGroup.style.display = 'block';
});

// --- Check for Stored Store ---
if (localStorage.getItem('vibeshop_store_id')) {
    showUploadSection(
        parseInt(localStorage.getItem('vibeshop_store_id')),
        localStorage.getItem('vibeshop_store_name')
    );
}

// --- Store Creation ---
storeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideStatus(storeStatus);
    
    const name = document.getElementById('shopName').value.trim();
    const phone = document.getElementById('phoneNumber').value.trim();
    const location = document.getElementById('location').value.trim();
    
    if (!name || !phone || !location) {
        setStatus(storeStatus, 'error', '⚠️ Fill in all fields');
        return;
    }

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
            
            // Check for database error
            if (errorMsg.includes('Database not available')) {
                setStatus(storeStatus, 'error', 
                    `❌ ${errorMsg}\n\nSee DATABASE_SETUP.md in project root for configuration instructions.`);
            } else {
                setStatus(storeStatus, 'error', `❌ ${errorMsg}`);
            }
            return;
        }
        
        setStatus(storeStatus, 'success', '✅ Store created! Now add your first product.');
        localStorage.setItem('vibeshop_store_id', data.store_id);
        localStorage.setItem('vibeshop_store_name', name);
        
        setTimeout(() => showUploadSection(data.store_id, name), 800);
    } catch (err) {
        setStatus(storeStatus, 'error', `❌ Error: ${err.message}`);
    }
});

// --- Product Upload ---
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideStatus(uploadStatus);
    
    if (!currentStore) {
        setStatus(uploadStatus, 'error', 'No store selected');
        return;
    }

    const productName = document.getElementById('productName').value.trim();
    const productPrice = document.getElementById('productPrice').value.trim();
    const productDesc = document.getElementById('productDescription').value.trim();

    if (!productName || !productPrice) {
        setStatus(uploadStatus, 'error', '⚠️ Enter product name and price');
        return;
    }

    let formData = new FormData();
    formData.append('store_id', currentStore.id);
    formData.append('name', productName);
    formData.append('price', Number(productPrice));
    if (productDesc) formData.append('description', productDesc);

    if (selectedSource === 'file') {
        const imageFile = document.getElementById('productImage').files[0];
        if (!imageFile) {
            setStatus(uploadStatus, 'error', '⚠️ Select an image file');
            return;
        }
        formData.append('image', imageFile);
        const imgURL = URL.createObjectURL(imageFile);
        preview.innerHTML = `<img src="${imgURL}" alt="Preview" />`;
    } else {
        const imageUrl = document.getElementById('productImageUrl').value.trim();
        if (!imageUrl) {
            setStatus(uploadStatus, 'error', '⚠️ Enter image URL');
            return;
        }
        formData.append('image_url', imageUrl);
        preview.innerHTML = `<img src="${imageUrl}" alt="Preview" />`;
    }

    setStatus(uploadStatus, 'info', '⏳ Uploading product...');
    
    try {
        const resp = await fetch(`${apiBase}/upload-product`, { method: 'POST', body: formData });
        const data = await resp.json();
        
        if (!resp.ok || data.status !== 'success') {
            setStatus(uploadStatus, 'error', `❌ ${data.message || 'Upload failed'}`);
            return;
        }
        
        setStatus(uploadStatus, 'success', `✅ Product added: ${data.product.name}`);
        uploadForm.reset();
        if (selectedSource === 'file') preview.innerHTML = '';
        
        setTimeout(() => loadProducts(), 500);
    } catch (err) {
        setStatus(uploadStatus, 'error', `❌ Error: ${err.message}`);
    }
});

// --- Change Store ---
document.getElementById('changeStore').addEventListener('click', () => {
    resetToStore();
});

