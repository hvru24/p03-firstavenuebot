import telebot
import sqlite3
from telebot import types
import threading
import schedule
import time

token = '6918807936:AAFQdo6qHN3JHLJCokg9oH1jIVWxa6H1BCM'
chat_ids = [718189301, 1133254892]

bot = telebot.TeleBot(token)

tasks = {
    'hvru': [
        {'Утренняя зарядка': False},
        {'Гвоздестояние': False},
        {'Холодный душ': False},
        {'ЛКУ в 12:00': False},
        {'ЛКУ в 15:00': False},
        {'ЛКУ в 18:00': False}
    ],
    'uki': [
        {'Утренняя зарядка': False},
        {'Гвоздестояние': False},
        {'Холодный душ': False},
        {'ЛКУ в 12:00': False},
        {'ЛКУ в 15:00': False},
        {'ЛКУ в 18:00': False}
    ]
}

week_tasks = {
    'hvru': [
        {'Холодная ванна 10 минут': False},
        {'Поход в горы': False},
    ],
    'uki': [
        {'Холодная ванна 10 минут': False},
        {'Поход в горы': False},
    ]
}

exp_dict = {'утренняя зарядка': 5,
        'гвоздестояние': 15,
        'холодный душ': 10,
        'лку в 12:00': 3,
        'лку в 15:00': 3,
        'лку в 18:00': 3,
        'холодная ванна 10 минут': 20,
        'поход в горы': 30
}

rank_list = [
    "Симулякр",
    "Адепт",
    "Перфекционист",
    "Открыватель",
    "Искатель",
    "Познаватель",
    "Стремительный",
    "Исследователь",
    "Знаток",
    "Бывалый",
    "Авантюрист",
    "Виртуоз",
    "Эксперт",
    "Корифей",
    "Мастер",
    "Просветленный",
    "Гуру",
    "Магистр",
    "Герой",
    "Легенда",
    "Превосходящий",
    "Величайший",
    "Авторитет",
    "Апекс",
    "Абсолют",
    "Луминар"
]

def reset_daily_tasks():
    global tasks
    for username in tasks:
        for task_dict in tasks[username]:
            for task_name in task_dict:
                task_dict[task_name] = False
    bot.send_message(chat_ids[0], "Ежедневные задания обновились!")
    bot.send_message(chat_ids[1], "Ежедневные задания обновились!")

def reset_weekly_tasks():
    global week_tasks
    for username in week_tasks:
        for task_dict in week_tasks[username]:
            for task_name in task_dict:
                task_dict[task_name] = False
    bot.send_message(chat_ids[0], "Еженедельные задания обновились!")
    bot.send_message(chat_ids[1], "Еженедельные задания обновились!")

def lku_notification():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
        types.KeyboardButton("Ежедневные задания")
    )
    bot.send_message(chat_ids[0], "Время выполнить комплекс упражнений!\n\nПоднятия на носки: 30 раз\nПриседания: 30 раз\nУпражнение Кегеля: 100 раз", reply_markup=keyboard)
    bot.send_message(chat_ids[1], "Время выполнить комплекс упражнений!\n\nПоднятия на носки: 30 раз\nПриседания: 30 раз\nУпражнение Кегеля: 100 раз", reply_markup=keyboard)

def schedule_task():
    schedule.every().day.at("00:00", "Asia/Almaty").do(reset_daily_tasks)
    schedule.every().monday.at("00:00", "Asia/Almaty").do(reset_weekly_tasks)
    times = ["12:00", "15:00", "18:00"]
    for time in times:
        schedule.every().day.at(time, "Asia/Almaty").do(lku_notification)

def poll_bot():
    while True:
        bot.infinity_polling()

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def update_progress(username, exp):
    conn = sqlite3.connect('character.db')
    conn.execute(f"UPDATE users SET experience = experience + {exp} WHERE username = '{username}'")
    level = conn.execute(f"SELECT level FROM users WHERE username = '{username}'").fetchone()[0]
    experience = conn.execute(f"SELECT experience FROM users WHERE username = '{username}'").fetchone()[0]
    required_experience = 0
    for i in range(1, level + 2):
        required_experience += int(40 + (i - 1) * 1.5)
    if experience >= required_experience and level < 250:
        level += 1
        conn.execute(f"UPDATE users SET level = {level} WHERE username = '{username}'")
        index = min(level // 10, len(rank_list) - 1)
        conn.execute(f"UPDATE users SET rank = '{rank_list[index]}' WHERE username = '{username}'")
    conn.commit()
    conn.close()

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.id in chat_ids:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
            types.KeyboardButton("Ежедневные задания"),
            types.KeyboardButton("Персонажи"),
            types.KeyboardButton("Еженедельные задания"),
            types.KeyboardButton("Статистика"),
            types.KeyboardButton("Меню")
        )
        gif_path = 'menu.gif'
        with open(gif_path, 'rb') as gif:
            bot.send_animation(message.chat.id, gif, caption="First Avenue\n\nДобро пожаловать, avenuer!\n\nВам посчастливилось иметь доступ!\nКуда отправитесь дальше?", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к использованию бота.")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.id in chat_ids:
        if message.text.lower() == "меню":
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                types.KeyboardButton("Ежедневные задания"),
                types.KeyboardButton("Персонажи"),
                types.KeyboardButton("Еженедельные задания"),
                types.KeyboardButton("Статистика")
            )
            gif_path = 'menu.gif'
            with open(gif_path, 'rb') as gif:
                bot.send_animation(message.chat.id, gif, caption="Вы в главном меню, avenuer!\n\nВремя повышать уровень!\n\nКуда отправитесь дальше?", reply_markup=keyboard)

        if message.text.lower() == "персонажи":
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                types.KeyboardButton("Меню")
            )
            for username in ['hvru', 'uki']:
                conn = sqlite3.connect('character.db')
                level = conn.execute(f"SELECT level FROM users WHERE username = '{username}'").fetchone()
                exp = conn.execute(f"SELECT experience FROM users WHERE username = '{username}'").fetchone()
                rank = conn.execute(f"SELECT rank FROM users WHERE username = '{username}'").fetchone()
                bot.send_message(message.chat.id, f"👾 Персонаж: {username}\n\n💠 Уровень: {level[0]}\n🔆 Опыт персонажа: {exp[0]}\n⚜️ Ранг: {rank[0]}", reply_markup=keyboard)
                conn.close()

        elif message.text.lower() == "ежедневные задания":
            if message.chat.id == chat_ids[0]:
                username = 'hvru'
            elif message.chat.id == chat_ids[1]:
                username = 'uki'
            active_tasks = [f"- {task_name}" for task_dict in tasks[username] for task_name, done in task_dict.items() if not done]

            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            buttons = []
            for task_name in active_tasks:
                button = types.KeyboardButton(task_name[2:])
                buttons.append(button)
            button7 = types.KeyboardButton("Меню")
            buttons.append(button7)
            keyboard.add(*buttons)

            done_tasks = [f"- {task_name}" for task_dict in tasks[username] for task_name, done in task_dict.items() if done]
            active_tasks_message = '\n'.join(active_tasks) if active_tasks else "Все задания выполнены!"
            done_tasks_message = '\n'.join(done_tasks) if done_tasks else "Выполненных заданий еще нет."
            bot.send_message(message.chat.id, f"Персонаж: {username}\n\nМинимальная квота:\nУтренняя зарядка: 10 минут\nХолодный душ: 3 минуты\nГвоздестояние: 1 минута\n\n🟡 Активные задания:\n{active_tasks_message}\n\n🟢 Выполненные задания:\n{done_tasks_message}", reply_markup=keyboard)

        elif message.text.lower() in ["утренняя зарядка", "гвоздестояние", "холодный душ", "лку в 12:00", "лку в 15:00", "лку в 18:00"]:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                types.KeyboardButton("Ежедневные задания"),
                types.KeyboardButton("Персонажи"),
                types.KeyboardButton("Еженедельные задания"),
                types.KeyboardButton("Статистика")
            )
            task_name = message.text.lower()
            if message.chat.id == chat_ids[0]:
                username = 'hvru'
            elif message.chat.id == chat_ids[1]:
                username = 'uki'

            for task_dict in tasks[username]:
                for task_name_dict, done in task_dict.items():
                    if task_name_dict.lower() == task_name and done:
                        bot.send_message(message.chat.id, "Задание уже выполнено.", reply_markup=keyboard)
                        return

            bot.send_message(message.chat.id, f"{task_name.capitalize()} выполнено. Опыт персонажа повышен!", reply_markup=keyboard)

            exp = exp_dict[task_name]
            update_progress(username, exp)

            for task_dict in tasks[username]:
                for task_name in task_dict.keys():
                    if task_name.lower() == message.text.lower():
                        task_dict[task_name] = True
                        break

        elif message.text.lower() == "еженедельные задания":
            if message.chat.id == chat_ids[0]:
                username = 'hvru'
            elif message.chat.id == chat_ids[1]:
                username = 'uki'
            active_tasks = [f"- {task_name}" for task_dict in week_tasks[username] for task_name, done in task_dict.items() if not done]

            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            buttons = []
            for task_name in active_tasks:
                button = types.KeyboardButton(task_name[2:])
                buttons.append(button)
            button7 = types.KeyboardButton("Меню")
            buttons.append(button7)
            keyboard.add(*buttons)

            done_tasks = [f"- {task_name}" for task_dict in week_tasks[username] for task_name, done in task_dict.items() if done]
            active_tasks_message = '\n'.join(active_tasks) if active_tasks else "Все задания выполнены!"
            done_tasks_message = '\n'.join(done_tasks) if done_tasks else "Выполненных заданий еще нет."
            bot.send_message(message.chat.id, f"Персонаж: {username}\n\n🟡 Активные задания:\n{active_tasks_message}\n\n🟢 Выполненные задания:\n{done_tasks_message}", reply_markup=keyboard)

        elif message.text.lower() in ["холодная ванна 10 минут", "поход в горы"]:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                types.KeyboardButton("Ежедневные задания"),
                types.KeyboardButton("Персонажи"),
                types.KeyboardButton("Еженедельные задания"),
                types.KeyboardButton("Статистика")
            )
            task_name = message.text.lower()
            if message.chat.id == chat_ids[0]:
                username = 'hvru'
            elif message.chat.id == chat_ids[1]:
                username = 'uki'

            for task_dict in week_tasks[username]:
                for task_name_dict, done in task_dict.items():
                    if task_name_dict.lower() == task_name and done:
                        bot.send_message(message.chat.id, "Задание уже выполнено.", reply_markup=keyboard)
                        return

            bot.send_message(message.chat.id, f"{task_name.capitalize()} выполнено. Опыт персонажа повышен!", reply_markup=keyboard)

            exp = exp_dict[task_name]
            update_progress(username, exp)

            for task_dict in week_tasks[username]:
                for task_name in task_dict.keys():
                    if task_name.lower() == message.text.lower():
                        task_dict[task_name] = True
                        break
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к использованию бота.")

if __name__ == '__main__':
    for id in chat_ids:
        bot.send_message(id, "Внимание! Бот был перезапущен!")

    schedule_task_thread = threading.Thread(target=schedule_task)
    schedule_task_thread.start()

    bot_thread = threading.Thread(target=poll_bot)
    bot_thread.start()

    run_schedule()
