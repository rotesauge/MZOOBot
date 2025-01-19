from models import *
from conf import *
from quiz import *
import telebot
import logging


# with SessionLocal() as db:
#     qq =  db.query(Commands).all()
#     commands = [item.title for item in qq]



def create_keyboard(*buttons):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    for button in buttons:
       keyboard.add(telebot.types.KeyboardButton(button))
    return keyboard

# def create_inline_keyboard(*buttons):
#     keyboard = telebot.types.InlineKeyboardMarkup ()
#     for button in buttons:
#        keyboard.add(telebot.types.InlineKeyboardButton(button, callback_data='btn'))
#     return keyboard



def start_help_handler(msg,bot):
    db = SessionLocal()
    if db.query(User_Condition).filter(User_Condition.TgUserId == msg.chat.id).first():
        Cond = db.query(User_Condition).filter(User_Condition.TgUserId == msg.chat.id).first()
        Cond.CurentCond = StatusEnum.START
    else:
        UsID = get_cur_id(db, User_Condition)
        cond = User_Condition(id=UsID,
                              CurentCond=StatusEnum.START,
                              TgUserId=msg.chat.id)
        db.add(cond)
    db.commit()
    if msg.chat.id == ADMIN_ID:
        keyboard = create_keyboard('Узнать свое тотемное животное','message','Добавить Вопрос','добавить результат','сообщения пользователей')
    else:
        keyboard = create_keyboard('Узнать свое тотемное животное', 'Программа опеки', 'Оставить отзыв')
    te = """Привет! Я — бот Московского зоопарка! Здесь вы можете пройти увлекательную викторину, '
    <i>чтобы узнать свое тотемное животное</i>
     а также получить информацию о программе '
    'опеки над нашими обитателями.\n\n'
    '<b>Команда:</b> /start - запускает меня'""",
    bot.send_message(msg.chat.id, te, reply_markup = keyboard, parse_mode ='HTML')



# def show_start_keyboard(bot, chat_id):
#     with open('Pig/start.jpg', 'rb') as photo:
#
#         bot.sendPhoto(chat_id, photo=photo)
#     bot.sendMessage(chat_id,
#                     reply_markup=keyboard, parse_mode='HTML')
 #
 # start_help_handler()
 #    text = ''
 #    with Session as db:
 #        if db.query(User_Condition).filter(User_Condition.TgUserId == message.chat.id).first():
 #            Cond = db.query(User_Condition).filter(User_Condition.TgUserId == message.chat.id).first()
 #            Cond.CurentCond = 'start'
 #        else:
 #            UsID = get_cur_id(db, User_Condition)
 #            cond = User_Condition(id=UsID,
 #                                  CurentCond='start',
 #                                  TgUserId=message.chat.id)
 #            db.add(cond)
 #        db.commit()
 #        greet = f"Добро пожаловать, {message.chat.username}\n"
 #        text = greet
 #    bot.send_message(message.chat.id,text)

def text_handler(msg,bot):
    command = msg.text.lower()
    chat_id = msg.chat.id
    db =  SessionLocal()
    UserC = db.query(User_Condition).filter(User_Condition.TgUserId == msg.chat.id).first()
    if UserC:
        CurentCond = UserC.CurentCond
    else:
        start_help_handler(msg,bot)
        return

    if CurentCond == StatusEnum.ENTERR:
        list_a = msg.text.split(',')
        if len(list_a) != 3:
            bot.send_message(msg.chat.id, "Неверный ввод!! Введите результат в формате: Текст результата,0,10(где 0 и 10 границы очков)")
            return
        UsID = get_cur_id(db, Results)
        result = Results(id=UsID,
                      title=list_a[0],
                      pointsmin=int(list_a[1]),
                      pointsmax=int(list_a[2]))
        db.add(result)
        db.commit()
        start_help_handler(msg, bot)
        return

    if CurentCond == StatusEnum.ENTERQ:
        UsID = get_cur_id(db, Questions)
        question = Questions(id=UsID,
                            title=msg.text)
        db.add(question)
        UserC.curent_question = question.id
        UserC.CurentCond = StatusEnum.ENTERA
        db.commit()
        bot.send_message(msg.chat.id, "Введите ответ и количество очков через запятую")
        return

    if CurentCond == StatusEnum.ENTERA:
        if command == 'завершить ввод ответов':
            UserC.curent_question = 0
            db.commit()
            start_help_handler(msg, bot)
            return
        list_a = msg.text.split(',')
        if len(list_a) != 2:
            bot.send_message(msg.chat.id, "Неверный ввод!! Введите ответ и количество очков через запятую")
            return
        UsID = get_cur_id(db, Answers)
        ans = Answers(id=UsID,
                           id_question = UserC.curent_question,
                           title=list_a[0],
                           points = int(list_a[1]))
        db.add(ans)
        db.commit()
        bot.send_message(msg.chat.id, "Введите ответ и количество очков через запятую",reply_markup = create_keyboard('Завершить ввод ответов'))
        return

    if command == 'Вернуться в главное меню':
        return start_help_handler(msg,bot)

    if command == 'message':
        if msg.chat.id == ADMIN_ID:
            bot.send_message(msg.chat.id, msg)
            return

    if command == 'добавить вопрос':
        if msg.chat.id == ADMIN_ID:
            UserC.CurentCond = StatusEnum.ENTERQ
            db.commit()
            bot.send_message(msg.chat.id, "Введите вопрос")
            return

    if command == 'добавить результат':
        if msg.chat.id == ADMIN_ID:
            UserC.CurentCond = StatusEnum.ENTERR
            db.commit()
            bot.send_message(msg.chat.id, "Введите результат в формате: Текст результата,0,10(где 0 и 10 границы очков)")
            return

    if command == 'Завершить Редактирование':
        if msg.chat.id == ADMIN_ID:
            bot.send_message(msg.chat.id, msg)
            return

    if CurentCond == StatusEnum.START:
        if command == 'узнать свое тотемное животное':
            UserC.CurentCond = StatusEnum.QUIZ
            db.commit()

            UsID = get_cur_id(db, Quiz)
            quiz = Quiz(id=UsID,
                        stoped=False,
                        started = False,
                        curent_points = 0,
                        TgUserId=msg.chat.id)
            db.add(quiz)
            db.commit()
            next_question(chat_id, db,UserC, quiz, bot, None)

        if command == 'Программа опеки':
            Cond = db.query(User_Condition).filter(User_Condition.TgUserId == msg.chat.id).first()
            Cond.CurentCond = StatusEnum.GUARDIANSHIP
            db.commit()
        if command == 'Оставить отзыв':
            Cond = db.query(User_Condition).filter(User_Condition.TgUserId == msg.chat.id).first()
            Cond.CurentCond = StatusEnum.FEEDBACK
            db.commit()

    if CurentCond == StatusEnum.FEEDBACK:
        pass

    if CurentCond == StatusEnum.QUIZ:
        quiz = db.query(Quiz).filter(User_Condition.TgUserId == msg.chat.id).first()
        if quiz:
            current_answers = db.query(Answers).filter(Answers.id_question == UserC.curent_question)
            for ans in current_answers:
                if ans.title.lower() == command:
                    next_question(chat_id, db,UserC, quiz, bot,ans)
                    return
        return start_help_handler(msg,bot)

    if CurentCond == StatusEnum.GUARDIANSHIP:
        pass

    # Обработка мультимедийных сообщений
    if command in ['photo', 'video', 'document', 'audio', 'sticker', 'animation', 'voice']:
        bot.send_message(chat_id, "Бот работает только с командами. Пожалуйста, используйте клавиши для взаимодействия.")
        logging.warning(f"Мультимедийное сообщение проигнорировано от пользователя {chat_id}.")
        return
    if not command:
        logging.warning(f"Получено сообщение без текста от пользователя {chat_id}: {msg}")
        return
    else:
        logging.warning(f"Пользователь {chat_id} отправил нераспознанную команду: {command}")
        bot.send_message(chat_id, "Бот работает только с командами. Пожалуйста, используйте клавиши для взаимодействия.")


    # if chat_id == int(ADMIN_ID):
    #     if reply_to_user(msg, bot, user_questions):
    #         return
    # # Команды викторины
    # elif command == 'Узнать свое тотемное животное':
    #     start_victorina(chat_id, bot)
    # elif command == 'Запустить вопросы заново':
    #     start_victorina(chat_id, bot)
    # elif command == 'Остановить викторину':
    #     logging.info(f"Пользователь {chat_id} остановил викторину")
    #     show_start_keyboard(bot, chat_id)
    #     user_scores[chat_id] = {'score': 0, 'current_question': 0}
    # # Обработка ответа на вопросы викторины
    # elif chat_id in user_scores and user_scores[chat_id]['current_question'] < len(questions) and command in \
    #         questions[user_scores[chat_id]['current_question']]["answers"]:
    #     index = questions[user_scores[chat_id]['current_question']]["answers"].index(command)
    #     user_scores[chat_id]['score'] += questions[user_scores[chat_id]['current_question']]['points'][index]
    #     user_scores[chat_id]['current_question'] += 1
    #     logging.info(f"Пользователь {chat_id} ответил на вопрос, ответом '{command}'")
    #     start_victorina(chat_id, bot)
    # # Обработка общения с администратором
    # elif command == 'Узнать подробнее':
    #     logging.info(f"Пользователь {chat_id} инициировал диалог с администратором.")
    #     result = user_scores.get(chat_id, {}).get('result',
    #                                               "Пользователь ещё не проходил викторину или результат был сброшен.")
    #     bot.sendMessage(chat_id, "Введите свой вопрос:", reply_markup=ReplyKeyboardMarkup(
    #         keyboard=[[KeyboardButton(text='Остановить разговор')]], resize_keyboard=True))
    #     user_questions[chat_id] = {'state': 'active', 'question_msg_id': None, 'result': result}
    # elif chat_id in user_questions and user_questions[chat_id]['state'] == 'active':
    #     if command == 'Остановить разговор':
    #         logging.info(f"Пользователь {chat_id} завершил диалог с администратором.")
    #         bot.sendMessage(admin_chat_id, f"Пользователь с ID {chat_id} завершил диалог.")
    #         show_start_keyboard(bot, chat_id)
    #         user_questions.pop(chat_id, None)
    #     else:
    #         if chat_id in user_scores:
    #             result = user_questions[chat_id].get('result', "Результат викторины не определён.")
    #             user_question_text = msg.get('text')
    #             question_msg = bot.sendMessage(admin_chat_id, f"Вопрос от пользователя {chat_id}:\n"
    #                                                           f"{user_question_text}\n\n"
    #                                                           f"Результат викторины: {result}")
    #             user_questions[chat_id]['question_msg_id'] = question_msg['message_id']
    #             bot.sendMessage(chat_id, "Ваш вопрос отправлен администратору, ждите ответа.")
    #             logging.info(f"Пользователь {chat_id} отправил сообщение администратору: {user_question_text}")
    # # Команды для отзыва
    # elif command == 'Оставить отзыв':
    #     logging.info(f"Пользователь {chat_id} начал оставлять отзыв.")
    #     with open('Pig/feedbacks.jpg', 'rb') as photo:
    #         bot.sendPhoto(chat_id, photo=photo)
    #     bot.sendMessage(chat_id, "Пожалуйста, оставьте свой отзыв:", reply_markup=ReplyKeyboardMarkup(
    #         keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True))
    #     user_questions[chat_id] = {'state': 'waiting_for_feedback'}
    # elif command == 'Отмена' and chat_id in user_questions:
    #     logging.info(f"Пользователь {chat_id} отменил оставление отзыва.")
    #     show_start_keyboard(bot, chat_id)
    #     user_questions.pop(chat_id, None)
    # elif chat_id in user_questions and user_questions[chat_id].get('state') == 'waiting_for_feedback':
    #     feedback_text = msg.get('text')
    #     save_feedback(feedback_text, chat_id)
    #     bot.sendMessage(chat_id, "Ваш отзыв был отправлен. Спасибо!", reply_markup=show_start_keyboard(bot, chat_id))
    #     user_questions.pop(chat_id, None)
    # # Команда программы опеки
    #
    # elif command == 'Посмотреть программу опеки':
    #     logging.info(f"Пользователь {chat_id} запросил программу опеки.")
    #     with open('Pig/programm.jpg', 'rb') as photo:
    #         bot.sendPhoto(chat_id, photo=photo)
    #     keyboard = ReplyKeyboardMarkup(
    #         keyboard=[[KeyboardButton(text='Узнать свое тотемное животное')],
    #                   [KeyboardButton(text='Вернуться в главное меню')]],
    #         resize_keyboard=True
    #     )
    #     bot.sendMessage(chat_id, care_program_text, reply_markup=keyboard, parse_mode="Markdown")
    # # Ответ по умолчанию для нераспознанных команд

# return{ "chat_id":msg.chat.id,"text":msg.text}


#
#
#     with Session as db:
#         qq = db.query(Commands).all()
#         for item in qq:
#             button = telebot.types.InlineKeyboardButton(item.title, callback_data=item.id)
#             keyboard.add(button)
#     bot.send_message(message.chat.id, text='Keyboard example', reply_markup=keyboard)
#
#
#
#
# @bot.message_handler(commands=commands)
# def begin(message: telebot.types.Message):
#         bot.send_message(message.chat.id,text)
# #         # bot.reply_to(message, Convertor.get_all_valutes())
#
# button_foo =
# button_bar = types.InlineKeyboardButton('Bar', callback_data='bar')
#
# keyboard.add(button_foo)
# keyboard.add(button_bar)
#
# bot.send_message(chat_id, text='Keyboard example', reply_markup=keyboard)
#
#     values = message.text.split(' ')
#     try:
#         if len(values) != 3:
#             raise ConvertException('Неверное количество параметров!')
#         cur1, cur2, amount = values
#         answer = Convertor.get_price(cur1.upper(), cur2.upper(), amount)
#     except ConvertException as e:
#         bot.reply_to(message, f"Ошибка в команде:\n{e}")
#     except Exception as e:
#         traceback.print_tb(e.__traceback__)
#         bot.reply_to(message, f"Неизвестная ошибка:\n{e}")
#     else:
#         bot.reply_to(message, answer)
#
#
# button_foo = types.InlineKeyboardButton('Foo', callback_data='foo')
# button_bar = types.InlineKeyboardButton('Bar', callback_data='bar')
#
# keyboard = types.InlineKeyboardMarkup()
# keyboard.add(button_foo)
# keyboard.add(button_bar)
#
# bot.send_message(chat_id, text='Keyboard example', reply_markup=keyboard)
#
#
#
#
# def handle_message(msg, bot):
#     chat_id = msg['chat']['id']
#     command = msg.get('text')
#
#     # Обработка мультимедийных сообщений
#     if any(key in msg for key in ['photo', 'video', 'document', 'audio', 'sticker', 'animation', 'voice']):
#         bot.sendMessage(chat_id, "Бот работает только с командами. Пожалуйста, используйте клавиши для взаимодействия.")
#         logging.warning(f"Мультимедийное сообщение проигнорировано от пользователя {chat_id}.")
#         return
#     if not command:
#         logging.warning(f"Получено сообщение без текста от пользователя {chat_id}: {msg}")
#         return
#
#     if chat_id == int(admin_chat_id):
#         if reply_to_user(msg, bot, user_questions):
#             return
#     if command == '/start':
#         show_start_keyboard(bot, chat_id)
#     elif command == 'Вернуться в главное меню':
#         show_start_keyboard(bot, chat_id)
#     # Команды викторины
#     elif command == 'Узнать свое тотемное животное':
#         start_victorina(chat_id, bot)
#     elif command == 'Запустить вопросы заново':
#         start_victorina(chat_id, bot)
#     elif command == 'Остановить викторину':
#         logging.info(f"Пользователь {chat_id} остановил викторину")
#         show_start_keyboard(bot, chat_id)
#         user_scores[chat_id] = {'score': 0, 'current_question': 0}
#     # Обработка ответа на вопросы викторины
#     elif chat_id in user_scores and user_scores[chat_id]['current_question'] < len(questions) and command in \
#             questions[user_scores[chat_id]['current_question']]["answers"]:
#         index = questions[user_scores[chat_id]['current_question']]["answers"].index(command)
#         user_scores[chat_id]['score'] += questions[user_scores[chat_id]['current_question']]['points'][index]
#         user_scores[chat_id]['current_question'] += 1
#         logging.info(f"Пользователь {chat_id} ответил на вопрос, ответом '{command}'")
#         start_victorina(chat_id, bot)
#     # Обработка общения с администратором
#     elif command == 'Узнать подробнее':
#         logging.info(f"Пользователь {chat_id} инициировал диалог с администратором.")
#         result = user_scores.get(chat_id, {}).get('result',
#                                                   "Пользователь ещё не проходил викторину или результат был сброшен.")
#         bot.sendMessage(chat_id, "Введите свой вопрос:", reply_markup=ReplyKeyboardMarkup(
#             keyboard=[[KeyboardButton(text='Остановить разговор')]], resize_keyboard=True))
#         user_questions[chat_id] = {'state': 'active', 'question_msg_id': None, 'result': result}
#     elif chat_id in user_questions and user_questions[chat_id]['state'] == 'active':
#         if command == 'Остановить разговор':
#             logging.info(f"Пользователь {chat_id} завершил диалог с администратором.")
#             bot.sendMessage(admin_chat_id, f"Пользователь с ID {chat_id} завершил диалог.")
#             show_start_keyboard(bot, chat_id)
#             user_questions.pop(chat_id, None)
#         else:
#             if chat_id in user_scores:
#                 result = user_questions[chat_id].get('result', "Результат викторины не определён.")
#                 user_question_text = msg.get('text')
#                 question_msg = bot.sendMessage(admin_chat_id, f"Вопрос от пользователя {chat_id}:\n"
#                                                               f"{user_question_text}\n\n"
#                                                               f"Результат викторины: {result}")
#                 user_questions[chat_id]['question_msg_id'] = question_msg['message_id']
#                 bot.sendMessage(chat_id, "Ваш вопрос отправлен администратору, ждите ответа.")
#                 logging.info(f"Пользователь {chat_id} отправил сообщение администратору: {user_question_text}")
#     # Команды для отзыва
#     elif command == 'Оставить отзыв':
#         logging.info(f"Пользователь {chat_id} начал оставлять отзыв.")
#         with open('Pig/feedbacks.jpg', 'rb') as photo:
#             bot.sendPhoto(chat_id, photo=photo)
#         bot.sendMessage(chat_id, "Пожалуйста, оставьте свой отзыв:", reply_markup=ReplyKeyboardMarkup(
#             keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True))
#         user_questions[chat_id] = {'state': 'waiting_for_feedback'}
#     elif command == 'Отмена' and chat_id in user_questions:
#         logging.info(f"Пользователь {chat_id} отменил оставление отзыва.")
#         show_start_keyboard(bot, chat_id)
#         user_questions.pop(chat_id, None)
#     elif chat_id in user_questions and user_questions[chat_id].get('state') == 'waiting_for_feedback':
#         feedback_text = msg.get('text')
#         save_feedback(feedback_text, chat_id)
#         bot.sendMessage(chat_id, "Ваш отзыв был отправлен. Спасибо!", reply_markup=show_start_keyboard(bot, chat_id))
#         user_questions.pop(chat_id, None)
#     # Команда программы опеки
#     elif command == 'Посмотреть программу опеки':
#         logging.info(f"Пользователь {chat_id} запросил программу опеки.")
#         with open('Pig/programm.jpg', 'rb') as photo:
#             bot.sendPhoto(chat_id, photo=photo)
#         keyboard = ReplyKeyboardMarkup(
#             keyboard=[[KeyboardButton(text='Узнать свое тотемное животное')],
#                       [KeyboardButton(text='Вернуться в главное меню')]],
#             resize_keyboard=True
#         )
#         bot.sendMessage(chat_id, care_program_text, reply_markup=keyboard, parse_mode="Markdown")
#     # Ответ по умолчанию для нераспознанных команд
#     else:
#         logging.warning(f"Пользователь {chat_id} отправил нераспознанную команду: {command}")
# #         bot.sendMessage(chat_id, "Бот работает только с командами. Пожалуйста, используйте клавиши для взаимодействия.")