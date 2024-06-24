async function submitCategoryForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const category_name = formData.get('category_name');

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

        if (!addCategoryResponse.ok) {
            throw new Error('Failed to add new category');
        }

        window.location.reload();
    } catch (error) {
        console.error('Error adding new item:', error);
    }
}