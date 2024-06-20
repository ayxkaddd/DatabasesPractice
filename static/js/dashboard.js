async function fetchData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    return await response.json();
}

async function submitForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const category = formData.get('category');
    const name = formData.get('name');
    const price = formData.get('price');
    const imageFile = formData.get('image');

    try {
        const addItemResponse = await fetch('/api/add_new_item/', {
            method: 'POST',
            body: new URLSearchParams({
                'category': category,
                'name': name,
                'price': price
            })
        });

        if (!addItemResponse.ok) {
            throw new Error('Failed to add new item');
        }

        const newItem = await addItemResponse.json();

        const uploadFormData = new FormData();
        uploadFormData.append('file', imageFile);

        const uploadResponse = await fetch(`/api/upload_image/?item_id=${newItem.item_id}`, {
            method: 'POST',
            body: uploadFormData
        });

        if (!uploadResponse.ok) {
            throw new Error('Failed to upload image');
        }

        window.location.reload();

    } catch (error) {
        console.error('Error adding new item:', error);
    }
}


async function populateTable(data, tableBodyId, extraColumn = false) {
    const tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = '';
    data.forEach(item => {
        const row = document.createElement('tr');
        Object.keys(item).forEach(key => {
            const cell = document.createElement('td');
            cell.textContent = item[key];
            row.appendChild(cell);
        });
        if (extraColumn) {
            const actionCell = document.createElement('td');
            const button = document.createElement('button');
            button.textContent = 'View Orders';
            button.onclick = () => fetchOrderHistory(item.customer_id);
            actionCell.appendChild(button);
            row.appendChild(actionCell);
        }
        tableBody.appendChild(row);
    });
}

async function fetchOrderHistory(customerId) {
    try {
        const orderHistory = await fetchData(`/api/order_history/${customerId}`);
        await populateTable(orderHistory, 'order-history-body');
    } catch (error) {
        console.error('Failed to fetch order history:', error);
    }
}

function showSection(sectionId) {
    document.querySelectorAll('.container').forEach(container => {
        container.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

function createMenuItemElement(item) {
    const menuItemDiv = document.createElement('div');
    menuItemDiv.className = 'menu-item';
    menuItemDiv.dataset.itemId = item.item_id;

    const img = document.createElement('img');
    img.src = `/static/images/${item.item_id}.jpg`;
    img.alt = item.name;

    const title = document.createElement('h3');
    title.textContent = item.name;

    const category = document.createElement('p');
    category.textContent = item.category;

    const price = document.createElement('p');
    price.textContent = `${item.price} UAH`;

    menuItemDiv.appendChild(img);
    menuItemDiv.appendChild(title);
    menuItemDiv.appendChild(category);
    menuItemDiv.appendChild(price);

    menuItemDiv.addEventListener('click', () => {
        addItemToOrder(item);
    });

    return menuItemDiv;
}

let selectedItems = [];

function addItemToOrder(item) {
    const existingItem = selectedItems.find(i => i.item_id === item.item_id);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        selectedItems.push({ ...item, quantity: 1 });
    }
    updateSelectedItemsList();
    updateTotalAmount();
    calculateChange();
}


function updateSelectedItemsList() {
    const selectedItemsList = document.getElementById('selected-items-list');
    selectedItemsList.innerHTML = '';

    selectedItems.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'selected-item';

        const itemName = document.createElement('span');
        itemName.textContent = `${item.name} (x${item.quantity})`;

        const increaseButton = document.createElement('button');
        increaseButton.textContent = '+';
        increaseButton.addEventListener('click', () => {
            item.quantity++;
            updateSelectedItemsList();
            updateTotalAmount();
        });

        const decreaseButton = document.createElement('button');
        decreaseButton.textContent = '-';
        decreaseButton.addEventListener('click', () => {
            item.quantity--;
            if (item.quantity === 0) {
                selectedItems = selectedItems.filter(i => i.item_id !== item.item_id);
            }
            updateSelectedItemsList();
            updateTotalAmount();
        });

        itemDiv.appendChild(itemName);
        itemDiv.appendChild(increaseButton);
        itemDiv.appendChild(decreaseButton);

        selectedItemsList.appendChild(itemDiv);
    });
}


function updateTotalAmount() {
    const totalAmount = selectedItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    document.getElementById('totalAmount').textContent = totalAmount;
}

async function handleCustomerInput(event) {
    const searchTerm = event.target.value;
    const customersList = document.getElementById('customers-list');
    customersList.innerHTML = '';

    if (searchTerm.length > 2) {
        const customers = await fetchData(`/api/customers/search/?search_query=${searchTerm}`);
        customers.forEach(customer => {
            console.log(customer)
            const option = document.createElement('option');
            option.value = `${customer.first_name} ${customer.last_name} ${customer.customer_id}`;
            customersList.appendChild(option);
        });
    }
}

function calculateChange() {
    const totalAmount = selectedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const cashGiven = parseFloat(document.getElementById('cash-given').value);
    const change = cashGiven - totalAmount;
    document.getElementById('change').textContent = `Change: ${change.toFixed(2)} UAH`;
}

document.getElementById('customer').addEventListener('input', handleCustomerInput);

document.getElementById('cash-button').addEventListener('click', () => {
    document.getElementById('cash-details').style.display = 'block';
    document.getElementById('cash-given').addEventListener('input', calculateChange);
});

document.getElementById('credit-card-button').addEventListener('click', () => {
    document.getElementById('cash-details').style.display = 'none';
});

function calculateChange() {
    const totalAmount = selectedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const cashGiven = parseFloat(document.getElementById('cash-given').value);
    const change = cashGiven - totalAmount;
    document.getElementById('change').textContent = `Change: ${change.toFixed(2)} UAH`;
}


async function submitOrder(event) {
    event.preventDefault();

    const customerInput = document.getElementById('customer').value.split(' ');
    const firstName = customerInput[0];
    const lastName = customerInput[1];
    const customerId = customerInput[2] || null;

    console.log(firstName, lastName, customerId)

    const paymentMethod = document.getElementById('cash-details').style.display === 'none' ? 'credit_card' : 'cash';
    const cashGiven = paymentMethod === 'cash' ? parseFloat(document.getElementById('cash-given').value) : 0;
    const totalMoney = selectedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    const order = {
        customer: {
            customer_id: customerId || null,
            first_name: firstName,
            last_name: lastName
        },
        payment_method: paymentMethod,
        total_money: cashGiven || totalMoney,
        items: selectedItems.map(item => ({ item_id: item.item_id, quantity: item.quantity }))
    };

    try {
        const response = await fetch('/api/order_add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(order)
        });
        const data = await response.json();
        alert('Order added successfully');
    } catch (error) {
        console.error('Error adding order:', error);
    }
}

document.getElementById('addOrderForm').addEventListener('submit', submitOrder);

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const categorySelect = document.getElementById('category');
        const categories = await fetchData("/api/categories/");
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.name;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });

        document.getElementById('addItemForm').addEventListener('submit', submitForm);

        const menuItems = await fetchData('/api/menu_items/');
        await populateTable(menuItems, 'menu-items-body');

        const popularMenuItems = await fetchData('/api/popular_menu_items/');
        await populateTable(popularMenuItems, 'popular-menu-items-body');

        const customers = await fetchData('/api/customers/');
        await populateTable(customers, 'customers-body', true);

        const regularCustomers = await fetchData('/api/regular_customers/');
        await populateTable(regularCustomers, 'regular-customers-body');

        const menuGrid = document.getElementById('menu-grid');
        menuItems.forEach(item => {
            const menuItemElement = createMenuItemElement(item);
            menuGrid.appendChild(menuItemElement);
        });

        showSection('menu-items');

    } catch (error) {
        console.error('Failed to fetch data:', error);
    }
});
