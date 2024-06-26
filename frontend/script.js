const apiBaseUrl = '/api/books';
const logoutApiUrl = '/api/admin/logout';
const loginStatusUrl = '/api/admin/status';

// Check login status
async function checkLoginStatus() {
    try {
        const response = await fetch('/api/admin/status');
        if (response.status === 403) {
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Error checking login status:', error);
        window.location.href = 'login.html';
    }
}

window.onload = checkLoginStatus;

document.getElementById('logoutButton').addEventListener('click', async function() {
    try {
        const response = await fetch(logoutApiUrl, { method: 'POST' });
        if (response.ok) {
            window.location.href = 'login.html';
        } else {
            console.error('Failed to logout:', await response.json());
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

document.getElementById('addBookForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const title = document.getElementById('title').value;
    const author = document.getElementById('author').value;

    try {
        const response = await fetch(apiBaseUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, author })
        });

        if (response.ok) {
            const newBook = await response.json();
            addBookToListKedua(newBook);

            // Hapus pesan "No book stored" jika ada
            const noBooksMessage = document.getElementById('noBooksMessage');
            if (noBooksMessage) {
                noBooksMessage.remove();
            }

            document.getElementById('addBookForm').reset();
        } else {
            console.error('Failed to add book:', await response.json());
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

async function fetchBooks() {
    try {
        const response = await fetch(apiBaseUrl);
        if (response.ok) {
            const books = await response.json();
            const bookList = document.getElementById('bookList');
            if (books.length === 0) {
                bookList.innerHTML = '<li id="noBooksMessage">No book stored</li>';
            } else {
                const noBooksMessage = document.getElementById('noBooksMessage');
                if (noBooksMessage) {
                    noBooksMessage.remove(); // Hapus pesan jika sudah ada buku yang ditampilkan
                }
                books.forEach(book => addBookToList(book));
            }
        } else {
            console.error('Failed to fetch books:', await response.json());
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function addBookToList(book) {
    const bookList = document.getElementById('bookList');
    const li = document.createElement('li');
    li.innerHTML = `
        <div>
            <p><strong>Title:</strong> ${book[1]}</p>
            <p><strong>Author:</strong> ${book[2]}</p>
        </div>
    `;
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.classList.add('delete-button');
    deleteButton.onclick = async function() {
        try {
            const response = await fetch(`${apiBaseUrl}/${book[0]}`, { method: 'DELETE' });
            if (response.ok) {
                bookList.removeChild(li);
                if (bookList.childElementCount === 0) {
                    bookList.innerHTML = '<li id="noBooksMessage">No book stored</li>';
                }
            } else {
                console.error('Failed to delete book:', await response.json());
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };
    li.appendChild(deleteButton);
    bookList.appendChild(li);
}

function addBookToListKedua(book) {
    const bookList = document.getElementById('bookList');
    const li = document.createElement('li');
    li.innerHTML = `
        <div>
            <p><strong>Title:</strong> ${book.title}</p>
            <p><strong>Author:</strong> ${book.author}</p>
        </div>
    `;
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.classList.add('delete-button');
    deleteButton.onclick = async function() {
        try {
            const response = await fetch(`${apiBaseUrl}/${book.id}`, { method: 'DELETE' });
            if (response.ok) {
                bookList.removeChild(li);
                if (bookList.childElementCount === 0) {
                    bookList.innerHTML = '<li id="noBooksMessage">No book stored</li>';
                }
            } else {
                console.error('Failed to delete book:', await response.json());
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };
    li.appendChild(deleteButton);
    bookList.appendChild(li);
}

fetchBooks();
