document.getElementById('add-student').addEventListener('click', function() {
    const firstName = document.getElementById('first-name').value.trim();
    const lastName = document.getElementById('last-name').value.trim();
    const age = document.getElementById('age').value.trim();
    const className = document.getElementById('class').value.trim();

    if (firstName && lastName && age && className) {
        const listItem = document.createElement('li');
        listItem.textContent = `${firstName} ${lastName}, Возраст: ${age}, Класс: ${className}`;
        document.getElementById('list').appendChild(listItem);

        // Очистка полей ввода
        document.getElementById('first-name').value = '';
        document.getElementById('last-name').value = '';
        document.getElementById('age').value = '';
        document.getElementById('class').value = '';
    } else {
        alert("Пожалуйста, заполните все поля.");
    }
});

document.getElementById('remove-all').addEventListener('click', function() {
    const list = document.getElementById('list');
    list.innerHTML = ''; // Удаляем всех учеников из списка
});