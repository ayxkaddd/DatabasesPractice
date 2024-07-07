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
        const response = await fetch('/api/orders/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': GetTokenHeader(),
            },
            body: JSON.stringify(order)
        });
        const data = await response.json();
        alert('Order added successfully');
        window.location.reload();
    } catch (error) {
        console.error('Error adding order:', error);
    }
}