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
            event.target.replaceWith(saveButton);

            listItem.insertBefore(editInput, span);
            span.remove();

            saveButton.addEventListener('click', function() {
                let newText = editInput.value;
                fetch(`/edit/${listItem.getAttribute('data-task-id')}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_content: newText })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let newSpan = document.createElement('span');
                        newSpan.textContent = newText;
                        listItem.insertBefore(newSpan, editInput);
                        editInput.remove();
                        saveButton.replaceWith(event.target);
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
            let isCompleted = event.target.checked;


            fetch(`/update/${taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_completed: isCompleted })
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


