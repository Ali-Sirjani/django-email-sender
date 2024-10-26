document.addEventListener('DOMContentLoaded', () => {
    // Function to dynamically render messages
    function renderMessages(messages) {
        const msgList = document.getElementById('id_block_msg');
        msgList.innerHTML = ''; // Clear the current message list

        messages.forEach(msg => {
            const msgItem = document.createElement('div');
            msgItem.classList.add('msg-item');

            msgItem.innerHTML = `
                <p><a href="${msg.url}">${msg.id}: ${msg.subject} ${msg.datetime_created}</a></p>
            `;
            msgList.appendChild(msgItem);
        });
    }

    // Function to dynamically update pagination
    function renderPagination(data) {
        const pagination = document.getElementById('id_msg_pagination');
        pagination.innerHTML = ''; // Clear current pagination
        if (data.total_pages > 1) {
            if (data.has_previous) {
                pagination.innerHTML += `
                <li class="page-item">
                    <a class="page-link" href="?page=1" aria-label="First">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page=${data.previous_page_number}" aria-label="Previous">
                        <span aria-hidden="true">&lsaquo;</span>
                    </a>
                </li>`;
            }

            for (let i = 1; i <= data.total_pages; i++) {
                if (i === data.page) {
                    pagination.innerHTML += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
                } else {
                    pagination.innerHTML += `<li class="page-item"><a class="page-link" href="?page=${i}">${i}</a></li>`;
                }
            }

            if (data.has_next) {
                pagination.innerHTML += `
                <li class="page-item">
                    <a class="page-link" href="?page=${data.next_page_number}" aria-label="Next">
                        <span aria-hidden="true">&rsaquo;</span>
                    </a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page=${data.total_pages}" aria-label="Last">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>`;
            }
        }
    }

    // Function to send AJAX request
    function sendRequestMsgList(currentUrl) {
        $.ajax({
            url: currentUrl,
            type: 'GET',
            success: function (data) {
                // Parse the messages and render them dynamically
                const messages = JSON.parse(data.messages);
                renderMessages(messages);

                // Render pagination dynamically
                renderPagination(data);

                console.log('Messages and pagination successfully updated.');
            },
            error: function () {
                console.log('Error occurred while fetching message list.');
            }
        });
    }

    // Search form button handler
    const searchInput = document.getElementById('id_search_msg');
    window.onload = function () {
        searchInput.value = new URL(window.location.href).searchParams.get('q') || '';
    }
    $(document).on('click', '#id_search_form_btn', function (e) {
        e.preventDefault();

        // Construct current URL and add search query
        const currentUrl = new URL(window.location.href.replace(window.location.search, ''));
        currentUrl.searchParams.set(searchInput.name, searchInput.value);

        // Update the browser's history state
        history.replaceState(null, '', currentUrl.toString());

        // Send the request to fetch filtered messages
        sendRequestMsgList(currentUrl);
    });

    // Pagination link handler
    $(document).on('click', '#id_msg_pagination a', function (e) {
        e.preventDefault();

        // Get the target page from the clicked pagination link
        const targetUrl = $(this).attr('href');
        const currentUrl = new URL(window.location.href);

        // Extract page number and update the URL
        let pageNumber = new URL(targetUrl, window.location.origin).searchParams.get('page');
        currentUrl.searchParams.set('page', pageNumber);

        // Update the browser's history state
        history.replaceState(null, '', currentUrl.toString());

        // Send the request to fetch the specified page
        sendRequestMsgList(currentUrl);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const filterRecipientBtn = document.getElementById('id_recipient_form_btn')
    filterRecipientBtn.addEventListener('click', async (e) => {
        e.preventDefault()

        const filterForm = document.getElementById('id_recipient_form')
        const formData = new FormData(filterForm)
        const params = new URLSearchParams(formData)

        const filterUrl = `${filterForm.action}?${params.toString()}`
        const response = await fetch(filterUrl)
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`)
        }

        const response_json = await response.json();
        const pResult = document.getElementById('id_recipient_result')
        if (!pResult.parentElement.classList.contains('show')) pResult.parentElement.classList.add('show')
        pResult.innerHTML = ''
        const users = JSON.parse(response_json.recipients);
        users.forEach(recipient => {
            pResult.innerHTML += `${recipient.username}:${recipient.email}, `
        });
    });

    const copyFilterResultBtn = document.getElementById('id_copy_recipient_result')
    copyFilterResultBtn.addEventListener('click', (e) => {
        const pResult = document.getElementById('id_recipient_result')
        navigator.clipboard.writeText(pResult.innerText)
    });

});
