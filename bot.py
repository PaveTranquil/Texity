from datetime import datetime
from secrets import API_KEY

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from game import (BACK_TO_MENU, CHANGE_OR_GO_TO_MENU_ARMY,
                  CHANGE_OR_GO_TO_MENU_BUILDINGS, CHANGE_OR_GO_TO_MENU_MARKET,
                  CHANGE_OR_GO_TO_MENU_REMELTING, PRODUCTIONS, FOREIGN_POLICY,
                  HIRE_ARMY, HIRING, MARKET, MENU, POPULATION, RESOURCES,
                  SUCCESSFUL_BUILD, SUCCESSFUL_BUYING, SUCCESSFUL_HIRING,
                  SUCCESSFUL_REMELTING, WAITING_FOR_CITY_NAME,
                  WAITING_FOR_COUNT_OF_METAL, WAITING_FOR_COUNT_TO_BUILD,
                  WAITING_FOR_SUM_TO_BUY, WAITING_FOR_TYPE_OF_METAL, attack,
                  build_farms, build_gold_mines, build_iron_mines,
                  build_quarries, build_sawmills, build_sieges, buy_food,
                  buy_iron, buy_stone, buy_wood, check_build, check_buy,
                  check_hiring, check_remelt, con, chose_type_of_buildings, cultivating,
                  cur, foreign_policy, get_info_about_city,
                  get_info_about_opposite, hire_army, hire_cavalry,
                  hire_infantry, hire_spy, list_of_players, market,
                  path_to_city, population, remelt_gold, remelt_iron,
                  remelting, resources, scouting, WAITING_FOR_TYPE_OF_BUILDING, STORAGES, OTHERS,
                  build_productions, build_storages, build_others, build_storages_food, build_storages_wood,
                  build_storages_iron, build_storages_gold, build_storages_stone, build_storages_iron_ore, build_storages_gold_ore,
                  build_houses)
from helpfuncs import (HELP, about_city, about_constrution,
                       about_foreign_policy, about_market, about_population,
                       about_resources, help_)
from logger import log

img_city = open("city.jpg", 'rb')

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
            'Приветствуем тебя в Texity - пошаговой стратегии, в которой '
            'ты можешь развивать свой город, чтобы достичь светлого экономического '
            'будущего. Итак, введи имя своего города! ''',
        )

        return WAITING_FOR_CITY_NAME

    context.chat_data['city_name'] = cur.execute(
        'SELECT city FROM cities WHERE tg_id = {}'.format(user_id)).fetchone()[0]
    update.message.reply_photo(img_city,
                               "Вновь добро пожаловать в {}!".format(context.chat_data['city_name']),
                               reply_markup=markup)
    img_city.seek(0)
    return MENU


@log
def set_name(update: Update, context: CallbackContext) -> int:
    name, user_id = update.message.text, update.message.from_user.id
    update.message.reply_text(
        'Прекрасный выбор! Мы уверены, что ваш город с гордым именем {} ждут '
        'небывалые свершения. Удачи, император! ✊🏻\n Вы всегда можете отправить '
        'команду /help, чтобы получить подробную справку по управлению и механикам.'.format(name))

    cur.execute('INSERT INTO cities VALUES ({}, "{}", 0.5, 1, 2, 1, 0)'.format(user_id, name))
    cur.execute('INSERT INTO buildings VALUES ({}, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)'.format(user_id))
    cur.execute('INSERT INTO army VALUES ({}, 15, 5, 3)'.format(user_id))
    cur.execute('INSERT INTO resources VALUES ({}, 1000, '
                '1000, 1000, 1000, 1000, 1000, 1000, 1000, "{}")'.format(user_id,
                                                                         datetime.now().isoformat(sep=' ')))
    list_of_players.append(user_id)
    con.commit()
    context.chat_data['city_name'] = name

    update.message.reply_photo(img_city,
                               "Добро пожаловать в {}!".format(context.chat_data['city_name']),
                               reply_markup=markup)
    img_city.seek(0)
    return MENU


@log
def menu(update: Update, context: CallbackContext):
    update.message.reply_photo(img_city,
                               "Добро пожаловать в {}!".format(context.chat_data['city_name']),
                               reply_markup=markup)
    img_city.seek(0)
    return MENU


def run():
    updater = Updater(API_KEY)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(Filters.regex('^(Город)$'), get_info_about_city),
                   MessageHandler(Filters.regex('^(Ресурсы)$'), resources),
                   MessageHandler(Filters.regex('^(Рынок)$'), market),
                   MessageHandler(Filters.regex('^(Население)$'), population),
                   MessageHandler(Filters.regex('^(Строительство)$'), chose_type_of_buildings),
                   MessageHandler(Filters.regex('^(Внешняя политика)$'), foreign_policy),
                   CommandHandler('help', help_)],

            RESOURCES: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                        MessageHandler(Filters.regex('^(Собрать ресурсы)$'), cultivating),
                        MessageHandler(Filters.regex('^(Переплавить руду)$'), remelting),
                        CommandHandler('help', help_)],

            MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                     MessageHandler(Filters.regex('^(Еда)$'), buy_food),
                     MessageHandler(Filters.regex('^(Дерево)$'), buy_wood),
                     MessageHandler(Filters.regex('^(Камни)$'), buy_stone),
                     MessageHandler(Filters.regex('^(Железо)$'), buy_iron),
                     CommandHandler('help', help_)],

            POPULATION: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                         MessageHandler(Filters.regex('^(Нанять армию)$'), hire_army),
                         CommandHandler('help', help_)],

            PRODUCTIONS: [MessageHandler(Filters.regex('^(Лесопилка)$'), build_sawmills),
                          MessageHandler(Filters.regex('^(Ферма)$'), build_farms),
                          MessageHandler(Filters.regex('^(Каменоломня)$'), build_quarries),
                          MessageHandler(Filters.regex('^(Золотой рудник)$'), build_gold_mines),
                          MessageHandler(Filters.regex('^(Железный рудник)$'), build_iron_mines),
                          MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                           CommandHandler('help', help_)],

            FOREIGN_POLICY: [MessageHandler(Filters.regex('^(Расчистить путь к городу 🧭)$'), path_to_city),
                             MessageHandler(Filters.regex('^(На разведку! 🥷🏻)$'), scouting),
                             MessageHandler(Filters.regex('^(В атаку! ⚔️)$'), attack),
                             MessageHandler(Filters.regex('^(Информация о противнике ℹ️)$'), get_info_about_opposite),
                             MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                             CommandHandler('help', help_)],
            BACK_TO_MENU: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                           CommandHandler('help', help_)],

            WAITING_FOR_CITY_NAME: [MessageHandler(Filters.text, set_name)],
            WAITING_FOR_SUM_TO_BUY: [MessageHandler(Filters.text, check_buy)],
            WAITING_FOR_COUNT_TO_BUILD: [MessageHandler(Filters.text, check_build)],
            WAITING_FOR_TYPE_OF_METAL: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                        MessageHandler(Filters.regex('^(Железная руда)$'), remelt_iron),
                                        MessageHandler(Filters.regex('^(Золотая руда)$'), remelt_gold)],
            WAITING_FOR_COUNT_OF_METAL: [MessageHandler(Filters.text, check_remelt)],

            CHANGE_OR_GO_TO_MENU_MARKET: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                          MessageHandler(Filters.regex('^(Попробовать еще раз)$'), market),
                                          CommandHandler('help', help_)],
            CHANGE_OR_GO_TO_MENU_BUILDINGS: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                             MessageHandler(Filters.regex('^(Попробовать еще раз)$'), chose_type_of_buildings),
                                             CommandHandler('help', help_)],
            CHANGE_OR_GO_TO_MENU_REMELTING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                             MessageHandler(Filters.regex('^(Попробовать еще раз)$'), remelting),
                                             CommandHandler('help', help_)],
            CHANGE_OR_GO_TO_MENU_ARMY: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                        MessageHandler(Filters.regex('^(Попробовать еще раз)$'), hire_army),
                                        CommandHandler('help', help_)],

            SUCCESSFUL_BUYING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                MessageHandler(Filters.regex('^(Продолжить покупки)$'), market),
                                CommandHandler('help', help_)],
            SUCCESSFUL_BUILD: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                               MessageHandler(Filters.regex('^(Продолжить строительство)$'), chose_type_of_buildings),
                               CommandHandler('help', help_)],
            SUCCESSFUL_REMELTING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                   MessageHandler(Filters.regex('^(Продолжить переплавку)$'), remelting),
                                   CommandHandler('help', help_)],
            SUCCESSFUL_HIRING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                MessageHandler(Filters.regex('^(Нанять еще войска)$'), hire_army),
                                CommandHandler('help', help_)],

            HIRE_ARMY: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                        MessageHandler(Filters.regex('^(Нанять пехоту)$'), hire_infantry),
                        MessageHandler(Filters.regex('^(Нанять кавалерию)$'), hire_cavalry),
                        MessageHandler(Filters.regex('^(Нанять разведчиков)$'), hire_spy),
                        MessageHandler(Filters.regex('^(Построить осадные машины)$'), build_sieges),
                        CommandHandler('help', help_)],
            HIRING: [MessageHandler(Filters.text, check_hiring)],

            HELP: [MessageHandler(Filters.regex('^(Про рынок)$'), about_market),
                   MessageHandler(Filters.regex('^(Про город)$'), about_city),
                   MessageHandler(Filters.regex('^(Про ресурсы)$'), about_resources),
                   MessageHandler(Filters.regex('^(Про население)$'), about_population),
                   MessageHandler(Filters.regex('^(Про строительство)$'), about_constrution),
                   MessageHandler(Filters.regex('^(Про внешнюю политику)$'), about_foreign_policy),
                   MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu)],
            WAITING_FOR_TYPE_OF_BUILDING: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                                           MessageHandler(Filters.regex('^(Производства)$'), build_productions),
                                           MessageHandler(Filters.regex('^(Хранилища)$'), build_storages),
                                           MessageHandler(Filters.regex('^(Прочие строения)$'), build_others)],
            STORAGES: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                       MessageHandler(Filters.regex('^(Еда)$'), build_storages_food),
                       MessageHandler(Filters.regex('^(Дерево)$'), build_storages_wood),
                       MessageHandler(Filters.regex('^(Железо)$'), build_storages_iron),
                       MessageHandler(Filters.regex('^(Золото)$'), build_storages_gold),
                       MessageHandler(Filters.regex('^(Камни)$'), build_storages_stone),
                       MessageHandler(Filters.regex('^(Железная руда)$'), build_storages_iron_ore),
                       MessageHandler(Filters.regex('^(Золотая руда)$'), build_storages_gold_ore)],
            OTHERS: [MessageHandler(Filters.regex('^(Вернуться в меню)$'), menu),
                     MessageHandler(Filters.regex('^(Жилые здания)$'), build_houses)]

        },
        fallbacks=[CommandHandler('cancel', menu)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


run()
