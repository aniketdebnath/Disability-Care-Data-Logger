// Fetch client list from server
async function loadClients() {
    try {
        const response = await fetch('/api/clients'); // Fetch the client list from an API endpoint
        const clients = await response.json();

        const clientListContainer = document.getElementById('client-list-container');

        clients.forEach(client => {
            const listItem = document.createElement('div');
            listItem.className = 'client-card';
            listItem.innerHTML = `
                <div class="client-details">
                    <h3>${client.ClientFirstName} ${client.ClientLastName}</h3>
                    <p><strong>Device ID:</strong> ${client.DeviceID}</p>
                    <p><strong>Date Created:</strong> ${new Date(client.DateOfCreation).toLocaleDateString()}</p>
                    <a href="health-data.html?deviceID=${client.DeviceID}" class="view-details-btn">View Health Data</a>
                </div>
            `;
            clientListContainer.appendChild(listItem);
        });
    } catch (error) {
        console.error('Error fetching client list:', error);
    }
}

// Call the function to load the clients when the page loads
window.onload = loadClients;
