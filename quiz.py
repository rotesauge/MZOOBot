from sqlalchemy.sql import text
from models import *
import telebot


def create_keyboard(buttons):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    for button in buttons:
       keyboard.add(telebot.types.KeyboardButton(button))
    return keyboard

def get_result(db, quiz):
    Result = db.query(Results).filter(Results.pointsmax > quiz.curent_points).filter(Results.pointsmin < quiz.curent_points).first()
    if Result:
        return Result.title
    else:
        return 'Результата нет'

def next_question(chat_id,db,cond,quiz,bot,ans):
    uaID = get_cur_id(db,userAnswers)
    if ans:
        userAnswer = userAnswers(id          = uaID,
                                 id_question = cond.curent_question,
                                 id_answer   = ans.id,
                                 id_quiz     = quiz.id,
                                 TgUserId    = chat_id)
        db.add(userAnswer)
        quiz.curent_points += ans.points
    stmt = text("""
                SELECT 
	                q.id id,
	                q.title title
                from questions q 
                WHERE 
	                id not in (SELECT ua.id from user_answers ua)
	            limit 1    
                """)
    result = db.execute(stmt)
    first = result.first()
    if first:
       cond.curent_question = first[0]
       db.commit()
       kbd = create_keyboard([ans.title for ans in db.query(Answers).filter(Answers.id_question == first[0])])
       bot.send_message(chat_id, text = first[1], reply_markup=kbd)
    else:
       quiz.stoped = True
       cond.CurentCond = StatusEnum.START
       db.commit()
       kbd = create_keyboard(['пройти еще раз','вернуться в главное меню'])
       bot.send_message(chat_id, get_result(db, quiz), reply_markup=kbd)

def addquestion(chat_id,db):
    pass