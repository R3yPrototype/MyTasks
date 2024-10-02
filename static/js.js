document.addEventListener('DOMContentLoaded', function() {
    let toDoList = document.getElementById('toDoList');

    // Handle delete button clicks
    toDoList.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-button')) {
            let listItem = event.target.closest('li');
            let taskId = listItem.getAttribute('data-task-id');

            fetch(`/delete/${taskId}`, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        listItem.remove();
                    } else {
                        alert('Failed to delete the task.');
                    }
                });
        }
    });

    // Handle edit button clicks
    toDoList.addEventListener('click', function(event) {
        if (event.target.classList.contains('edit-button')) {
            let listItem = event.target.closest('li');
            let span = listItem.querySelector('span');
            let currentText = span.textContent;
            let editInput = document.createElement('input');
            editInput.classList.add('editAttribute');
            editInput.setAttribute('type', 'text');
            editInput.value = currentText;
            let saveButton = document.createElement('button');
            saveButton.textContent = 'Save';

            // Replace the Edit button with Save button
            event.target.replaceWith(saveButton);

            // Insert input field and remove the current text span
            listItem.insertBefore(editInput, span);
            span.remove();

            saveButton.addEventListener('click', function() {
                let newText = editInput.value;

                fetch(`/edit/${listItem.getAttribute('data-task-id')}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: newText }) 
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let newSpan = document.createElement('span');
                        newSpan.textContent = newText;
                        listItem.insertBefore(newSpan, editInput);
                        editInput.remove();

                        // Replace Save button with a new Edit button
                        let editButton = document.createElement('button');
                        editButton.textContent = 'Edit';
                        editButton.classList.add('edit-button');
                        saveButton.replaceWith(editButton);
                    } else {
                        alert('Failed to update the task.');
                    }
                });
            });
        }
    });

    // Handle checkbox changes
    toDoList.addEventListener('change', function(event) {
        if (event.target.type === 'checkbox') {
            let listItem = event.target.closest('li');
            let taskId = listItem.getAttribute('data-task-id');
            let isChecked = event.target.checked;

            fetch(`/update/${taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ checked: isChecked })  
            }).then(response => {
                if (!response.ok) {
                    alert('Failed to update the task status.');
                }
            });
        }
    });
});

document.getElementById('logoutButton').addEventListener('click', function() {
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/'; 
        } else {
            console.error('Logout failed');
        }
    });
});



