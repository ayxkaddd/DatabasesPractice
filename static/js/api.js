function GetTokenHeader() {
    token = localStorage.getItem("token");
    return `Bearer ${token}`
}

async function fetchData(url) {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            "Authorization": GetTokenHeader(),
        }
    });
    if (!response.ok) {
        window.location.href = '/login/';
    }
    return await response.json();
}