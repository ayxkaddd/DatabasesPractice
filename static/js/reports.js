async function fetchDashboardData() {
    const today = new Date();
    const todayData = await fetchReportData(today);
    const yesterdayData = await fetchReportData(getPreviousDay(today));

    updateDashboard(todayData, yesterdayData);
}

function getPreviousDay(date) {
    const previous = new Date(date);
    previous.setDate(date.getDate() - 2);
    console.log(previous)
    return previous;
}

async function fetchReportData(date) {
    const startDate = date.toISOString().split('T')[0];
    const endDate = new Date(date.setDate(date.getDate() + 1)).toISOString().split('T')[0];
    const response = await fetchData(`/api/reports/?period=day&start_date=${startDate}&end_date=${endDate}`);
    const data = await response
    return data[0];
}

function updateDashboard(todayData, yesterdayData) {
    updateCard('total-orders', todayData.total_orders, yesterdayData.total_orders);
    updateCard('unique-customers', todayData.unique_customers, yesterdayData.unique_customers);
    updateCard('total-revenue', todayData.total_revenue, yesterdayData.total_revenue, true);
    updateCard('average-order-value', todayData.average_order_value, yesterdayData.average_order_value, true);
    updateCard('top-selling-item', todayData.top_selling_item_quantity, yesterdayData.top_selling_item_quantity);
}

function updateCard(id, todayValue, yesterdayValue, isCurrency = false) {
    const card = document.getElementById(id);
    const todayElement = card.querySelector('.today-value');
    todayElement.className = "large-number"
    const changeElement = card.querySelector('.change');

    const formatValue = (value) => isCurrency ? `₴${value.toFixed(2)}` : value;

    todayElement.textContent = `${formatValue(todayValue)}`;

    const change = todayValue - yesterdayValue;
    const percentChange = ((change / yesterdayValue) * 100).toFixed(2);
    const changeText = `${change >= 0 ? '+' : ''}${formatValue(change)} (${percentChange}%)`;

    changeElement.textContent = changeText;
    changeElement.className = `change ${change >= 0 ? 'positive' : 'negative'}`;
    changeElement.innerHTML = `${changeText} <i class="fas fa-arrow-${change >= 0 ? 'up' : 'down'}" style="font-size: 0.8em;"></i>`;
}

function updateTopSellingItem(todayItem, yesterdayItem, todayQuantity, yesterdayQuantity) {
    const card = document.getElementById('top-selling-item');
    const todayElement = card.querySelector('.today-value');
    const yesterdayElement = card.querySelector('.yesterday-value');

    todayElement.textContent = `Today: ${todayItem} (${todayQuantity})`;
    yesterdayElement.textContent = `Yesterday: ${yesterdayItem} (${yesterdayQuantity})`;
}
