let previewItems = [];
let selectedItems = [];

function GetTokenHeader() {
	token = localStorage.getItem("token");
    return `Bearer ${token}`
}

async function fetchData(url) {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            "Authorization": GetTokenHeader(),
        }
    });
    if (!response.ok) {
        window.location.href = '/login/';
    }
    return await response.json();
}

async function submitCategoryForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const category_name = formData.get('category_name');
    console.log(category_name)

    try {
        const category_req = {
            'name': category_name
        }

        const addCategoryResponse = await fetch('/api/categories/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': GetTokenHeader(),
            },
            body: JSON.stringify(category_req)
        });

        console.log(addCategoryResponse);

        if (!addCategoryResponse.ok) {
            throw new Error('Failed to add new category');
        }

        window.location.reload();
    } catch (error) {
        console.error('Error adding new item:', error);
    }
}


function removeItem(index) {
    previewItems.splice(index, 1);
    updatePreviewItemsGrid();
}


function updatePreviewItemsGrid() {
    const previewItemsGrid = document.getElementById('preview-items-grid');
    previewItemsGrid.innerHTML = '';
    previewItems.forEach((item, index) => {
        const menuItemDiv = document.createElement('div');
        menuItemDiv.className = 'menu-item';

        const img = document.createElement('img');
        img.src = item.imageSrc;
        img.alt = item.name;

        const title = document.createElement('h3');
        title.textContent = item.name;

        const category = document.createElement('p');
        category.textContent = item.category;

        const price = document.createElement('p');
        price.textContent = `${item.price} UAH`;

        const removeButton = document.createElement('button');
        removeButton.className = 'remove-button';
        removeButton.textContent = 'X';
        removeButton.onclick = () => removeItem(index);

        menuItemDiv.appendChild(img);
        menuItemDiv.appendChild(title);
        menuItemDiv.appendChild(category);
        menuItemDiv.appendChild(price);
        menuItemDiv.appendChild(removeButton);

        previewItemsGrid.appendChild(menuItemDiv);
    });
}

async function submitAllItems() {
    const itemsToSubmit = previewItems.map(item => ({
        category: item.category,
        name: item.name,
        price: parseInt(item.price)
    }));

    const response = await fetch('/api/add_new_item/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': GetTokenHeader(),
        },
        body: JSON.stringify(itemsToSubmit)
    });

    const result = await response.json();
    if (result && result.length > 0) {
        for (const item of result) {
            const imageFile = previewItems.find(i => i.name === item.name).imageFile;
            const formData = new FormData();
            formData.append('file', imageFile);

            await fetch(`/api/upload_image/?item_id=${item.item_id}`, {
                method: 'POST',
                headers: {
                    'Authorization': GetTokenHeader(),
                },
                body: formData
            });
        }
        alert('All items have been added successfully.');
        previewItems = [];
        updatePreviewItemsGrid();
    } else {
        alert('Failed to submit items.');
    }
}


function addItem() {
    const category = document.getElementById('category').value;
    const name = document.getElementById('name').value;
    const price = document.getElementById('price').value;
    const imageInput = document.getElementById('image');
    const image = imageInput.files[0];

    if (category && name && price && image) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const item = {
                category: category,
                name: name,
                price: price,
                imageSrc: e.target.result,
                imageFile: image
            };
            previewItems.push(item);
            updatePreviewItemsGrid();
        };
        reader.readAsDataURL(image);

        document.getElementById('addItemForm').reset();
    } else {
        alert('Please fill all fields.');
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
        console.log(row);
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

        const quantityAdjust = document.createElement('div');
        quantityAdjust.className = 'quantity-adjust';

        const increaseButton = document.createElement('button');
        increaseButton.textContent = '+';
        increaseButton.addEventListener('click', () => {
            item.quantity++;
            updateSelectedItemsList();
            updateTotalAmount();
            calculateChange();
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
            calculateChange();
        });

        quantityAdjust.appendChild(increaseButton);
        quantityAdjust.appendChild(decreaseButton);

        itemDiv.appendChild(itemName);
        itemDiv.appendChild(quantityAdjust);

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
        const customers = await fetchData(`/api/customers/${searchTerm}/`);
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
    document.getElementById('change').textContent = `${change.toFixed(2)}`;
}


async function submitOrder(event) {
    event.preventDefault();

    const customerInput = document.getElementById('customer').value.split(' ');
    const firstName = customerInput[0];
    const lastName = customerInput[1];
    const customerId = customerInput[2] || null;

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
                'Content-Type': 'application/json',
                'Authorization': GetTokenHeader(),
            },
            body: JSON.stringify(order)
        });
        const data = await response.json();
        alert('Order added successfully');
    } catch (error) {
        console.error('Error adding order:', error);
    }
}

function updateFileName(input) {
    const fileName = input.files[0]?.name;
    const fileNameDisplay = input.parentElement.querySelector('.file-name');
    fileNameDisplay.textContent = fileName || '';
}

function GenerateRandomPwd() {
    const length = 12;
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~`|}{[]:;?><,./-=";
    let password = "";
    for (let i = 0, n = charset.length; i < length; ++i) {
        password += charset.charAt(Math.floor(Math.random() * n));
    }
    document.getElementById('password').value = password;
}


async function SubmitEmployeeForm() {
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const password = document.getElementById('password').value;

    const employee = {
        first_name: firstName,
        last_name: lastName,
        password: password
    };

    try {
        const response = await fetch('/api/employees/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': GetTokenHeader(),
            },
            body: JSON.stringify(employee)
        });

        if (response.ok) {
            alert('Employee added successfully!');
            document.getElementById('addItemForm').reset(); // Reset form after successful submission
        } else {
            const errorData = await response.json();
            alert('Failed to add employee: ' + errorData.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.');
    }
}

document.getElementById('addOrderForm').addEventListener('submit', submitOrder);

document.addEventListener('DOMContentLoaded', async () => {
    showSection('menu-items');
    try {
        const categorySelect = document.getElementById('category');
        const categories = await fetchData("/api/categories/");
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.name;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });

        document.getElementById('addCategoryForm').addEventListener('submit', submitCategoryForm);

        const menuItems = await fetchData('/api/menu_items/');
        await populateTable(menuItems, 'menu-items-body');

        const popularMenuItems = await fetchData('/api/popular_menu_items/');
        await populateTable(popularMenuItems, 'popular-menu-items-body');

        const customers = await fetchData('/api/customers/');
        await populateTable(customers, 'customers-body', true);

        const regularCustomers = await fetchData('/api/regular_customers/');
        await populateTable(regularCustomers, 'regular-customers-body');

        const employees = await fetchData('/api/employees/');
        await populateTable(employees, 'employees-body');

        const menuGrid = document.getElementById('menu-grid');
        menuItems.forEach(item => {
            const menuItemElement = createMenuItemElement(item);
            menuGrid.appendChild(menuItemElement);
        });

    } catch (error) {
        console.error('Failed to fetch data:', error);
    }
});
