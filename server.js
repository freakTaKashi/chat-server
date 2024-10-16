const express = require('express');
const path = require('path'); // Для работы с путями
const app = express();
const cors = require('cors');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid'); // Импортируем uuid

let chats = {}; // Хранилище сообщений по chat_id
let carts = {}; // Хранилище данных корзин

app.use(cors());
app.use(bodyParser.json());

// Обслуживание статических файлов из папки 'public'
app.use(express.static(path.join(__dirname, 'public')));

// Маршрут для cart.html с параметром link_id
app.get('/cart.html/:link_id', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'cart.html'));
});

// Маршрут для получения данных корзины по link_id
app.get('/api/cart/:link_id', (req, res) => {
    const { link_id } = req.params;
    console.log(`Запрос на получение корзины с link_id: ${link_id}`); // Добавлено логирование

    const cartData = carts[link_id];

    if (cartData) {
        res.json(cartData);
    } else {
        console.log(`Корзина с link_id ${link_id} не найдена`); // Добавлено логирование
        res.status(404).json({ error: 'Корзина не найдена' });
    }
});

// Маршрут для создания новой корзины (данные от бота)
app.post('/api/cart', (req, res) => {
    const cartData = req.body;
    const { link_id } = cartData;

    if (!link_id) {
        return res.status(400).json({ error: 'link_id обязателен' });
    }

    carts[link_id] = cartData;

    console.log(`Корзина с link_id ${link_id} создана:`, cartData); // Добавлено логирование

    res.status(201).json({ message: 'Корзина создана', cart: cartData });
});

// Обработка POST-запроса для добавления нового сообщения
app.post('/api/messages', (req, res) => {
    const { chat_id, role, message } = req.body;

    if (!chat_id || !role || !message) {
        return res.status(400).json({ error: 'Bad Request: chat_id, role, and message are required.' });
    }

    if (!chats[chat_id]) {
        chats[chat_id] = [];
    }

    // Присваиваем уникальный ID и текущую дату и время в формате ISO
    const msgId = uuidv4();
    const msgTimestamp = new Date().toISOString();

    console.log(`Received message: [${chat_id}] ${role} at ${msgTimestamp} - ${message}`);

    // Создаем объект сообщения
    const newMessage = { id: msgId, role, message, timestamp: msgTimestamp, read: false };

    // Добавляем сообщение в хранилище
    chats[chat_id].push(newMessage);

    // Отправляем созданное сообщение обратно клиенту в формате JSON
    res.status(200).json(newMessage);
});

// Обработка GET-запроса для получения сообщений по chat_id
app.get('/api/messages/:chat_id', (req, res) => {
    const { chat_id } = req.params;
    const role = req.query.role; // 'admin' или 'user'

    if (!role || !['admin', 'user'].includes(role)) {
        return res.status(400).json({ error: 'Bad Request: role query parameter is required and must be "admin" or "user".' });
    }

    const messages = chats[chat_id] || [];

    res.json(messages);
});

// Запуск сервера на порту 3000
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
