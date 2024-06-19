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


function populateTable(data, tableBodyId, extraColumn = false) {
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
        populateTable(orderHistory, 'order-history-body');
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
        populateTable(menuItems, 'menu-items-body');

        const popularMenuItems = await fetchData('/api/popular_menu_items/');
        populateTable(popularMenuItems, 'popular-menu-items-body');

        const customers = await fetchData('/api/customers/');
        populateTable(customers, 'customers-body', true);

        const regularCustomers = await fetchData('/api/regular_customers/');
        populateTable(regularCustomers, 'regular-customers-body');

        showSection('menu-items');


    } catch (error) {
        console.error('Failed to fetch data:', error);
    }
});
