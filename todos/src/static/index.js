document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('todo-search');
    const todoList = document.getElementById('todo-list');
    
    // Check if the todoList element exists before trying to access its properties
    if (todoList) {
        const todoItems = todoList.getElementsByTagName('li');

        if (searchInput) {
            searchInput.addEventListener('keyup', function(event) {
                const query = event.target.value.toLowerCase();

                for (let i = 0; i < todoItems.length; i++) {
                    const item = todoItems[i];
                    const title = item.querySelector('.todo-title').textContent.toLowerCase();
                    const description = item.querySelector('.todo-description').textContent.toLowerCase();

                    // Check if the query is found in the title or description
                    if (title.includes(query) || description.includes(query)) {
                        item.style.display = 'flex'; // Show the item
                    } else {
                        item.style.display = 'none'; // Hide the item
                    }
                }
            });
        }
    }
});
