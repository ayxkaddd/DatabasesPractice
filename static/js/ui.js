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

async function populateTable(data, tableBodyId, actions = []) {
    const tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = '';
    data.forEach(item => {
        const row = document.createElement('tr');
        row.dataset.itemId = item.item_id;
        Object.keys(item).forEach(key => {
            const cell = document.createElement('td');
            cell.textContent = item[key];
            if (item[key] === null){
                cell.textContent = "hidden"
            }
            row.appendChild(cell);
        });
        if (actions.length > 0) {
            const actionCell = document.createElement('td');
            actionCell.className = 'action-cell';
            actions.forEach(action => {
                const button = document.createElement('button');
                button.textContent = action.text;
                button.className = 'action-button';
                button.onclick = () => action.onClick(item);
                actionCell.appendChild(button);
            });
            row.appendChild(actionCell);
        }
        tableBody.appendChild(row);
    });
}