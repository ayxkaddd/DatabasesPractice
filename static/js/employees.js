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

function resetPassword(emp_id) {
    const length = 12;
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~`|}{[]:;?><,./-=";
    let password = "";
    for (let i = 0, n = charset.length; i < length; ++i) {
        password += charset.charAt(Math.floor(Math.random() * n));
    }
    alert(`Employee password was reset to ${password}`)
}