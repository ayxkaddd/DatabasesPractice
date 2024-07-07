document.addEventListener('DOMContentLoaded', async () => {
    showSection('menu-items');
    try {
        const user_data = await fetchData("/api/me/");
        const userNameElement = document.getElementById('user-name');
        userNameElement.textContent = `${user_data.first_name}`;

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
        const menuActions = [
            {
                text: 'Edit Item',
                onClick: (menuItems) => editItem(menuItems.item_id)
            }
        ];
        await populateTable(menuItems, 'menu-items-body', menuActions);

        const popularMenuItems = await fetchData('/api/menu_items/popular/');
        await populateTable(popularMenuItems, 'popular-menu-items-body');

        const customers = await fetchData('/api/customers/');
        const customerActions = [
            {
                text: 'View Orders',
                onClick: (customer) => fetchOrderHistory(customer.customer_id)
            }
        ];
        await populateTable(customers, 'customers-body', customerActions);

        const regularCustomers = await fetchData('/api/customers/regular_customers/');
        await populateTable(regularCustomers, 'regular-customers-body');

        const employees = await fetchData('/api/employees/');
        employeesActions = [
            {
                text: 'Reset Password',
                onClick: (employees) => resetPassword(employees.employee_id)
            }
        ];
        await populateTable(employees, 'employees-body', employeesActions);

        const menuGrid = document.getElementById('menu-grid');
        menuItems.forEach(item => {
            const menuItemElement = createMenuItemElement(item);
            menuGrid.appendChild(menuItemElement);
        });
        fetchDashboardData();
    } catch (error) {
        console.error('Failed to fetch data:', error);
    }
});

document.getElementById('addOrderForm').addEventListener('submit', submitOrder);
document.getElementById('customer').addEventListener('input', handleCustomerInput);
document.getElementById('cash-button').addEventListener('click', () => {
    document.getElementById('cash-details').style.display = 'block';
    document.getElementById('cash-given').addEventListener('input', calculateChange);
});
document.getElementById('credit-card-button').addEventListener('click', () => {
    document.getElementById('cash-details').style.display = 'none';
});