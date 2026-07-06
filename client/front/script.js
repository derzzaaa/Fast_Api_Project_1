


let cart = [];
let token = localStorage.getItem("token") || null;
let username = localStorage.getItem("username") || null;

document.addEventListener("DOMContentLoaded", () => {
    
    const savedCart = localStorage.getItem("coffee_cart");
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
        } catch (e) {
            console.error("Ошибка парсинга корзины из кэша:", e);
            cart = [];
        }
    }
    
    
    updateAuthUI();
    updateCartUI();
    setupEventListeners();
});




function setupEventListeners() {
    
    const addButtons = document.querySelectorAll(".menu-card .add-to-cart-btn");
    addButtons.forEach(button => {
        button.addEventListener("click", (e) => {
            const card = e.target.closest(".menu-card");
            if (!card) return;

            const name = card.querySelector(".card-title").textContent.trim();
            const priceText = card.querySelector(".card-price").textContent.trim();
            const price = parseFloat(priceText.replace(/[^0-9]/g, ""));
            const image = card.querySelector("img").src;

            addToCart(name, price, image);
        });
    });

    
    const checkoutBtn = document.querySelector(".checkout-btn");
    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", handleCheckout);
    }

    
    const authModal = document.getElementById("auth-modal");
    const profileTrigger = document.getElementById("profile-trigger");
    const closeAuthModal = document.getElementById("close-auth-modal");
    const authModalOverlay = document.getElementById("auth-modal-overlay");

    
    if (profileTrigger) {
        profileTrigger.addEventListener("click", () => {
            authModal.style.display = "flex";
            updateAuthModalView();
        });
    }

    
    const closeActions = [closeAuthModal, authModalOverlay];
    closeActions.forEach(element => {
        if (element) {
            element.addEventListener("click", () => {
                authModal.style.display = "none";
                const modalContent = document.querySelector(".modal-content");
                if (modalContent) modalContent.classList.remove("cabinet-mode");
            });
        }
    });

    
    const orderSuccessModal = document.getElementById("order-success-modal");
    const closeOrderSuccessModal = document.getElementById("close-order-success-modal");
    const orderSuccessOverlay = document.getElementById("order-success-overlay");
    const okOrderBtn = document.getElementById("ok-order-btn");

    const closeSuccessActions = [closeOrderSuccessModal, orderSuccessOverlay, okOrderBtn];
    closeSuccessActions.forEach(element => {
        if (element) {
            element.addEventListener("click", () => {
                orderSuccessModal.style.display = "none";
            });
        }
    });

    
    const switchToRegister = document.getElementById("switch-to-register");
    const switchToLogin = document.getElementById("switch-to-login");
    const loginFormContainer = document.getElementById("login-form-container");
    const registerFormContainer = document.getElementById("register-form-container");

    if (switchToRegister) {
        switchToRegister.addEventListener("click", (e) => {
            e.preventDefault();
            loginFormContainer.style.display = "none";
            registerFormContainer.style.display = "block";
        });
    }

    if (switchToLogin) {
        switchToLogin.addEventListener("click", (e) => {
            e.preventDefault();
            registerFormContainer.style.display = "none";
            loginFormContainer.style.display = "block";
        });
    }

    
    
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }

    
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    
    const logoutTrigger = document.getElementById("logout-trigger");
    if (logoutTrigger) {
        logoutTrigger.addEventListener("click", handleLogout);
    }

    
    const tabBtns = document.querySelectorAll(".cabinet-tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabName = btn.getAttribute("data-tab");
            switchCabinetTab(tabName);
        });
    });

    
    const editProfileForm = document.getElementById("edit-profile-form");
    if (editProfileForm) {
        editProfileForm.addEventListener("submit", handleProfileUpdate);
    }
}





async function handleRegister(e) {
    e.preventDefault();
    const loginInput = document.getElementById("register-login").value.trim();
    const usernameInput = document.getElementById("register-username").value.trim();
    const passwordInput = document.getElementById("register-password").value;

    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                login: loginInput,
                username: usernameInput,
                password: passwordInput
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Регистрация успешна! Теперь вы можете войти.");
            
            document.getElementById("register-form").reset();
            document.getElementById("register-form-container").style.display = "none";
            document.getElementById("login-form-container").style.display = "block";
        } else {
            alert(`Ошибка регистрации: ${data.detail || "неизвестная ошибка"}`);
        }
    } catch (err) {
        console.error("Ошибка при отправке запроса регистрации:", err);
        alert("Не удалось связаться с сервером при регистрации.");
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const usernameInput = document.getElementById("login-username").value.trim();
    const passwordInput = document.getElementById("login-password").value;

    
    const formData = new URLSearchParams();
    formData.append("username", usernameInput);
    formData.append("password", passwordInput);

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            token = data.access_token;
            username = usernameInput;

            localStorage.setItem("token", token);
            localStorage.setItem("username", username);

            alert("Вход выполнен успешно!");
            document.getElementById("login-form").reset();
            document.getElementById("auth-modal").style.display = "none";
            
            updateAuthUI();
        } else {
            alert(`Ошибка авторизации: ${data.detail || "неверный логин или пароль"}`);
        }
    } catch (err) {
        console.error("Ошибка при отправке запроса авторизации:", err);
        alert("Не удалось связаться с сервером для входа.");
    }
}

function handleLogout() {
    token = null;
    username = null;
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    
    alert("Вы вышли из профиля.");
    document.getElementById("auth-modal").style.display = "none";
    
    const modalContent = document.querySelector(".modal-content");
    if (modalContent) modalContent.classList.remove("cabinet-mode");
    
    updateAuthUI();
}


function updateAuthUI() {
    const authStatusText = document.getElementById("auth-status-text");
    const profileTrigger = document.getElementById("profile-trigger");

    if (token && username) {
        if (authStatusText) authStatusText.textContent = username;
        if (profileTrigger) profileTrigger.classList.add("logged-in");
    } else {
        if (authStatusText) authStatusText.textContent = "Войти";
        if (profileTrigger) profileTrigger.classList.remove("logged-in");
    }
}


async function updateAuthModalView() {
    const loginFormContainer = document.getElementById("login-form-container");
    const registerFormContainer = document.getElementById("register-form-container");
    const userProfileContainer = document.getElementById("user-profile-container");
    const modalContent = document.querySelector(".modal-content");

    if (token && username) {
        loginFormContainer.style.display = "none";
        registerFormContainer.style.display = "none";
        userProfileContainer.style.display = "block";
        if (modalContent) modalContent.classList.add("cabinet-mode");
        
        switchCabinetTab("orders");
        await fetchUserProfile();
        await fetchMyOrders();
    } else {
        loginFormContainer.style.display = "block";
        registerFormContainer.style.display = "none";
        userProfileContainer.style.display = "none";
        if (modalContent) modalContent.classList.remove("cabinet-mode");
    }
}



function checkAuthError(response) {
    if (response.status === 401) {
        token = null;
        username = null;
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        updateAuthUI();
        
        
        const modalContent = document.querySelector(".modal-content");
        if (modalContent) modalContent.classList.remove("cabinet-mode");
        
        
        document.getElementById("login-form-container").style.display = "block";
        document.getElementById("register-form-container").style.display = "none";
        document.getElementById("user-profile-container").style.display = "none";
        
        alert("Ваша сессия устарела. Пожалуйста, войдите в профиль снова.");
        return true;
    }
    return false;
}

function switchCabinetTab(tabName) {
    const tabBtns = document.querySelectorAll(".cabinet-tab-btn");
    const tabContents = document.querySelectorAll(".cabinet-tab-content");

    tabBtns.forEach(btn => {
        if (btn.getAttribute("data-tab") === tabName) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    tabContents.forEach(content => {
        if (content.id === `tab-${tabName}`) {
            content.style.display = "block";
        } else {
            content.style.display = "none";
        }
    });
}

async function fetchUserProfile() {
    if (!token) return;
    try {
        const response = await fetch("/api/users/me", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.status === 401) {
            checkAuthError(response);
            return;
        }
        if (response.ok) {
            const data = await response.json();
            const editLogin = document.getElementById("edit-login");
            const editUsername = document.getElementById("edit-username");
            const editPassword = document.getElementById("edit-password");
            
            if (editLogin) editLogin.value = data.login;
            if (editUsername) editUsername.value = data.username;
            if (editPassword) editPassword.value = "";
        }
    } catch (err) {
        console.error("Ошибка при получении профиля:", err);
    }
}

async function fetchMyOrders() {
    if (!token) return;
    const ordersListContainer = document.getElementById("my-orders-list");
    if (!ordersListContainer) return;

    ordersListContainer.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-light);">Загрузка заказов...</div>`;

    try {
        const response = await fetch("/api/orders/my", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.status === 401) {
            checkAuthError(response);
            return;
        }
        if (response.ok) {
            const orders = await response.json();
            ordersListContainer.innerHTML = "";
            
            if (orders.length === 0) {
                ordersListContainer.innerHTML = `<div class="orders-empty-msg">У вас пока нет заказов</div>`;
                return;
            }

            orders.sort((a, b) => b.id - a.id);

            orders.forEach(order => {
                let itemsHTML = "";
                let total = 0;
                
                order.items.forEach(item => {
                    const itemTotal = item.price * item.amount;
                    total += itemTotal;
                    itemsHTML += `
                        <div class="order-history-item">
                            <span>${item.name} x${item.amount}</span>
                            <span>${itemTotal} Р</span>
                        </div>
                    `;
                });

                const orderCardHTML = `
                    <div class="order-history-card">
                        <div class="order-history-header">
                            <div class="order-history-num">Заказ #${order.order_number}</div>
                            <div class="order-history-status ${order.status === 'новый' ? 'new' : ''}">${order.status}</div>
                        </div>
                        <div class="order-history-items">
                            ${itemsHTML}
                        </div>
                        <div class="order-history-total">
                            <span>Итого:</span>
                            <span>${total} Р</span>
                        </div>
                    </div>
                `;
                ordersListContainer.insertAdjacentHTML("beforeend", orderCardHTML);
            });
        } else {
            ordersListContainer.innerHTML = `<div class="orders-empty-msg">Не удалось загрузить историю заказов</div>`;
        }
    } catch (err) {
        console.error("Ошибка при загрузке заказов:", err);
        ordersListContainer.innerHTML = `<div class="orders-empty-msg">Ошибка сети при загрузке заказов</div>`;
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    const loginInput = document.getElementById("edit-login").value.trim();
    const usernameInput = document.getElementById("edit-username").value.trim();
    const passwordInput = document.getElementById("edit-password").value;

    const payload = {
        login: loginInput,
        username: usernameInput
    };
    if (passwordInput && passwordInput.length > 0) {
        payload.password = passwordInput;
    }

    try {
        const response = await fetch("/api/users/me", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 401) {
            checkAuthError(response);
            return;
        }

        const data = await response.json();

        if (response.ok) {
            if (data.access_token) {
                token = data.access_token;
                localStorage.setItem("token", token);
            }
            username = data.username;
            localStorage.setItem("username", username);

            alert("Данные профиля успешно обновлены.");
            
            updateAuthUI();
            switchCabinetTab("orders");
            await fetchMyOrders();
        } else {
            alert(`Ошибка обновления: ${data.detail || "не удалось сохранить изменения"}`);
        }
    } catch (err) {
        console.error("Ошибка при отправке запроса обновления профиля:", err);
        alert("Не удалось связаться с сервером при обновлении профиля.");
    }
}





async function handleCheckout() {
    if (cart.length === 0) {
        alert("Ваша корзина пуста!");
        return;
    }

    
    if (!token) {
        alert("Для оформления заказа, пожалуйста, войдите в профиль!");
        
        document.getElementById("auth-modal").style.display = "flex";
        updateAuthModalView();
        return;
    }

    
    
    const orderItemsPayload = {};
    cart.forEach((item, index) => {
        orderItemsPayload[`item_${index + 1}`] = {
            name: item.name,
            price: item.price,
            amount: item.amount
        };
    });

    try {
        
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(orderItemsPayload)
        });

        if (response.status === 401) {
            checkAuthError(response);
            return;
        }

        const data = await response.json();

        if (response.ok) {
            
            document.getElementById("success-order-number").textContent = data.order_number;
            document.getElementById("success-order-user").textContent = data.user_name;
            document.getElementById("success-order-status").textContent = data.status;

            
            const itemsListContainer = document.getElementById("success-order-items-list");
            itemsListContainer.innerHTML = "";
            let total = 0;

            data.items.forEach(item => {
                const itemTotal = item.price * item.amount;
                total += itemTotal;
                
                const itemHTML = `
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                        <span>${item.name} x${item.amount}</span>
                        <span>${itemTotal} Р</span>
                    </div>
                `;
                itemsListContainer.insertAdjacentHTML("beforeend", itemHTML);
            });

            document.getElementById("success-order-total").textContent = `${total} Р`;

            
            document.getElementById("order-success-modal").style.display = "flex";
            
            
            cart = [];
            saveCart();
            updateCartUI();

            
            const cartToggle = document.getElementById("cart-toggle");
            if (cartToggle) cartToggle.checked = false;
        } else {
            alert(`Ошибка оформления заказа: ${data.detail || "не удалось сохранить"}`);
        }
    } catch (err) {
        console.error("Ошибка при отправке заказа:", err);
        alert("Не удалось отправить заказ на сервер.");
    }
}

function addToCart(name, price, image) {
    const existingItem = cart.find(item => item.name === name);

    if (existingItem) {
        existingItem.amount += 1;
    } else {
        cart.push({
            name: name,
            price: price,
            image: image,
            amount: 1
        });
    }

    saveCart();
    updateCartUI();
}

function changeQuantity(name, delta) {
    const item = cart.find(item => item.name === name);
    if (!item) return;

    item.amount += delta;

    if (item.amount <= 0) {
        cart = cart.filter(i => i.name !== name);
    }

    saveCart();
    updateCartUI();
}

function saveCart() {
    localStorage.setItem("coffee_cart", JSON.stringify(cart));
}

function updateCartUI() {
    const cartItemsContainer = document.querySelector(".cart-items");
    const cartBadge = document.querySelector(".cart-badge");
    const totalPriceText = document.querySelector(".total-price");

    if (!cartItemsContainer) return;

    cartItemsContainer.innerHTML = "";

    let totalAmount = 0;
    let totalPrice = 0;

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="cart-empty-msg" style="text-align: center; color: var(--text-light); margin: 3rem 0; font-style: italic;">
                Ваша корзина пока пуста
            </div>
        `;
    } else {
        cart.forEach(item => {
            totalAmount += item.amount;
            totalPrice += item.price * item.amount;

            const cartItemHTML = `
                <div class="cart-item">
                    <img src="${item.image}" alt="${item.name}" class="cart-item-img">
                    <div class="cart-item-details">
                        <div class="cart-item-title">${item.name}</div>
                        <div class="cart-item-price">${item.price * item.amount} ₽</div>
                    </div>
                    <div class="cart-quantity-control">
                        <button class="quantity-btn decrease-btn" data-name="${item.name}">-</button>
                        <span class="quantity-value">${item.amount}</span>
                        <button class="quantity-btn increase-btn" data-name="${item.name}">+</button>
                    </div>
                </div>
            `;
            cartItemsContainer.insertAdjacentHTML("beforeend", cartItemHTML);
        });
    }

    if (cartBadge) {
        cartBadge.textContent = totalAmount;
        cartBadge.style.display = totalAmount > 0 ? "flex" : "none";
    }

    if (totalPriceText) {
        totalPriceText.textContent = `${totalPrice} ₽`;
    }

    const decreaseBtns = cartItemsContainer.querySelectorAll(".decrease-btn");
    const increaseBtns = cartItemsContainer.querySelectorAll(".increase-btn");

    decreaseBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const name = btn.getAttribute("data-name");
            changeQuantity(name, -1);
        });
    });

    increaseBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const name = btn.getAttribute("data-name");
            changeQuantity(name, 1);
        });
    });
}
