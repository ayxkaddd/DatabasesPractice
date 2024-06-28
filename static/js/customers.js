async function handleCustomerInput(event) {
    const searchTerm = event.target.value;
    const customersList = document.getElementById('customers-list');
    customersList.innerHTML = '';

    if (searchTerm.length >= 1) {
        const customers = await fetchData(`/api/customers/${searchTerm}/`);
        customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = `${customer.first_name} ${customer.last_name} ${customer.customer_id}`;
            customersList.appendChild(option);
        });
    }
}

async function fetchOrderHistory(customerId) {
    try {
        const orderHistory = await fetchData(`/api/order_history/${customerId}`);
        await populateTable(orderHistory, 'order-history-body');
    } catch (error) {
        console.error('Failed to fetch order history:', error);
    }
}