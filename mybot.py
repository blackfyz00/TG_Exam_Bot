import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
import extension as exten
bot = telebot.TeleBot(config.token)
users = {}
sudo_password = "IMADMIN"

@bot.message_handler(commands=['start'])
def send_welcome(message):
       # Создаем инлайн-клавиатур
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Начать", callback_data='start'))
    bot.send_message(message.chat.id, text=config.init_message, reply_markup=keyboard)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query_main(call):

    user_id = call.message.chat.id
    if user_id not in users:
        users[user_id] = []

    if call.data == 'start':
        users[user_id] = []
        keyboard_init = InlineKeyboardMarkup()
        keyboard_init.row(InlineKeyboardButton("Записаться на экзамен", callback_data='group_rec'))
        keyboard_init.row(InlineKeyboardButton("Для админов", 
                                               callback_data='for_admins'))
        keyboard_init.row(InlineKeyboardButton("Посмотреть списки экзаменуемых и время", 
                                                callback_data='for_teach'))
        bot.send_message(call.message.chat.id, text='Выберите действие:', reply_markup=keyboard_init)

    if call.data.startswith('group_rec'):
        keyboard_record1 = exten.create_keyboard_from_dir(dirname='list_student', 
                                                         callback='exam_rec')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выберите группу на запись:", reply_markup=keyboard_record1)
        
    if call.data.startswith('for_admins'):
        keyboard_foradmins1 = InlineKeyboardMarkup()
        keyboard_foradmins1.row(InlineKeyboardButton("Изменить расписание и время экзаменов", 
                                                     callback_data='change_exam_list_for_groups'))
        keyboard_foradmins1.row(InlineKeyboardButton('Домой', callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Вы вошли в режим админа. Выберите действие:", 
                            reply_markup=keyboard_foradmins1)
        

    if call.data.startswith('for_teach'):
        keyboard_record2 = exten.create_keyboard_from_dir(dirname='list_student',  
                                                       callback='teach_watch_subject')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выберите группу для просмотра студентов:", 
                            reply_markup=keyboard_record2)

    if call.data.startswith('teach_watch_subject'):
        substring = call.data[len("teach_watch_subject_"):]
        users[user_id].append(substring)
        keyboard_record22 = exten.create_object_from_db(to_return='keyboard', 
                                                        column_name='Экзамен', 
                                                        callback='teach_watch_group',
                                                        group=users[user_id][0])
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Вы выбрали группу {users[user_id][0]}. Выберите экзамен для просмотра:", 
                                reply_markup=keyboard_record22)
    
    if call.data.startswith('change_exam_list_for_groups'):
        keyboard_foradmins3 = InlineKeyboardMarkup()
        keyboard_foradmins3.row(InlineKeyboardButton("Очистить все очереди", 
                                                     callback_data='clean_queue'))
        keyboard_foradmins3.row(InlineKeyboardButton("Добавить очередь на экзамен", 
                                                     callback_data='add_queue'))
        keyboard_foradmins3.row(InlineKeyboardButton("Удалить очередь на экзамен", 
                                                     callback_data='remove_queue'))
        keyboard_foradmins3.row(InlineKeyboardButton('Домой', callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Вы вошли в режим работы с очередями. Выберите действие:", 
                            reply_markup=keyboard_foradmins3)
        

    if call.data.startswith('clean_queue'):
        keyboard_foradmins4 = InlineKeyboardMarkup()
        keyboard_foradmins4.row(InlineKeyboardButton("Подтвердить", 
                                                     callback_data='rsudo_all_queue'))
        keyboard_foradmins4.row(InlineKeyboardButton('Отмена', callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                    message_id=call.message.message_id, 
                    text="Подтвердите удаление очередей.", 
                    reply_markup=keyboard_foradmins4)

    if call.data.startswith('rsudo_all_queue'):
        keyboard_foradmins2 = InlineKeyboardMarkup()
        keyboard_foradmins2.row(InlineKeyboardButton('Домой', callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Введите пароль", 
                                reply_markup=keyboard_foradmins2)
        bot.register_next_step_handler(call.message, lambda msg: handle_password(msg, info='queue'))
        
        
    if call.data.startswith('add_queue'):
        keyboard_addqueue = exten.create_keyboard_from_dir(dirname='list_student', 
                                                         callback='add_group_inqueue')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выберите группу на добавление в очередь:", 
                            reply_markup=keyboard_addqueue)
        
    if call.data.startswith('add_group_inqueue'):
        substring = call.data[len("add_group_inqueue_"):]
        users[user_id].append(substring)
        keyboard_foradmins2 = InlineKeyboardMarkup()
        keyboard_foradmins2.row(InlineKeyboardButton('Домой', callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text="Введите название предмета и время через пробел, например: Алгебра 14:00", 
                                reply_markup=keyboard_foradmins2)
        bot.register_next_step_handler(call.message, lambda msg: input_subject_time(msg, info=users[user_id], time=msg.text.split()[-1]))

    if call.data.startswith('remove_queue'):
        keyboard_rqueue = exten.create_keyboard_from_dir(dirname='db_groups', 
                                                         callback='remove_groupqueue')
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выберите группу:", 
                            reply_markup=keyboard_rqueue)

    if call.data.startswith('remove_groupqueue'):
        substring = call.data[len("remove_groupqueue_"):]
        users[user_id].append(substring)
        keyboard_rqueue = exten.create_object_from_db(to_return='keyboard', 
                                                         callback='remove_Ygroupqueue',
                                                         group=users[user_id][0]
                                                         )
        bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id, 
                            text="Отлично! Выберите очередь на удаление:", 
                            reply_markup=keyboard_rqueue)    

    if call.data.startswith('remove_Ygroupqueue'):
        substring = call.data[len("remove_Ygroupqueue_"):]
        substring = substring.split('_')
        for item in substring:
            users[user_id].append(item)
        keyboard_foradmins2 = InlineKeyboardMarkup()
        keyboard_foradmins2.row(InlineKeyboardButton("Подтвердить", 
                                                     callback_data='remove_groupqueue_reset'))
        keyboard_foradmins2.row(InlineKeyboardButton('Домой', callback_data='start'))
        bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id, 
                                text=f"Подтвердите сброс очереди {users[user_id][1]}: {users[user_id][2]}", 
                                reply_markup=keyboard_foradmins2)