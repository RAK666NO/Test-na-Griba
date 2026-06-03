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

# Клавиатура с вариантами ответов на вопросы
reply_keyboard = [["Да", "Нет", "Пропустить"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Клавиатура для завершения теста или перезапуска
restart_keyboard = [["Начать тест заново", "Завершить тест"]]
restart_markup = ReplyKeyboardMarkup(restart_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Инициализируем список ответов пользователя
    context.user_data['answers'] = []
    context.user_data['current_question'] = 0
    context.user_data['skipped_questions'] = []  # Для отслеживания пропущенных вопросов
    
    await update.message.reply_text(
        "🍄 Добро пожаловать в тест на грибность в Clash Royale! 🍄\n\n"
        "Ответь на 20 вопросов и узнай, насколько ты похож на гриба!\n"
        "Выбирай 'Да' или 'Нет' на каждый вопрос.\n"
        "💡 Можно пропустить вопрос, выбрав 'Пропустить'\n\n"
        f"📋 Вопрос 1 из 20:\n{questions[0][0]}",
        reply_markup=markup
    )
    return QUESTIONS

# Обработка ответов на вопросы
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer_text = update.message.text
    
    # Обработка команды "Начать тест заново"
    if answer_text == "Начать тест заново":
        await update.message.reply_text(
            "🔄 Начинаем тест заново!\n\n"
            f"📋 Вопрос 1 из 20:\n{questions[0][0]}",
            reply_markup=markup
        )
        context.user_data['answers'] = []
        context.user_data['current_question'] = 0
        context.user_data['skipped_questions'] = []
        return QUESTIONS
    
    # Обработка команды "Завершить тест"
    if answer_text == "Завершить тест":
        await update.message.reply_text(
            "Тест завершен досрочно. Если захочешь узнать свою грибность, напиши /start",
            reply_markup=ReplyKeyboardMarkup([["/start"]], resize_keyboard=True)
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # Получаем текущий вопрос
    current_q = context.user_data['current_question']
    
    # Если текущий вопрос уже последний и пользователь отвечает на него
    if current_q >= len(questions):
        # Это означает, что мы уже закончили тест и показываем результаты
        # Обрабатываем повторный запуск
        if answer_text == "Да":
            await update.message.reply_text(
                "🔄 Начинаем тест заново!\n\n"
                f"📋 Вопрос 1 из 20:\n{questions[0][0]}",
                reply_markup=markup
            )
            context.user_data['answers'] = []
            context.user_data['current_question'] = 0
            context.user_data['skipped_questions'] = []
            return QUESTIONS
        elif answer_text == "Нет":
            await update.message.reply_text(
                "Спасибо за прохождение теста! Чтобы начать заново, используйте /start",
                reply_markup=ReplyKeyboardMarkup([["/start"]], resize_keyboard=True)
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("Пожалуйста, выбери 'Да' или 'Нет'.")
            return QUESTIONS
    
    # Проверяем валидность ответа на вопрос
    if answer_text not in ["Да", "Нет", "Пропустить"]:
        await update.message.reply_text("Пожалуйста, выбери 'Да', 'Нет' или 'Пропустить'.", reply_markup=markup)
        return QUESTIONS
    
    # Обработка пропуска вопроса
    if answer_text == "Пропустить":
        context.user_data['skipped_questions'].append(current_q)
        context.user_data['answers'].append(None)  # None означает пропущенный вопрос
    else:
        # Преобразуем ответ в булево значение
        user_answer = True if answer_text == "Да" else False
        # Сохраняем ответ пользователя
        context.user_data['answers'].append(user_answer)
    
    # Переходим к следующему вопросу
    context.user_data['current_question'] += 1
    
    # Если вопросы еще остались, задаем следующий
    if context.user_data['current_question'] < len(questions):
        next_q = context.user_data['current_question']
        question_num = next_q + 1  # +1 потому что индексы начинаются с 0
        await update.message.reply_text(
            f"📋 Вопрос {question_num} из 20:\n{questions[next_q][0]}",
            reply_markup=markup
        )
        return QUESTIONS
    else:
        # Все вопросы заданы, подсчитываем результат
        await show_results(update, context)
        return ConversationHandler.END

# Функция показа результатов
async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_questions = len(questions)
    
    # Подсчитываем "грибные" ответы
    mushroom_score = 0
    answered_questions = 0
    
    # Вопросы где "Да" - грибной ответ (индексы: 1,3,4,7,8,11,12,16,17,18)
    mushroom_yes_questions = [1, 3, 4, 7, 8, 11, 12, 16, 17, 18]
    # Вопросы где "Нет" - грибной ответ (индексы: 0,2,5,6,9,10,13,14,15,19)
    mushroom_no_questions = [0, 2, 5, 6, 9, 10, 13, 14, 15, 19]
    
    # Подсчитываем правильные ответы с точки зрения оптимальной игры
    correct_answers = 0
    
    for i in range(total_questions):
        user_ans = context.user_data['answers'][i]
        
        # Пропущенные вопросы не учитываем в статистике
        if user_ans is None:
            continue
            
        answered_questions += 1
        
        # Проверяем грибность
        if i in mushroom_yes_questions and user_ans == True:
            mushroom_score += 1
        elif i in mushroom_no_questions and user_ans == False:
            mushroom_score += 1
        
        # Проверяем правильность ответа с точки зрения оптимальной игры
        if user_ans == questions[i][1]:
            correct_answers += 1
    
    # Рассчитываем проценты
    if answered_questions > 0:
        percentage = (mushroom_score / answered_questions) * 100
        optimal_percentage = (correct_answers / answered_questions) * 100
    else:
        percentage = 0
        optimal_percentage = 0
    
    # Определяем уровень грибности
    if percentage >= 90:
        level = "🏆 БАТЮШКА ВСЕХ ГРИБОВ! 🍄👑"
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
    
    skipped_count = len(context.user_data['skipped_questions'])
    
    result_message = f"🎮 ТЕСТ ЗАВЕРШЕН! 🎮\n\n"
    result_message += f"📊 ТВОИ РЕЗУЛЬТАТЫ:\n"
    result_message += f"✅ Отвечено вопросов: {answered_questions} из {total_questions}\n"
    
    if skipped_count > 0:
        result_message += f"⏭️ Пропущено вопросов: {skipped_count}\n"
    
    result_message += f"🍄 Уровень грибности: {percentage:.1f}%\n"
    result_message += f"🎯 Оптимальные ответы: {correct_answers} из {answered_questions} ({optimal_percentage:.1f}%)\n\n"
    result_message += f"🏅 ТВОЙ ТИТУЛ: {level}\n"
    result_message += f"📝 {description}\n\n"
    
    if percentage >= 50:
        result_message += f"💡 Совет: Продолжай в том же духе, король грибов! 🍄👑\n\n"
    else:
        result_message += f"💡 Совет: Ты на правильном пути к мастерству! 🚀\n\n"
    
    result_message += f"Хочешь пройти тест заново?"
    
    # Создаем клавиатуру для выбора действий после теста
    after_test_keyboard = [["Да", "Нет"]]
    after_test_markup = ReplyKeyboardMarkup(after_test_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        result_message,
        reply_markup=after_test_markup
    )

# Команда /cancel для отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Тест отменен. Если захочешь узнать свою грибность, напиши /start",
        reply_markup=ReplyKeyboardMarkup([["/start"]], resize_keyboard=True)
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
        "/cancel - отменить текущий тест\n"
        "/stats - показать статистику теста\n\n"
        "📝 О тесте:\n"
        "• 20 вопросов о твоих игровых привычках\n"
        "• Ответы: Да, Нет или Пропустить\n"
        "• Можно начать тест заново в процессе\n"
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
        "• 90-100%: Батюшка всех грибов 👑\n"
        "• 80-89%: Чемпионский Гриб 💎\n"
        "• 70-79%: Элитный Гриб ⭐\n"
        "• 60-69%: Воин Гриб ⚔️\n"
        "• 50-59%: Рыцарь Гриб 🛡️\n"
        "• 40-49%: Опытный не-гриб 🎯\n"
        "• 30-39%: Начинающий про-игрок 🚀\n"
        "• 20-29%: Мастер тактики 👑\n"
        "• 0-19%: Киберспортсмен 🤖\n\n"
        "⚡ Особенности теста:\n"
        "• Можно пропускать вопросы\n"
        "• Можно начать тест заново\n"
        "• Результат учитывает только отвеченные вопросы"
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
