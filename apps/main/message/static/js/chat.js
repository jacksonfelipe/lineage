function openTab(evt, tabName) {
    // Ocultar todas as abas
    const tabContents = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = "none";
    }

    // Remover a classe ativa de todos os botões
    const tabButtons = document.getElementsByClassName("tab-button");
    for (let i = 0; i < tabButtons.length; i++) {
        tabButtons[i].classList.remove("active");
    }

    // Mostrar a aba atual e adicionar a classe ativa ao botão
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");
}

function filterFriends() {
    const searchInput = document.getElementById('msg-friends').value.toLowerCase();
    const friendItems = document.querySelectorAll('.friend-item');

    document.getElementById("smileys").style.display = "block";

    friendItems.forEach(function(item) {
        // Usando a classe friend-name para encontrar o nome do amigo
        const friendName = item.querySelector('.friend-name').textContent.toLowerCase();

        // Verifica se o nome do amigo contém o texto da pesquisa
        if (friendName.includes(searchInput)) {
            item.classList.remove('desativar'); // Remove a classe .desativar se houver correspondência
        } else {
            item.classList.add('desativar'); // Adiciona a classe .desativar se não houver correspondência
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    
    const chatInput = document.querySelector('#message-input');
    const emojiButton = document.querySelector('#emoji-button');
    
    // Inicialize o Emoji Button
    const picker = new EmojiButton();

    // Mostra o seletor de emojis ao clicar no botão
    emojiButton.addEventListener('click', () => {
        picker.togglePicker(emojiButton);
    });

    // Insere o emoji no campo de texto quando selecionado
    picker.on('emoji', emoji => {
        chatInput.value += emoji;
        chatInput.focus(); // Foca no campo de texto após inserir o emoji
    });

    const toggleButton = document.getElementById('toggle-friend-list');
    const friendListContent = document.getElementById('friend-list-content');
    const chatSection = toggleButton.closest('.row').querySelector('.col-lg-9'); // Seleciona a coluna do chat

    let activeFriendId = null;  // Armazena o ID do amigo selecionado
    let messageReloadInterval = null; // Variável para o intervalo de recarregamento

    toggleButton.onclick = function() {
        if (friendListContent.classList.contains('hidden')) {
            friendListContent.classList.remove('hidden');
            chatSection.classList.remove('col-lg-12');
            chatSection.classList.add('col-lg-9');
            toggleButton.classList.remove('fa-plus'); // Troca para "X"
            toggleButton.classList.add('fa-times'); // Volta para "X"
        } else {
            friendListContent.classList.add('hidden');
            chatSection.classList.remove('col-lg-9');
            chatSection.classList.add('col-lg-12'); // Ajuste para ocupar toda a largura
            toggleButton.classList.remove('fa-times'); // Troca para "+"
            toggleButton.classList.add('fa-plus'); // Troca para "+"
        }
    };

    const sendMessageButton = document.getElementById('send-message');
    const messageInput = document.getElementById('message-input');
    const messageContainer = document.getElementById('message-container');
    const messageInputGroup = document.getElementById('message-input-group');


    // Função para enviar mensagem via AJAX
    sendMessageButton.addEventListener('click', function () {
        const message = messageInput.value;
        const friendId = activeFriendId; // Usa o ID do amigo ativo

        if (message && friendId) {
            fetch('/app/api/send-message/', { // Altere para a URL correta do seu endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Inclua o token CSRF se necessário
                },
                body: JSON.stringify({ message: message, friend_id: friendId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    // Substitui quebras de linha por <br> para exibição no HTML
                    const formattedMessage = message.replace(/\n/g, '<br>');

                    // Atualiza a interface com a nova mensagem
                    messageContainer.innerHTML += `
                    <div class="media mb-3 text-end d-flex" style="gap: 5px;">
                        <div class="media-body">
                            <div class="current-user">
                                <div class="title-current">
                                    <h6 class="m-0" style="font-weight: bold;">${currentUser}</h6>
                                    <small class="text-dark">${new Date().toLocaleString()}</small>
                                </div>
                                <p class="m-0" style="font-size: 12pt; word-break: break-word; white-space: pre-wrap; max-width: 100%;">${formattedMessage}</p>
                            </div>
                        </div>
                        <img src="${avatarUrl}" class="rounded-circle me-3" alt="Avatar" width="40" height="40">
                    </div>`;
                    messageInput.value = ''; // Limpa o campo de entrada

                    // Adiciona autoscroll
                    messageContainer.scrollTop = messageContainer.scrollHeight; // Rola para o final
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });

    messageInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            // Se apenas "Enter" for pressionado, envia a mensagem
            event.preventDefault();  // Impede a quebra de linha padrão
            sendMessageButton.click();  // Simula o clique no botão de enviar
        } else if (event.key === 'Enter' && event.shiftKey) {
            // Se "Shift + Enter" for pressionado, permite a quebra de linha
            event.preventDefault();  // Impede o envio da mensagem
            const cursorPosition = messageInput.selectionStart;
            messageInput.value = messageInput.value.slice(0, cursorPosition) + '\n' + messageInput.value.slice(cursorPosition);
            messageInput.selectionEnd = cursorPosition + 1;  // Move o cursor para a nova linha
        }
    });

    // Função para carregar mensagens ao selecionar um amigo
    const friendItems = document.querySelectorAll('.friend-item');
    friendItems.forEach(item => {
        item.addEventListener('click', function () {
            const friendId = this.getAttribute('data-friend-id');
            activeFriendId = friendId; // Define o amigo ativo
            loadMessages(friendId); // Chama a função para carregar mensagens

            // Remove a classe 'active' de todos os amigos
            friendItems.forEach(friend => {
                friend.classList.remove('active');
                const status = friend.querySelector('.friend-status');
                if (status) {
                    status.classList.remove('shadow-text');
                }
            });

            // Adiciona a classe 'active' no amigo clicado
            this.classList.add('active');

            const status = this.querySelector('.friend-status');
            if (status) { status.classList.add('shadow-text'); }

            messageInputGroup.style.display = 'flex'; // Mostra a caixa de entrada de mensagem

            // Configura o intervalo de recarregamento das mensagens
            if (messageReloadInterval) {
                clearInterval(messageReloadInterval); // Limpa qualquer intervalo anterior
            }

            // Inicia a recarga de mensagens a cada 3 segundos
            messageReloadInterval = setInterval(() => {
                loadMessages(friendId);
            }, 3000);

        });
    });


    function loadMessages(friendId) {
        fetch(`/app/api/load-messages/${friendId}/`, { // Substitua pela URL correta
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            messageContainer.innerHTML = ''; // Limpa as mensagens atuais
    
            data.messages.forEach(message => {
                const isCurrentUser = message.sender.username === currentUser; // Verifica se é o usuário atual
    
                // Define a cor de fundo com base no remetente
                const bgColorClass = isCurrentUser ? 'current-user' : 'current-friend';
                
                // Substitui quebras de linha por <br> para exibição no HTML
                const formattedMessage = message.text.replace(/\n/g, '<br>');
    
                // Estrutura da mensagem
                messageContainer.innerHTML += `
                <div class="media mb-3 ${isCurrentUser ? 'text-end' : 'text-start'} d-flex" style="gap: 5px;"> <!-- Classe de alinhamento -->
                    ${isCurrentUser ? '' : `<img src="/media/${message.sender.avatar_url}" class="rounded-circle me-3" alt="${message.sender.username}" width="40" height="40">`}
                    <div class="media-body">
                        <div class="${bgColorClass}">
                            <div class="${isCurrentUser ? 'title-current' : 'title-friend'}">
                                <h6 class="m-0" style="font-weight: bold;">${message.sender.username}</h6>
                                <small class="text-dark">${new Date(message.timestamp).toLocaleString()}</small>
                            </div>
                            <p class="m-0" style="font-size: 12pt; word-break: break-word; white-space: pre-wrap; max-width: 100%;">${formattedMessage}</p> <!-- Exibe o texto formatado -->
                        </div>
                    </div>
                    ${isCurrentUser ? `<img src="/media/${message.sender.avatar_url}" class="rounded-circle ms-3" alt="${message.sender.username}" width="40" height="40">` : ''}
                </div>`;
            });
    
            // Se houver mensagens não lidas, rolar para o final do chat
            if (data.has_unread_messages) {
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
    
        })
        .catch(error => console.error('Error:', error));
    }        


    function updateUnreadCounts() {
        $.ajax({
            url: '/app/api/get_unread_count/',  // URL correta
            method: 'GET',
            success: function(response) {
                // Atualiza os contadores de mensagens não lidas para cada amigo
                for (const [friendId, count] of Object.entries(response.unread_counts)) {
                    const $unreadCountElement = $(`#unread-count-${friendId}`);
                    
                    // Atualiza o contador para cada amigo
                    var valuenow = (count > 0) ? count : "";
                    $unreadCountElement.text(valuenow);
    
                    // Adiciona classes se a contagem for maior que zero
                    if (count > 0) {
                        $unreadCountElement.addClass('bg-success text-white'); // Adiciona classes
                    } else {
                        $unreadCountElement.removeClass('bg-success text-white'); // Remove classes se não houver mensagens não lidas
                    }
                }
            },
            error: function(xhr) {
                console.error('Erro ao carregar contadores de mensagens não lidas:', xhr.responseJSON.error);
            }
        });
    }
    
    $(document).ready(function() {
        updateUnreadCounts(); // Carrega contadores ao iniciar
        setInterval(updateUnreadCounts, 5000); // Atualiza contadores a cada 5 segundos
    });

    // Função para notificar que o usuário está ativo
    function setUserActive() {
        fetch('/app/api/set-user-active/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Inclua o token CSRF se necessário
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Atividade do usuário registrada:', data);
        })
        .catch(error => console.error('Erro ao registrar atividade do usuário:', error));
    }

    // Chama a função a cada 5 minuto
    setInterval(setUserActive, 300000); // 300000 ms = 5 minutos
    setUserActive();

    friendItems.forEach(item => {
    const friendId = item.getAttribute('data-friend-id');
    fetch(`/app/api/check-user-activity/${friendId}/`)
        .then(response => response.json())
        .then(data => {
            const status = item.querySelector('.friend-status');
            if (data.is_online) {
                status.classList.add('text-success');
                status.classList.remove('text-danger');
                status.innerText = 'Online';
            } else {
                status.classList.remove('text-success');
                status.classList.add('text-danger');
                status.innerText = 'Offline';
            }
        })
        .catch(error => console.error('Erro ao verificar status do amigo:', error));
    });
});
