// Функция для экранирования HTML
function escapeHtml(text) {
    return text.replace(/[&<>"'`=\/]/g, function(s) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;',
            '`': '&#x60;',
            '=': '&#x3D;'
        }[s];
    });
}

// Функция для преобразования текста в кликабельные ссылки
function makeLinksClickable(text) {
    const urlPattern = /(\b(https?|ftp|file):\/\/[^\s]+)/ig;
    let result = '';
    let lastIndex = 0;
    let match;

    while ((match = urlPattern.exec(text)) !== null) {
        // Экранируем текст перед ссылкой
        result += escapeHtml(text.substring(lastIndex, match.index));
        // Добавляем кликабельную ссылку без инлайновых стилей
        const url = match[0];
        result += '<a href="' + escapeHtml(url) + '" target="_blank">' + escapeHtml(url) + '</a>';
        lastIndex = urlPattern.lastIndex;
    }
    // Экранируем оставшийся текст
    result += escapeHtml(text.substring(lastIndex));
    return result;
}

// Функция для форматирования времени
function formatTimestamp(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return 'Неизвестное время';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Получение параметров из URL
function getURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const chatId = urlParams.get('cid');
    const adminNick = urlParams.get('a');
    const userNick = urlParams.get('u');
    return { chatId, adminNick, userNick };
}

const { chatId, adminNick, userNick } = getURLParams();

// Проверка наличия необходимых параметров
if (!chatId || !adminNick || !userNick) {
    alert('Недостаточно параметров в URL для загрузки чата.');
}

// Отображение имен в заголовке чата
const chatHeader = document.getElementById('chat-header');
if (adminNick && userNick) {
    chatHeader.innerText = `Чат с ЛОХОМ # ${userNick}`;
}

// Получение элементов аудио
const sendSound = document.getElementById('send-sound');
const receiveSound = document.getElementById('receive-sound');

// Хранение ID уже отображённых сообщений
const displayedMessageIds = new Set();

// Флаг для прокрутки при загрузке страницы
window.scrollOnLoad = false;

// Функция для отправки сообщения
document.getElementById('send-button').addEventListener('click', async function () {
    const messageInput = document.getElementById('message-input');
    const messageText = messageInput.value.trim();

    if (messageText) {
        try {
            // Отправляем сообщение на сервер
            const response = await fetch('/api/messages', { // Используем относительный путь
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    chat_id: chatId,    // Уникальный идентификатор чата
                    role: 'admin',      // Роль отправителя
                    message: messageText
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ошибка при отправке сообщения.');
            }

            // Получаем созданное сообщение из ответа
            const createdMessage = await response.json();

            // Добавляем сообщение в чат
            appendMessage(createdMessage);

            // Проигрываем звук отправки
            sendSound.play();

            // Очищаем поле ввода
            messageInput.value = '';
            // Автопрокрутка при отправке сообщения удалена
        } catch (error) {
            console.error('Ошибка:', error);
            alert("Произошла ошибка при отправке сообщения: " + error.message);
        }
    }
});

// Функция для добавления сообщения в чат
function appendMessage(message) {
    const chatWindow = document.getElementById('chat-window');

    // Проверяем, было ли сообщение уже отображено
    if (displayedMessageIds.has(message.id)) {
        return; // Пропускаем уже отображённые сообщения
    }

    // Создание контейнера для сообщения
    const newMessage = document.createElement('div');
    // Добавляем класс 'sent' для сообщений от админа, 'received' для от пользователя
    newMessage.classList.add('message', message.role === 'admin' ? 'sent' : 'received');

    // Создание аватара
    if (message.role === 'user') {
        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.style.backgroundImage = 'url("avatars/user_avatar.png")'; // Путь к аватару пользователя
        newMessage.appendChild(avatar);
    }

    // Создание контейнера для содержимого сообщения и футера
    const messageBody = document.createElement('div');
    messageBody.classList.add('message-body');

    // Создание блока с текстом сообщения
    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    messageContent.innerHTML = makeLinksClickable(message.message);
    messageBody.appendChild(messageContent);

    // Создание блока с временной меткой и именем отправителя
    const messageFooter = document.createElement('div');
    messageFooter.classList.add('message-footer');
    const senderName = message.role === 'admin' ? adminNick : userNick;
    messageFooter.innerText = `Отправлено в ${formatTimestamp(message.timestamp)} | ${senderName}`;

    // Футер будет выравнен с помощью CSS классов

    messageBody.appendChild(messageFooter);
    newMessage.appendChild(messageBody);
    chatWindow.appendChild(newMessage);

    // Добавляем ID сообщения в Set
    displayedMessageIds.add(message.id);

    // Прокрутка вниз после добавления сообщения, только при загрузке страницы
    if (window.scrollOnLoad) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

// Функция для обновления чата
async function updateChat() {
    try {
        const response = await fetch(`/api/messages/${chatId}?role=admin`); // Используем относительный путь
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка при получении сообщений:', errorData.error || response.statusText);
            return;
        }
        const messages = await response.json();

        messages.forEach(message => {
            // Проверяем, было ли сообщение уже отображено
            if (displayedMessageIds.has(message.id)) {
                return; // Пропускаем уже отображённые сообщения
            }

            // Добавляем новое сообщение
            appendMessage(message);

            // Проигрываем звук получения сообщения
            receiveSound.play();
        });

        // Автопрокрутка при обновлении чата удалена

    } catch (error) {
        console.error('Ошибка при обновлении чата:', error);
    }
}

// Обновление чата каждые 2 секунды
setInterval(updateChat, 2000);

// Добавление отправки сообщения по нажатию Enter
document.getElementById('message-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('send-button').click();
    }
});

// Автоматическая прокрутка при загрузке страницы
window.onload = function() {
    const chatWindow = document.getElementById('chat-window');
    if (chatWindow) {
        console.log("Автопрокрутка при полной загрузке страницы");
        setTimeout(() => {
            chatWindow.scrollTop = chatWindow.scrollHeight;
            window.scrollOnLoad = true; // Флаг для прокрутки при загрузке
        }, 100); // Задержка 100 мс
    } else {
        console.error("Элемент с id 'chat-window' не найден");
    }
};
