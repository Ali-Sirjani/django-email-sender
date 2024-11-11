document.addEventListener('DOMContentLoaded', () => {
    // Function to dynamically render messages
    function renderMessages(msg_list) {
        const msgList = document.querySelector('#id_block_msg .messages')
        msgList.innerHTML = ''; // Clear the current message list

        msg_list.forEach(msg => {
            const msgItem = document.createElement('div');

            msgItem.innerHTML = `
                <p class="messages__item">
                    <a href="${msg.url}" class="messages__item__link">${msg.id}: ${msg.subject} ${msg.datetime_created}</a>
                </p>
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
                <li class="page-item-cst">
                    <a class="page-link-cst" href="?page=1" aria-label="First">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
                <li class="page-item-cst">
                    <a class="page-link-cst" href="?page=${data.previous_page_number}" aria-label="Previous">
                        <span aria-hidden="true">&lsaquo;</span>
                    </a>
                </li>`;
            }

            for (let i = 1; i <= data.total_pages; i++) {
                if (i === data.page) {
                    pagination.innerHTML += `<li class="page-item-cst active"><span class="page-link-cst">${i}</span></li>`;
                } else {
                    pagination.innerHTML += `<li class="page-item-cst"><a class="page-link-cst" href="?page=${i}">${i}</a></li>`;
                }
            }

            if (data.has_next) {
                pagination.innerHTML += `
                <li class="page-item-cst">
                    <a class="page-link-cst" href="?page=${data.next_page_number}" aria-label="Next">
                        <span aria-hidden="true">&rsaquo;</span>
                    </a>
                </li>
                <li class="page-item-cst">
                    <a class="page-link-cst" href="?page=${data.total_pages}" aria-label="Last">
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
                const msg_list = JSON.parse(data.msg_list);
                renderMessages(msg_list);

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
            let withUser = recipient.username ? `${recipient.username}:` : '';
            pResult.innerHTML += `${withUser}${recipient.email}, `
        });
    });

    const copyFilterResultBtn = document.getElementById('id_copy_recipient_result')
    copyFilterResultBtn.addEventListener('click', (e) => {
        const pResult = document.getElementById('id_recipient_result')
        navigator.clipboard.writeText(pResult.innerText)
    });

});


document.addEventListener('DOMContentLoaded', () => {
    const msgSendFormBtn = document.getElementById('id_msg_send_form_btn')
    msgSendFormBtn.addEventListener('click', async (e) => {
        e.preventDefault()

        const spinnerBtn = msgSendFormBtn.querySelector('.spinner-border')
        const spanTextBtn = msgSendFormBtn.querySelector('[role=status]')

        msgSendFormBtn.setAttribute('disabled', '')
        spinnerBtn.classList.remove('d-none')
        spanTextBtn.innerText = 'Sending...'

        if (typeof tinyMCE !== 'undefined') {
            tinyMCE.triggerSave();
        }
        const msgSendFrom = document.getElementById('id_msg_send_form')

        const csrftoken = getCookie('csrftoken');
        let sendUrl = msgSendFrom.action
        const formData = new FormData(msgSendFrom);
        Array.from(document.querySelectorAll('.is-invalid')).forEach(element => {
            element.classList.remove('is-invalid')
        })
        Array.from(document.querySelectorAll('.invalid-feedback')).forEach(element => {
            element.classList.remove('d-block')
        })

        const response = await fetch(sendUrl, {
            method: msgSendFrom.method,
            body: formData,
            headers: {'X-CSRFToken': formData.get('csrfmiddlewaretoken')},
        })

        if (!response.ok) {
            const formBlockErrors = msgSendFrom.querySelector('#id_msg_form_errors')
            try {
                const errorData = await response.json();

                handleFormErrors(formBlockErrors, errorData);
            } catch (e) {
                const errorServer = 'Email can\'t send for these reason: \n 1. Check you internet and if you can ' +
                    'connect to vpn \n 2. The server of site is not work correctly '
                addNoneFieldError(errorServer, formBlockErrors)
                formBlockErrors.classList.remove('d-none')
            }

            setTimeout(() => {
                msgSendFormBtn.removeAttribute('disabled')
                spinnerBtn.classList.add('d-none')
                spanTextBtn.innerText = 'Send'
            }, 300)
            return;
        }

        location.reload();
    })
});

function handleFormErrors(formBlockErrors, errorData) {
    formBlockErrors.innerHTML = ''

    for (const form in errorData) {
        let formData = errorData[form]

        if (formData.length) {
            for (const formOfFormsetKey in formData) {
                let formOfFormset = formData[formOfFormsetKey]
                if (formOfFormset.errors) {
                    for (const error of formOfFormset.errors) {
                        addNoneFieldError(error, formBlockErrors)
                    }
                }
                const fieldsOfForm = formOfFormset['fields']

                for (const fieldKey in fieldsOfForm) {
                    if (fieldsOfForm[fieldKey].errors.length) {
                        addErrorMessage(fieldsOfForm[fieldKey], fieldKey)
                    }
                }
            }
        } else {
            if (formData.errors) {
                for (const error of formData.errors) {
                    addNoneFieldError(error, formBlockErrors)
                }
            }
            for (const fieldKey in formData['fields']) {
                if (formData['fields'][fieldKey].errors.length) {
                    addErrorMessage(formData['fields'][fieldKey], fieldKey)
                }
            }
        }
    }

    if (formBlockErrors.innerText) {
        formBlockErrors.classList.remove('d-none')
    }

}

function addNoneFieldError(message, formBlockErrors) {
    const newNoneError = document.createElement('div');
    newNoneError.classList = formBlockErrors.dataset.childClass
    newNoneError.textContent = `${formBlockErrors.dataset.startWith}${message}`;
    formBlockErrors.appendChild(newNoneError);
}

function addErrorMessage(field, fieldName) {
    const fieldError = document.getElementById(`id_${fieldName}`)
    const fieldBoxMsg = document.getElementById(`id_${fieldName}_feedback`)

    fieldError.classList.add('is-invalid')
    fieldError.setAttribute('aria-invalid', 'true')
    fieldBoxMsg.innerHTML = ''
    fieldBoxMsg.classList.add('mb-4', 'invalid-feedback', 'd-block')
    for (const error of field.errors) {
        fieldBoxMsg.innerHTML += `<strong>${error}</strong>`
    }
}
