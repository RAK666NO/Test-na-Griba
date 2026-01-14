import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Определяем этапы разговора
QUESTIONS = 1

# 20 вопросов про Clash Royale и правильные ответы (True = "Да", False = "Нет")
questions = [
    # 1-10: Вопросы про игровые привычки
    ("1. Вы всегда ставите Мегарыцаря на мост в начале матча?", False),  # Нет
    ("2. ТЫ СЧИТАЕШЬ СЕБЯ ГРИБОМ?", True),  # Да
    ("3. Вы считаете, что арбалет — это скилловая карта?", False),  # Нет
    ("4. Вы тратите весь эликсир в первые 10 секунд матча?", True),  # Да
    ("5. вы из Саратова?", True),  # Да
    ("6. Илья?", False),  # Нет
    ("7. 67?", False),  # Нет
    ("8. Самая плохая карта не считая элексирного голема это арбалет?", True),  # Да
    ("9. Вы спамите смайлики, когда проигрываете?", True),  # Да
    ("10. Вы считаете, что валькирия слабее Рыцаря?", False),  # Нет
    
    # 11-17: Вопросы про мета и карты
    ("11. Вы считаете, что Элексирный Голем — лучшая карта в игре?", False),  # Нет
    ("12. Вы верите, что 67 — это магическое число в Clash Royale?", True),  # Да
    ("13. Вы используете три легендарки в одной колоде?", True),  # Да
    ("14. Вы считаете, что Нарек — лучший игрок в мире?", False),  # Нет
    ("15. Вы ставите меганайта против пекки?", False),  # Нет
    ("16. Вы считаете, что Шахтер после нерфа стал лучше?", False),  # Нет
    ("17. Вы используете Бабиджон против толпы скелетов?", True),  # Да
    
    # 18-20: Вопросы про стратегию
    ("18. У вас есть муж Аноним?", True),  # Да
    ("19. Самый лучший ютубер по клеш роялю это Ванко?", True),  # Да
    ("20. Вы считаете, что лучшая тактика — это спам карт без раздумий?", False),  # Нет
]

# Клавиатура с вариантами ответов
reply_keyboard = [["Да", "Нет"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Инициализируем список ответов пользователя
    context.user_data['answers'] = []
    context.user_data['current_question'] = 0
    
    await update.message.reply_text(
        "🍄 Добро пожаловать в тест на грибность в Clash Royale! 🍄\n\n"
        "Ответь на 20 вопросов и узнай, насколько ты похож на гриба!\n"
        "Выбирай 'Да' или 'Нет' на каждый вопрос.\n\n"
        f"📋 Вопрос 1 из 20:\n{questions[0][0]}",
        reply_markup=markup
    )
    return QUESTIONS

# Обработка ответов на вопросы
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer_text = update.message.text
    
    # Проверяем валидность ответа
    if answer_text not in ["Да", "Нет"]:
        await update.message.reply_text("Пожалуйста, выбери 'Да' или 'Нет'.", reply_markup=markup)
        return QUESTIONS
    
    # Преобразуем ответ в булево значение
    user_answer = True if answer_text == "Да" else False
    
    # Сохраняем ответ пользователя
    context.user_data['answers'].append(user_answer)
    current_q = context.user_data['current_question']
    context.user_data['current_question'] += 1
    
    # Если вопросы еще остались, задаем следующий
    if current_q + 1 < len(questions):
        question_num = current_q + 2  # +2 потому что индексы начинаются с 0
        await update.message.reply_text(
            f"📋 Вопрос {question_num} из 20:\n{questions[current_q + 1][0]}",
            reply_markup=markup
        )
        return QUESTIONS
    else:
        # Все вопросы заданы, подсчитываем результат
        total_questions = len(questions)
        
        # Подсчитываем "грибные" ответы
        # Грибные ответы: True для вопросов 2,4,5,8,9,12,13,17,18,19
        # И False для вопросов 1,3,6,7,10,11,14,15,16,20
        mushroom_score = 0
        
        # Вопросы где "Да" - грибной ответ (индексы: 1,3,4,7,8,11,12,16,17,18)
        mushroom_yes_questions = [1, 3, 4, 7, 8, 11, 12, 16, 17, 18]
        # Вопросы где "Нет" - грибной ответ (индексы: 0,2,5,6,9,10,13,14,15,19)
        mushroom_no_questions = [0, 2, 5, 6, 9, 10, 13, 14, 15, 19]
        
        for i in range(total_questions):
            user_ans = context.user_data['answers'][i]
            if i in mushroom_yes_questions and user_ans == True:
                mushroom_score += 1
            elif i in mushroom_no_questions and user_ans == False:
                mushroom_score += 1
        
        percentage = (mushroom_score / total_questions) * 100
        
        # Определяем уровень грибности
        if percentage >= 90:
            level = "🏆 <БАТЮШКА ВСЕХ ГРИБОВ! 🍄👑"
            description = "Ты легенда среди грибов! Твои решения настолько грибные, что их изучают в академиях!"
        elif percentage >= 80:
            level = "💎 ЧЕМПИОНСКИЙ ГРИБ! 🍄💎"
            description = "Ты — образец для подражания всех грибов! Твоя игра — это искусство грибности!"
        elif percentage >= 70:
            level = "⭐ ЭЛИТНЫЙ ГРИБ! 🍄⭐"
            description = "Ты продвинутый гриб! Понимаешь все тонкости грибной тактики!"
        elif percentage >= 60:
            level = "⚔️ ВОИН ГРИБ! 🍄⚔️"
            description = "Ты уверенный гриб! Знаешь, как правильно делать неоптимальные ходы!"
        elif percentage >= 50:
            level = "🛡️ РЫЦАРЬ ГРИБ! 🍄🛡️"
            description = "Ты надежный гриб! Стабильно делаешь странные выборы в игре!"
        elif percentage >= 40:
            level = "🎯 ОПЫТНЫЙ НЕ-ГРИБ 🍄➡️👤"
            description = "Ты на пути исправления! Еще есть грибные замашки, но ты учишься!"
        elif percentage >= 30:
            level = "🚀 НАЧИНАЮЩИЙ ПРО-ИГРОК 👤✨"
            description = "Ты почти не гриб! Понимаешь основы игры и делаешь разумные ходы!"
        elif percentage >= 20:
            level = "👑 МАСТЕР ТАКТИКИ 👑🎮"
            description = "Ты определенно не гриб! Твои решения продуманы и эффективны!"
        else:
            level = "🤖 КИБЕРСПОРТСМЕН 🤖🏆"
            description = "Ты абсолютно не гриб! Возможно, ты даже участвуешь в турнирах!"
        
        # Подсчитываем правильные ответы с точки зрения оптимальной игры
        correct_answers = 0
        for i in range(total_questions):
            if context.user_data['answers'][i] == questions[i][1]:
                correct_answers += 1
        
        optimal_percentage = (correct_answers / total_questions) * 100
        
        await update.message.reply_text(
            f"🎮 ТЕСТ ЗАВЕРШЕН! 🎮\n\n"
            f"📊 ТВОИ РЕЗУЛЬТАТЫ:\n"
            f"🍄 Уровень грибности: {percentage:.1f}%\n"
            f"✅ Оптимальные ответы: {correct_answers} из {total_questions} ({optimal_percentage:.1f}%)\n\n"
            f"🏅 ТВОЙ ТИТУЛ: {level}\n"
            f"📝 {description}\n\n"
            f"💡 Совет: {'Продолжай в том же духе, король грибов! 🍄👑' if percentage >= 50 else 'Ты на правильном пути к мастерству! 🚀'}\n\n"
            f"Если хочешь пройти тест заново, напиши /start",
            reply_markup=markup
        )
        
        # Очищаем данные пользователя
        context.user_data.clear()
        return ConversationHandler.END

# Команда /cancel для отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Тест отменен. Если захочешь узнать свою грибность, напиши /start",
        reply_markup=markup
    )
    context.user_data.clear()
    return ConversationHandler.END

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🎮 Clash Royale Гриб-Тест 🍄\n\n"
        "🤖 Доступные команды:\n"
        "/start - начать тест на грибность (20 вопросов)\n"
        "/help - показать это сообщение\n"
        "/cancel - отменить текущий тест\n\n"
        "📝 О тесте:\n"
        "• 20 вопросов о твоих игровых привычках\n"
        "• Ответы: Да или Нет\n"
        "• Результат: процент твоей 'грибности'\n"
        "• Титул в зависимости от результата\n\n"
        "🍄 Что такое 'гриб'?\n"
        "Гриб — игрок, который делает неоптимальные ходы,\n"
        "верит в стереотипы и играет на эмоциях, а не тактике!"
    )

# Команда /stats - показывает общую статистику
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📈 Статистика гриб-теста:\n\n"
        "🍄 Всего вопросов: 20\n"
        "📊 Категории вопросов:\n"
        "• Игровые привычки: 10 вопросов\n"
        "• Мета и карты: 7 вопросов\n"
        "• Стратегия: 3 вопроса\n\n"
        "🎯 Критерии грибности:\n"
        "• 90-100%: Корпоральный Гриб 👑\n"
        "• 80-89%: Чемпионский Гриб 💎\n"
        "• 70-79%: Элитный Гриб ⭐\n"
        "• 60-69%: Воин Гриб ⚔️\n"
        "• 50-59%: Рыцарь Гриб 🛡️\n"
        "• 40-49%: Опытный не-гриб 🎯\n"
        "• 30-39%: Начинающий про-игрок 🚀\n"
        "• 20-29%: Мастер тактики 👑\n"
        "• 0-19%: Киберспортсмен 🤖"
    )

def main() -> None:
    # Ваш токен бота
    TOKEN = "8532136154:AAGGaIpJQo4lhNSoaPv-uNyzPHw0lMa52jI"
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Создаем обработчик разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Добавляем обработчики команд
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()