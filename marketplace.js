// Cataloro Marketplace JavaScript
(function($) {
    'use strict';

    let currentUser = null;
    let authToken = localStorage.getItem('marketplace_token');

    // Initialize marketplace functionality
    $(document).ready(function() {
        initializeMarketplace();
        setupEventListeners();
        
        // Check if user is logged in
        if (authToken) {
            updateCartCount();
        }
    });

    function initializeMarketplace() {
        // Load products on home page
        if ($('#marketplace-home').length) {
            loadCategories();
            loadProducts();
        }
        
        // Load cart if on cart page
        if ($('#marketplace-cart').length && authToken) {
            loadCart();
        }
        
        // Load dashboard if on dashboard page
        if ($('#marketplace-dashboard').length && authToken) {
            loadUserOrders();
        }
    }

    function setupEventListeners() {
        // Authentication
        $('#login-form').on('submit', handleLogin);
        $('#register-form').on('submit', handleRegister);
        $('#login-tab, #register-tab').on('click', toggleAuthForm);
        
        // Search and filters
        $('#search-input').on('input', debounce(searchProducts, 300));
        $('#category-filter, #listing-type-filter').on('change', loadProducts);
        
        // Cart
        $(document).on('click', '.add-to-cart', addToCart);
        $(document).on('click', '.remove-from-cart', removeFromCart);
        
        // Dashboard tabs
        $('.tab-btn').on('click', switchTab);
    }

    // Authentication Functions
    function handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        apiRequest('/auth/login', 'POST', data)
            .then(response => {
                if (response.access_token) {
                    authToken = response.access_token;
                    currentUser = response.user;
                    localStorage.setItem('marketplace_token', authToken);
                    showSuccess('Welcome back!');
                    redirectToHome();
                } else {
                    showError('Login failed. Please check your credentials.');
                }
            })
            .catch(error => {
                showError('Login failed: ' + error.message);
            });
    }

    function handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        apiRequest('/auth/register', 'POST', data)
            .then(response => {
                if (response.access_token) {
                    authToken = response.access_token;
                    currentUser = response.user;
                    localStorage.setItem('marketplace_token', authToken);
                    showSuccess('Account created successfully!');
                    redirectToHome();
                } else {
                    showError('Registration failed.');
                }
            })
            .catch(error => {
                showError('Registration failed: ' + error.message);
            });
    }

    function toggleAuthForm(e) {
        const isLogin = $(e.target).attr('id') === 'login-tab';
        
        $('.tab-btn').removeClass('active');
        $(e.target).addClass('active');
        
        if (isLogin) {
            $('#login-form').show();
            $('#register-form').hide();
        } else {
            $('#login-form').hide();
            $('#register-form').show();
        }
    }

    // Product Functions
    function loadProducts() {
        const search = $('#search-input').val();
        const category = $('#category-filter').val();
        const listingType = $('#listing-type-filter').val();
        
        let endpoint = '/listings?limit=20';
        if (search) endpoint += '&search=' + encodeURIComponent(search);
        if (category) endpoint += '&category=' + encodeURIComponent(category);
        if (listingType) endpoint += '&listing_type=' + encodeURIComponent(listingType);
        
        apiRequest(endpoint)
            .then(products => {
                renderProducts(products);
            })
            .catch(error => {
                showError('Failed to load products: ' + error.message);
            });
    }

    function loadCategories() {
        apiRequest('/categories')
            .then(categories => {
                const select = $('#category-filter');
                categories.forEach(category => {
                    select.append(`<option value="${category}">${category}</option>`);
                });
            })
            .catch(error => {
                console.error('Failed to load categories:', error);
            });
    }

    function renderProducts(products) {
        const container = $('#product-listings, #products-grid');
        
        if (products.length === 0) {
            container.html('<p class="no-products">No products found.</p>');
            return;
        }
        
        const html = products.map(product => `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-image">
                    <img src="${product.images[0] || '/wp-content/plugins/cataloro-marketplace/placeholder.jpg'}" 
                         alt="${product.title}">
                    <div class="product-badges">
                        <span class="badge ${product.listing_type}">${product.listing_type === 'auction' ? 'Auction' : 'Buy Now'}</span>
                    </div>
                </div>
                <div class="product-info">
                    <h3 class="product-title">${product.title}</h3>
                    <p class="product-description">${product.description.substring(0, 100)}...</p>
                    <div class="product-price">
                        ${product.listing_type === 'fixed_price' 
                            ? `$${product.price.toFixed(2)}` 
                            : `Current bid: $${(product.current_bid || product.starting_bid).toFixed(2)}`}
                    </div>
                    <div class="product-meta">
                        <span class="category">${product.category}</span>
                        <span class="condition">${product.condition}</span>
                        <span class="views">${product.views} views</span>
                    </div>
                    <div class="product-actions">
                        <button class="btn view-product" onclick="viewProduct('${product.id}')">View Details</button>
                        ${product.listing_type === 'fixed_price' 
                            ? `<button class="btn add-to-cart" data-product-id="${product.id}">Add to Cart</button>`
                            : `<button class="btn place-bid" data-product-id="${product.id}">Place Bid</button>`}
                    </div>
                </div>
            </div>
        `).join('');
        
        container.html(html);
    }

    function searchProducts() {
        loadProducts();
    }

    // Cart Functions
    function addToCart(e) {
        if (!authToken) {
            showError('Please log in to add items to cart.');
            return;
        }
        
        const productId = $(e.target).data('product-id');
        const data = {
            listing_id: productId,
            quantity: 1
        };
        
        apiRequest('/cart', 'POST', data)
            .then(response => {
                showSuccess('Item added to cart!');
                updateCartCount();
            })
            .catch(error => {
                showError('Failed to add to cart: ' + error.message);
            });
    }

    function loadCart() {
        apiRequest('/cart')
            .then(cartItems => {
                renderCart(cartItems);
            })
            .catch(error => {
                showError('Failed to load cart: ' + error.message);
            });
    }

    function renderCart(cartItems) {
        const container = $('#cart-items');
        const summary = $('#cart-summary');
        
        if (cartItems.length === 0) {
            container.html('<p>Your cart is empty.</p>');
            summary.hide();
            return;
        }
        
        let total = 0;
        const html = cartItems.map(item => {
            const itemTotal = item.listing.price * item.cart_item.quantity;
            total += itemTotal;
            
            return `
                <div class="cart-item" data-item-id="${item.cart_item.id}">
                    <img src="${item.listing.images[0] || '/placeholder.jpg'}" alt="${item.listing.title}">
                    <div class="item-details">
                        <h4>${item.listing.title}</h4>
                        <p>$${item.listing.price.toFixed(2)} x ${item.cart_item.quantity}</p>
                        <p class="item-total">$${itemTotal.toFixed(2)}</p>
                    </div>
                    <button class="remove-from-cart btn-small" data-item-id="${item.cart_item.id}">Remove</button>
                </div>
            `;
        }).join('');
        
        container.html(html);
        $('#cart-total').text(total.toFixed(2));
        summary.show();
    }

    function removeFromCart(e) {
        const itemId = $(e.target).data('item-id');
        
        apiRequest(`/cart/${itemId}`, 'DELETE')
            .then(() => {
                showSuccess('Item removed from cart.');
                loadCart();
            })
            .catch(error => {
                showError('Failed to remove item: ' + error.message);
            });
    }

    // Dashboard Functions
    function switchTab(e) {
        const tabName = $(e.target).data('tab');
        
        $('.tab-btn').removeClass('active');
        $(e.target).addClass('active');
        
        $('.tab-content').removeClass('active');
        $(`#${tabName}-tab`).addClass('active');
        
        // Load content based on tab
        switch(tabName) {
            case 'orders':
                loadUserOrders();
                break;
            case 'listings':
                loadUserListings();
                break;
            case 'profile':
                loadUserProfile();
                break;
        }
    }

    function loadUserOrders() {
        apiRequest('/orders')
            .then(orders => {
                renderUserOrders(orders);
            })
            .catch(error => {
                showError('Failed to load orders: ' + error.message);
            });
    }

    function renderUserOrders(orders) {
        const container = $('#user-orders');
        
        if (orders.length === 0) {
            container.html('<p>No orders found.</p>');
            return;
        }
        
        const html = orders.map(orderData => `
            <div class="order-item">
                <h4>Order #${orderData.order.id}</h4>
                <p><strong>Item:</strong> ${orderData.listing ? orderData.listing.title : 'N/A'}</p>
                <p><strong>Total:</strong> $${orderData.order.total_amount.toFixed(2)}</p>
                <p><strong>Status:</strong> <span class="status ${orderData.order.status}">${orderData.order.status}</span></p>
                <p><strong>Date:</strong> ${new Date(orderData.order.created_at).toLocaleDateString()}</p>
            </div>
        `).join('');
        
        container.html(html);
    }

    function loadUserListings() {
        // Placeholder for loading user listings
        $('#user-listings').html('<p>My listings functionality coming soon...</p>');
    }

    function loadUserProfile() {
        // Placeholder for loading user profile
        $('#user-profile').html('<p>Profile settings coming soon...</p>');
    }

    // Utility Functions
    function apiRequest(endpoint, method = 'GET', data = null) {
        const url = marketplace_ajax.api_base_url + endpoint;
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (authToken) {
            options.headers['Authorization'] = 'Bearer ' + authToken;
        }
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
    }

    function showSuccess(message) {
        // Create or update success notification
        showNotification(message, 'success');
    }

    function showError(message) {
        // Create or update error notification
        showNotification(message, 'error');
    }

    function showNotification(message, type) {
        // Remove existing notifications
        $('.marketplace-notification').remove();
        
        const notification = $(`
            <div class="marketplace-notification ${type}">
                ${message}
                <button class="close-notification">&times;</button>
            </div>
        `);
        
        $('body').prepend(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.fadeOut(() => notification.remove());
        }, 5000);
        
        // Manual close
        notification.find('.close-notification').click(() => {
            notification.fadeOut(() => notification.remove());
        });
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function redirectToHome() {
        window.location.href = '/marketplace/';
    }

    function updateCartCount() {
        if (!authToken) return;
        
        apiRequest('/cart')
            .then(cartItems => {
                const count = cartItems.length;
                $('.cart-count').text(count);
                if (count > 0) {
                    $('.cart-count').show();
                } else {
                    $('.cart-count').hide();
                }
            })
            .catch(error => {
                console.error('Failed to update cart count:', error);
            });
    }

    // Global functions
    window.viewProduct = function(productId) {
        window.location.href = `/marketplace-product/${productId}/`;
    };

    window.logout = function() {
        authToken = null;
        currentUser = null;
        localStorage.removeItem('marketplace_token');
        showSuccess('Logged out successfully.');
        redirectToHome();
    };

})(jQuery);