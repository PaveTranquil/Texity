import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext

from logger import log

con = sqlite3.connect("players.db", check_same_thread=False)
cur = con.cursor()
list_of_players = [i[0] for i in cur.execute('SELECT tg_id FROM cities').fetchall()]

RESOURCES, MARKET, POPULATION, CONSTRUCTION, FOREIGN_POLICY, INFO, WAITING_FOR_SUMM, CHANGE_OR_GO_TO_MENU, NOT_ENOUGH_GOLD, BAD_SUMM, SUCCESSFUL_BUYING = range(
    2, 13)
WAITING_FOR_CITY_NAME, MENU = range(2)


@log
def get_info_about_city(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id
    if user_id in list_of_players:
        resources_1 = cur.execute('SELECT farms FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_2 = cur.execute('SELECT quarries FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_3 = cur.execute('SELECT sawmills FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_4 = cur.execute('SELECT iron_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        resources_5 = cur.execute('SELECT gold_mines FROM buildings WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        update.message.reply_text('Ваши предприятия\n'
                                  '🧑🏻‍🌾 Фермы: {}\n'
                                  '🪨 Каменоломни: {}\n'
                                  '🪵 Лесопилки: {}\n'
                                  '🏭 Железные рудники: {}\n'
                                  '💰 Золотые рудники: {}'.format(
            resources_1, resources_2, resources_3, resources_4, resources_5
        ), reply_markup=resources_markup)
    else:
        update.message.reply_text('Нет такого пользователя ¯\_(ツ)_/¯')
    return INFO


@log
def resources(update: Update, context: CallbackContext):
    resources_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    user_id = update.message.from_user.id
    if user_id in list_of_players:
        stone = cur.execute('SELECT stone FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        wood = cur.execute('SELECT wood FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        food = cur.execute('SELECT food FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        iron = cur.execute('SELECT iron FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        gold_ore = cur.execute('SELECT gold_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        iron_ore = cur.execute('SELECT iron_ore FROM resources WHERE tg_id = {}'.format(user_id)).fetchone()[0]
        update.message.reply_text('Ваши ресурсы\n'
                                  'Еда: {}\n'
                                  'Камни: {}\n'
                                  'Дерево: {}\n'
                                  'Железо: {}\n'
                                  'Золото: {}\n'
                                  'Золотая руда: {}\n'
                                  'Железная руда: {}'.format(food, stone, wood, iron, gold, gold_ore, iron_ore),
                                  reply_markup=resources_markup)
    else:
        update.message.reply_text('Нет такого пользователя ¯\_(ツ)_/¯')
    return RESOURCES


@log
def market(update: Update, context: CallbackContext):
    market_markup = ReplyKeyboardMarkup([['Еда', 'Дерево'],
                                         ['Камни', 'Железо'],
                                         ['Вернуться в меню']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Рынок", reply_markup=market_markup)
    return MARKET


def buy_food(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц еды')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUMM


def buy_wood(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 5 единиц еды')
    context.chat_data['material'] = 'wood'
    return WAITING_FOR_SUMM


def buy_stone(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 1 единицу камня')
    context.chat_data['material'] = 'stone'
    return WAITING_FOR_SUMM


def buy_iron(update: Update, context: CallbackContext):
    update.message.reply_text('За 1 единицу золота вы получите 1 единицу железа')
    context.chat_data['material'] = 'iron'
    return WAITING_FOR_SUMM


def check_summ(update: Update, context: CallbackContext):
    gold = cur.execute('SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0]
    markup_fail = ReplyKeyboardMarkup([['Попробовать еще раз'], ['Вернуться в меню']], one_time_keyboard=False,
                                      resize_keyboard=True)
    markup_success = ReplyKeyboardMarkup([['Продолжить покупки'], ['Вернуться в меню']], one_time_keyboard=False,
                                         resize_keyboard=True)
    summ = int(update.message.text)
    try:
        if summ > gold:
            update.message.reply_text('К сожалению, у вас недостаточно золота!', reply_markup=markup_fail)
            return CHANGE_OR_GO_TO_MENU
        elif summ <= 0:
            raise ValueError
        else:
            update.message.reply_text('Покупка прошла упешно!', reply_markup=markup_success)
            tranzaction(context.chat_data['material'], summ, update.message.from_user.id)
            print(cur.execute(
                'SELECT gold FROM resources WHERE tg_id = {}'.format(update.message.from_user.id)).fetchone()[0])
            return SUCCESSFUL_BUYING
    except ValueError:
        update.message.reply_text('Похоже, то что вы ввели, не выглядит как натуральное число.',
                                  reply_markup=markup_fail)
        return CHANGE_OR_GO_TO_MENU


def tranzaction(type_of_material, summ, user):
    print(user)
    cur.execute('UPDATE resources SET gold = (SELECT gold FROM resources WHERE tg_id = {}) - {}'.format(user, summ))
    con.commit()
    if type_of_material == 'food':
        cur.execute(
            'UPDATE resources SET food = (SELECT food FROM resources WHERE tg_id = {}) + 5 * {}'.format(user, summ))
    elif type_of_material == 'wood':
        cur.execute(
            'UPDATE resources SET wood = (SELECT wood FROM resources WHERE tg_id = {}) + 5 * {}'.format(user, summ))
    elif type_of_material == 'stone':
        cur.execute(
            'UPDATE resources SET stone = (SELECT stone FROM resources WHERE tg_id = {}) + {}'.format(user, summ))
    elif type_of_material == 'iron':
        cur.execute('UPDATE resources SET iron = (SELECT iron FROM resources WHERE tg_id = {}) + {}'.format(user, summ))
    con.commit()


@log
def population(update: Update, context: CallbackContext):
    population_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text("Ваше население", reply_markup=population_markup)
    return POPULATION


@log
def construction(update: Update, context: CallbackContext):
    construction_markup = ReplyKeyboardMarkup([['Ферма', 'Каменоломня', 'Лесопилка'],
                                               ['Железный рудник', 'Золотой рудник'],
                                               ['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Каких производств желаете построить?", reply_markup=construction_markup)
    return CONSTRUCTION


@log
def foreign_policy(update: Update, context: CallbackContext):
    foreign_policy_markup = ReplyKeyboardMarkup([['Вернуться в меню']], one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Внешняя политика", reply_markup=foreign_policy_markup)
    return FOREIGN_POLICY
