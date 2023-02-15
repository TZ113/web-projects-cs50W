document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#edit_btn').forEach(function(element){
        element.onclick = function() {
            const form = element.nextElementSibling;
            if (getComputedStyle(form).display === 'none'){    
                form.style.display = 'block';
                form.nextElementSibling.style.display = 'none';
            }
            else {
                form.style.display = 'none';
                form.nextElementSibling.style.display = 'block';
            }
            form.onsubmit = function() {
                fetch('/post', {
                    method: "PUT",
                    headers: {
                        'X-CSRFToken': form.children[0].value
                    },
                    body: JSON.stringify({
                        post_id: form.children[2].value,
                        post: form.children[1].value
                    })
                })
                .then(response => {
                    console.log(response)
                    if (response.status === 204){
                        form.style.display = 'none';
                        form.nextElementSibling.innerHTML = `<pre style="font: 17px Arial, sans-serif;">${form.children[1].value}</pre>`;
                        form.nextElementSibling.style.display = 'block';
                    }
                })
                .catch(error => console.log(error))
                
                return false;
            }
        }

    })
    
    document.querySelectorAll('i').forEach(element => {
        element.addEventListener('click', () => {
            if (element.parentElement.children[4].innerHTML === ''){
                location.href = '/login';
            }
            else {
                fetch('/post', {
                    method: "PUT",
                    headers: {
                        'X-CSRFToken': element.parentElement.children[0].value
                    },
                    body: JSON.stringify({
                        post_id: element.parentElement.children[1].innerHTML
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (element.className === 'fa-regular fa-heart'){
                        element.className = 'fa-solid fa-heart';
                        element.parentElement.children[3].innerHTML = result.likes;
                    }
                    else{
                        element.className = 'fa-regular fa-heart';
                        element.parentElement.children[3].innerHTML = result.likes;
                    }
                })
                .catch(error => console.log(error))
            }
            
        })
    })
})

function follow_unfollow(event, id) {
    fetch(id, {
        method: "PUT",
        headers: {
            'X-CSRFToken': event.target.previousElementSibling.value
        }
    })
    .then(response => {
        console.log(response);
        location.reload();
    })
    .catch(error => console.log(error))
}