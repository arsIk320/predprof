/*document.addEventListener('DOMContentLoaded', function() {
    const toggleInventoryButton = document.getElementById('toggle-inventory');
    const inventoryContainer = document.getElementById('inventory-container');
    const requestContainer = document.getElementById('request-container');

    toggleInventoryButton.addEventListener('click', function() {
        if (inventoryContainer.style.display === 'none') {
            inventoryContainer.style.display = 'block';
            requestContainer.style.display = 'block';
        } else {
            inventoryContainer.style.display = 'none';
            requestContainer.style.display = 'none';
        }
    });

    const requestButton = document.getElementById('request-button');
    const inventoryRequest = document.getElementById('inventory-request');
    const repairRequest = document.getElementById('request-repair-container');

    requestButton.addEventListener('click', function() {
        if (inventoryRequest.style.display === 'none') {
            repairRequest.style.display = 'block';
            inventoryRequest.style.display = 'block';
        } else {
            repairRequest.style.display = 'none';
            inventoryRequest.style.display = 'none';
        }
    });

});
*/

document.addEventListener('DOMContentLoaded', function() {
    const toggleInventoryButton = document.getElementById('toggle-inventory');
    const requestButton = document.getElementById('request-button');
    const upperContainers = document.getElementById('upper');
    const lowerContainers = document.getElementById('lower');
    const MainData = document.getElementById('main-data');

    toggleInventoryButton.addEventListener('click', function(){
        if (upperContainers.style.display === 'none') {
            MainData.style.display = 'none';
            upperContainers.style.display = 'flex';
        } else {
            upperContainers.style.display = 'none';
        }
        if ((lowerContainers.style.display === 'none') && (upperContainers.style.display === 'none')) {
            MainData.style.display = 'flex';
        }
    });

    requestButton.addEventListener('click', function() {
        if (lowerContainers.style.display === 'none') {
            MainData.style.display = 'none';
            lowerContainers.style.display = 'flex';
        } else {
            lowerContainers.style.display = 'none';
        }
        if ((lowerContainers.style.display === 'none') && (upperContainers.style.display === 'none')) {
            MainData.style.display = 'flex';
        }
    });
});