document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('orderChart').getContext('2d');
    let orderChart;

    async function fetchData() {
        const response = await fetch(`/api/reports/?period=day&start_date=2024-06-01&end_date=2024-06-30`);
        const data = await response.json();
        return data;
    }

    function updateChart(data) {
        if (orderChart) {
            orderChart.destroy();
        }

        const labels = data.map(item => item.start_date);
        const uniqueCustomers = data.map(item => item.unique_customers);
        const averageOrderValue = data.map(item => item.average_order_value);
        const topSellingItemQuantity = data.map(item => item.top_selling_item_quantity);
        const totalOrders = data.map(item => item.total_orders);
        const totalRevenue = data.map(item => item.total_revenue);

        orderChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Unique Customers',
                        data: uniqueCustomers,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: true,
                    },
                    {
                        label: 'Average Order Value (UAH)',
                        data: averageOrderValue,
                        borderColor: 'rgba(153, 102, 255, 1)',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        fill: true,
                    },
                    {
                        label: 'Top Selling Item Quantity',
                        data: topSellingItemQuantity,
                        borderColor: 'rgba(255, 159, 64, 1)',
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        fill: true,
                    },
                    {
                        label: 'Total Orders',
                        data: totalOrders,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: true,
                    },
                    {
                        label: 'Total Revenue (UAH)',
                        data: totalRevenue,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            tooltipFormat: 'll',
                        },
                    },
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    async function loadChart() {
        const data = await fetchData();
        updateChart(data);
    }


    loadChart();
});
