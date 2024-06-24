let previewItems = [];
let editedItems = new Set();

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

async function editItem(itemId) {
    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
    const cells = row.querySelectorAll('td');
    const item = {
        item_id: itemId,
        category: cells[1].textContent,
        name: cells[2].textContent,
        price: parseFloat(cells[3].textContent)
    };

    if (!window.categories) {
        window.categories = await fetchData('/api/categories/');
    }

    cells[1].innerHTML = createCategorySelect(item.category);
    cells[2].innerHTML = `<input type="text" value="${item.name}" />`;
    cells[3].innerHTML = `<input type="number" step="0.01" value="${item.price}" />`;

    const actionCell = cells[cells.length - 1];
    const editButton = actionCell.querySelector('button');
    editButton.textContent = 'Cancel';
    editButton.onclick = () => cancelEdit(itemId);

    editedItems.add(itemId);
    updateSaveChangesButton();
}

function createCategorySelect(currentCategory) {
    const select = document.createElement('select');
    window.categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.name;
        option.textContent = category.name;
        if (category.name === currentCategory) {
            option.selected = true;
        }
        select.appendChild(option);
    });
    return select.outerHTML;
}

async function cancelEdit(itemId) {
    editedItems.delete(itemId);
    const menuItems = await fetchData('/api/menu_items/');
    const menuActions = [{
        text: 'Edit Item',
        onClick: (menuItem) => editItem(menuItem.item_id)
    }];
    await populateTable(menuItems, 'menu-items-body', menuActions);
    editedItems.clear();
    updateSaveChangesButton();
}

function updateSaveChangesButton() {
    const saveButton = document.getElementById('saveChangesButton');
    if (editedItems.size > 0) {
        if (!saveButton) {
            const newSaveButton = document.createElement('button');
            newSaveButton.id = 'saveChangesButton';
            newSaveButton.textContent = 'Save All Changes';
            newSaveButton.onclick = saveAllChanges;
            document.querySelector('#menu-items-body').insertAdjacentElement('afterend', newSaveButton);
        }
    } else {
        saveButton?.remove();
    }
}

async function saveAllChanges() {
    const updatedItems = [];
    editedItems.forEach(itemId => {
        const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
        const cells = row.querySelectorAll('td');
        updatedItems.push({
            item_id: itemId,
            category: cells[1].querySelector('select').value,
            name: cells[2].querySelector('input').value,
            price: parseFloat(cells[3].querySelector('input').value)
        });
    });

    try {
        const response = await fetch('/api/menu_items/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': GetTokenHeader(),
            },
            body: JSON.stringify(updatedItems)
        });

        if (response.ok) {
            alert('Changes saved successfully!');
            const menuItems = await fetchData('/api/menu_items/');
            const menuActions = [{
                text: 'Edit Item',
                onClick: (menuItem) => editItem(menuItem.item_id)
            }];
            await populateTable(menuItems, 'menu-items-body', menuActions);
            editedItems.clear();
            updateSaveChangesButton();
        } else {
            throw new Error('Failed to save changes');
        }
    } catch (error) {
        alert('Error saving changes: ' + error.message);
    }
}