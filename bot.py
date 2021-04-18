from secrets import API_KEY

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from game import (CONSTRUCTION, FOREIGN_POLICY, MARKET, POPULATION, RESOURCES, INFO, WAITING_FOR_SUMM, CHANGE_OR_GO_TO_MENU, WAITING_FOR_CITY_NAME, MENU, SUCCESSFUL_BUYING, SUCCESSFUL_BUILD, WAITING_FOR_COUNT_TO_BUILD,
                  con, construction, cur, foreign_policy, list_of_players,
                  market, population, resources, get_info_about_city, buy_food, buy_wood, buy_iron, buy_stone, check_summ,
                  build_farms, build_quarries, build_sawmills, build_gold_mines, build_iron_mines, check_build, tranzaction_build)
from logger import log

markup = ReplyKeyboardMarkup([['Город'],
                              ['Ресурсы', 'Рынок'],
                              ['Население', 'Строительство'],
                              ['Внешняя политика']],
                             one_time_keyboard=False, resize_keyboard=True)



@log
def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id not in list_of_players:
        update.message.reply_text(
            '''
Приветствуем тебя в Texity - пошаговой стратегии, в которой ты можешь развивать свой город, чтобы достичь светлого экономического будущего.

Итак, введи имя своего города! ''',
        )

        return WAITING_FOR_CITY_NAME

    context.chat_data['city_name'] = cur.execute(
        'SELECT city FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    update.message.reply_text("Вновь добро пожаловать в {}!".format(
        context.chat_data['city_name']), reply_markup=markup)
    return MENU


@log
def set_name(update: Update, context: CallbackContext) -> int:
    name, user_id = update.message.text, update.message.from_user.id
    update.message.reply_text('''
Прекрасный выбор! Мы уверены, что ваш город с гордым именем {} ждут небывалые свершения.
Удачи, император! ✊🏻
Вы всегда можете отправить команду /help, чтобы получить подробную справку по управлению и механикам.
    '''.format(name),
    )
    
    cur.execute('''INSERT INTO cities VALUES ({}, "{}")'''.format(user_id, name))
    cur.execute('''INSERT INTO buildings VALUES ({}, 1, 1, 1, 1, 1)'''.format(user_id))
    cur.execute('''INSERT INTO resources VALUES ({}, 1000, 1000, 1000, 1000, 1000)'''.format(user_id))
    list_of_players.append(user_id)
    con.commit()
    context.chat_data['city_name'] = name

    update.message.reply_text("Добро пожаловать в {}!".format(context.chat_data['city_name']), reply_markup=markup)
    return MENU


@log
def help(update: Update, context: CallbackContext) -> int:
    # todo: Вызввать админов или порешать, как должен работать /help
    update.message.reply_text(
        'Мир суров. Поэтому рабирайся сам.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


@log
def menu(update: Update, context: CallbackContext):
    update.message.reply_text("Добро пожаловать в {}!".format(context.chat_data['city_name']), reply_markup=markup)
    return MENU



def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_CITY_NAME: [MessageHandler(Filters.text, set_name)],
            MENU: [MessageHandler(Filters.regex('^(Город)$'), get_info_about_city),
                   MessageHandler(Filters.regex('^(Ресурсы)$'), resources),
                   MessageHandler(Filters.regex('^(Рынок)$'), market),
                   MessageHandler(Filters.regex('^(Население)$'), population),
                   MessageHandler(Filters.regex('^(Строительство)$'), construction),
                   MessageHandler(Filters.regex('^(Внешняя политика)$'), foreign_policy)],
            RESOURCES: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                     MessageHandler(Filters.regex('^(Еда)$'), buy_food),
                     MessageHandler(Filters.regex('^(Дерево)$'), buy_wood),
                     MessageHandler(Filters.regex('^(Камни)$'), buy_stone),
                     MessageHandler(Filters.regex('^(Железо)$'), buy_iron),
                     ],
            POPULATION: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            CONSTRUCTION: [MessageHandler(Filters.regex('^(Лесопилка)$'), build_sawmills),
                           MessageHandler(Filters.regex('^(Ферма)$'), build_farms),
                           MessageHandler(Filters.regex('^(Каменоломня)$'), build_quarries),
                           MessageHandler(Filters.regex('^(Золотой рудник)$'), build_gold_mines),
                           MessageHandler(Filters.regex('^(Железный рудник)$'), build_iron_mines),
                           MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)
                           ],
            FOREIGN_POLICY: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            INFO: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            WAITING_FOR_SUMM: [MessageHandler(Filters.text, check_summ)],
            WAITING_FOR_COUNT_TO_BUILD: [MessageHandler(Filters.text, check_build)],
            CHANGE_OR_GO_TO_MENU_MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                              MessageHandler(Filters.regex('^(Попробовать еще раз)$'), market)],
            SUCCESSFUL_BUYING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                              MessageHandler(Filters.regex('^(Продолжить покупки)$'), market)],
            SUCCESSFUL_BUILD: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                MessageHandler(Filters.regex('^(Продолжить строительство)$'), construction)]

        },
        fallbacks=[CommandHandler('cancel', menu)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

run()