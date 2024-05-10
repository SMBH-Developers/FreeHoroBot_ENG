import asyncio
import random
import logging
import re

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.utils import markdown
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from loguru import logger
from zodiac_sign import get_zodiac_sign
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import Markups
from bf_texts import bf_sending, SendingData
from texts import random_texts_year, study_menu_texts, welcome_text, to_connect, start_texts, study_text, astro_advices
from src.common import settings
from src.models import db, db_sendings

from data.skip_100_lead import skip_100_leads


class States(StatesGroup):
    get_user_date_for_horoscope_year = State()
    back_state = State()


storage = RedisStorage2(db=settings.redis_db, pool_size=40)
bot = Bot(settings.tg_token)
dp = Dispatcher(bot, storage=storage)
ADMIN_IDS = (1188441997, 791363343)
markups = Markups()

available_codes = list(range(15908, 531284))  # Коды для генерации заявки при окончании получения разбора гороскопа
horoscopes_padejs = {'Aries': 'Aries', 'Taurus': 'Taurus', 'Gemini': 'Gemini', 'Cancer': 'Cancer',
                     'Leo': 'Leo', 'Virgo': 'Virgo', 'Libra': 'Libra', 'Scorpio': 'Scorpio',
                     'Sagittarius': 'Sagittarius', 'Capricorn': 'Capricorn', 'Aquarius': 'Aquarius', 'Pisces': 'Pisces'}
language = 'en_US'

astro_advice_photo = "AgACAgIAAxkBAALh-GTb8V2CjeboPMbxCqT_X_RF0xuXAAJa0jEb1fvhSqtfMMzRcXDlAQADAgADeQADMAQ"
astrology_is_photo = "AgACAgIAAxkBAALh-WTb8XC7Kgec83nd-cBmaeAKBvQdAAJc0jEb1fvhSqFeL9QHtyBIAQADAgADeQADMAQ"
lune_horoscope_photo = "AgACAgIAAxkBAALh-mTb8X2CG2p51lcOPHSET0LG8zEKAAI2yzEbEB7gSuc24irJBkw_AQADAgADeQADMAQ"
#types.InputFile('data/photos/year_horoscope.JPG') = "AgACAgIAAxkBAALh-2Tb8Yi05TG0ZUHqoyjfbLjwOHKzAAJe0jEb1fvhSiVBtqT4X0zYAQADAgADeQADMAQ"
BF_PEOPLE = [791363343, 923202245, 1633990660, 1188441997, 627568042]


def get_value_of_arg(arg: str) -> str:
    """Получает значение из аргумент=значение"""
    return arg.split('=')[-1]


def generate_apply_code():
    code = ''.join(map(lambda num: str(num), [random.choice((4, 5, 6, 7, 8, 9)) for _ in range(6)]))
    return code


@dp.message_handler(lambda message: message.from_user.id == 1188441997, content_types=['photo'], state='*')
async def get_photo_from_me(message: types.Message, state: FSMContext):
    print(message.photo[-1].file_id)


@dp.message_handler(lambda message: message.from_user.id == 1188441997, content_types=['document'], state='*')
async def get_photo_from_me(message: types.Message, state: FSMContext):
    print(message.document.file_id)


@dp.message_handler(commands=['start'], state='*')
@logger.catch
async def start_mes(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    await message.answer_photo(types.InputFile('data/photos/lune_horoscope_2.png'), welcome_text, reply_markup=markups.start_mrkup, parse_mode='html')
    await db.registrate_if_not_exists(message.from_user.id)


@dp.message_handler(lambda message: message.from_user.id in BF_PEOPLE, commands=['bf_stat'], state='*')
async def get_bf_stat(message: types.Message):
    stat = await db_sendings.get_bf_stat()
    await message.answer(stat)


@dp.callback_query_handler(lambda call: call.data == 'delete_msg', state='*')
async def del_msg(call: types.CallbackQuery, state: FSMContext):
    """
    Deletes the message as garbage
    """
    try:
        await call.message.delete()
    except exceptions.MessageCantBeDeleted:
        await call.message.delete_reply_markup()
        await call.answer('Unable to delete message')


@dp.message_handler(lambda message: message.text == '👈Обратно', state="*")
@logger.catch
async def back_from_getting_horoscope_year(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer_photo(types.InputFile('data/photos/lune_horoscope_2.png'), welcome_text, reply_markup=markups.start_mrkup, parse_mode='html')


@dp.message_handler(lambda message: message.text == '👈Back', state='*')
@logger.catch
async def back_from_get_user_date_guide(message: types.Message, state: FSMContext):
    await message.answer(study_text, reply_markup=markups.study_mrkup)


@dp.message_handler(lambda message: message.text == '✨Get a horoscope for 2024', state='*')
@logger.catch
async def get_horoscope_on_2023_year(message: types.Message, state: FSMContext):
    user_date = await db.check_if_user_has_birth_date(message.from_user.id)
    if not bool(user_date):
        await bot.send_message(message.chat.id,
                               text='🙏To receive a horoscope for the year, please write your date of birth in the form dd.mm.yyyy',
                               reply_markup=markups.to_menu_mrkup, parse_mode='html')
        await state.set_state(States.get_user_date_for_horoscope_year.state)
    else:
        day, month = user_date.split('.')[:2]
        zodiac = get_zodiac_sign(day, month, language='en_US')
        user_choose = await db.get_horoscope_text_index(message.from_user.id)
        await bot.send_message(message.chat.id, text=generate_beautiful_text('year', zodiac, user_date, user_choose),
                               reply_markup=markups.to_menu_mrkup,
                               parse_mode='html')
        await state.set_state(States.back_state.state)
        asyncio.create_task(send_text_with_inline_btn(message.chat.id))


@dp.message_handler(lambda message: message.text in start_texts, state='*')
@logger.catch
async def which_horoscope(message: types.Message, state) -> None:
    if message.text == '✨Get a horoscope':
        user_date = await db.check_if_user_has_birth_date(message.from_user.id)
        if not bool(user_date):
            await bot.send_message(message.chat.id,
                                   text='🙏To receive a horoscope for the year, please write your date of birth in the form dd.mm.yyyy',
                                   reply_markup=markups.to_menu_mrkup, parse_mode='html')
            await state.set_state(States.get_user_date_for_horoscope_year.state)
        else:
            day, month = user_date.split('.')[:2]
            zodiac = get_zodiac_sign(day, month, language='en_US')
            user_choose = await db.get_horoscope_text_index(message.from_user.id)
            await message.answer_photo(types.InputFile('data/photos/year_horoscope_2.png'),
                                       caption=generate_beautiful_text('year', zodiac, user_date, user_choose),
                                       reply_markup=markups.to_menu_mrkup,
                                       parse_mode='html')
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_text_with_inline_btn(message.chat.id))

    elif message.text == '📜Educational Menu':
        await message.answer(study_text, reply_markup=markups.study_mrkup)


async def generate_astro_advice(user_id):
    start_of_text = '✨Astrological advice for the day:'
    advice = astro_advices[await db.get_user_advice_step(user_id)]
    now_time = datetime.now()
    tomorrow_time = (now_time + timedelta(days=1))
    necessary_time = datetime(year=tomorrow_time.year, month=tomorrow_time.month, day=tomorrow_time.day, hour=0,
                              minute=0, second=0)
    left_time_for_update = round(((necessary_time - now_time).total_seconds() / 60 / 60), 1)
    end_of_text = f"❤️There are {left_time_for_update}hours left until the new astrological advice appears."
    main_text = f'{start_of_text}\n\n{advice}\n\n{end_of_text}'
    return main_text


@dp.message_handler(lambda message: message.text in study_menu_texts or message.text in ('🙏Get a personalized horoscope', '✨Get a horoscope for the year', '✨Astrological advice of the day'), state='*' )
async def study_menu_dispatcher(message: types.Message, state: FSMContext):
    if message.text in ('🙏Get a personalized horoscope', '✨Get a horoscope for the year'):
        user_date = await db.check_if_user_has_birth_date(message.from_user.id)
        if not bool(user_date):
            await bot.send_message(message.chat.id,
                                   text='🙏To receive a horoscope for the year, please write your date of birth in the form dd.mm.yyyy',
                                   reply_markup=markups.to_menu_mrkup, parse_mode='html')
            await state.set_state(States.get_user_date_for_horoscope_year.state)
        else:
            day, month = user_date.split('.')[:2]
            zodiac = get_zodiac_sign(day, month, language='en_US')
            user_choose = await db.get_horoscope_text_index(message.from_user.id)
            await message.answer_photo(photo=types.InputFile('data/photos/year_horoscope_2.png'),
                                       caption=generate_beautiful_text('year', zodiac, user_date, user_choose),
                                       reply_markup=markups.to_menu_mrkup,
                                       parse_mode='html')
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_text_with_inline_btn(message.chat.id))

    elif message.text == '✨Astrological advice of the day':
        text = await generate_astro_advice(message.from_user.id)
        await message.answer_photo(types.InputFile('data/photos/astro_advice.JPG'), text, reply_markup=markups.mrkup_for_every_study_btn)
    elif message.text == '✨What is astrology?':
        await message.answer_photo(types.InputFile('data/photos/astrology_is.JPG'), study_menu_texts[message.text],
                                   reply_markup=markups.mrkup_for_every_study_btn)
    else:
        text = study_menu_texts[message.text]
        await message.answer(text, reply_markup=markups.mrkup_for_every_study_btn)


@dp.message_handler(lambda message: message.from_user.id in ADMIN_IDS, state='*', commands=['admin'])
@logger.catch
async def admin_menu(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(message.chat.id, text='Выберите действие', reply_markup=markups.admin_mrkup)


@dp.callback_query_handler(lambda call: call.from_user.id in ADMIN_IDS and call.data.startswith('Admin'), state='*')
@logger.catch
async def admin_calls(call: types.CallbackQuery, state: FSMContext) -> None:
    action = '_'.join(call.data.split('_')[1:])
    if action == 'Users_Total':
        await call.message.edit_text(text=f'Пользователей всего: {await db.get_count_all_users()}',
                                     reply_markup=markups.back_admin_mrkup)

    elif action == 'Users_For_TODAY':
        await call.message.edit_text(text=f'Пользователей за сегодня: {await db.users_for_today()}',
                                     reply_markup=markups.back_admin_mrkup)

    elif action == 'BACK':
        await call.message.edit_text(text='Выберите действие', reply_markup=markups.admin_mrkup)


def generate_beautiful_text(horoscope_type, zodiac, user_date, user_choose):
    main_text = '⭐️Horoscope for '
    main_text += '2024'
    horoscope_text = random_texts_year[user_choose]
    main_text += f' for {markdown.hbold(horoscopes_padejs[zodiac])} | Date of birth: {markdown.hbold(user_date)}\n\n{horoscope_text}' + to_connect
    return main_text


async def send_analyze_of_answers(chat_id, text_to_send):
    await asyncio.sleep(7)
    await bot.send_photo(chat_id, photo=types.InputFile('data/photos/year_horoscope_2.png'), caption=text_to_send, parse_mode='html')
    asyncio.create_task(send_text_with_inline_btn(chat_id))


async def send_text_with_inline_btn(chat_id):
    apply_code = await db.get_apply_code(chat_id)
    if apply_code is None:
        apply_code = generate_apply_code()
        await db.set_apply_code(chat_id, str(apply_code))
    await asyncio.sleep(2) #12106
    text = "🔆 Only today, certified astrologer Briana will prepare a personal horoscope for you covering all areas of life: destiny, money, realization, relationships.\n\n📎 Your application's code number: 759845\n\nPlease send astrologer Briana the code number of your application and the place of birth to the personal account - @Your_soul_assistant👈\n\n❗️There are 15 spots left for analysis until the end of the month"
    await bot.send_message(chat_id, text, parse_mode='html',
                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(
                               text='Write to an astrologer', url=f'https://t.me/Your_soul_assistant')]]))

@dp.message_handler(state=States.get_user_date_for_horoscope_year)
@logger.catch
async def choose_zodiac_year(message: types.Message, state: FSMContext) -> None:
    if re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{4}', message.text):
        day, month, year = message.text.split('.')
        if 0 < int(day) < 32 and 0 < int(month) < 13 and int(year) < 2023:
            await db.update_user_birth_date(message.from_user.id, message.text)
            zodiac = get_zodiac_sign(day, month, language='en_US')
            user_choose_year = random.choice(range(3, len(random_texts_year)))
            await db.set_horoscope_text_index(message.from_user.id, user_choose_year)
            await message.answer('  Processing information...', reply_markup=markups.to_menu_mrkup)
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_analyze_of_answers(message.chat.id,
                                                        generate_beautiful_text('year', zodiac, message.text,
                                                                                user_choose_year)))
        else:
            await message.answer('Invalid date!\n'
                                 '🙏To receive a horoscope for the year, please write your date of birth in the form dd.mm.yyyy',
                                 reply_markup=markups.to_menu_mrkup)
    else:
        await message.answer('Invalid format.\n'
                             '🙏To receive a horoscope for the year, please write your date of birth in the form dd.mm.yyyy',
                             reply_markup=markups.to_menu_mrkup)


async def sending_messages_2h():
    while True:
        await asyncio.sleep(7)

        text_for_2h_autosending = "🙌 My dear, I hasten to inform you that there are only 6 spots left for creating a personal horoscope for the current year.\n\nDo not miss your chance to find out what awaits you, write the word 'Happiness' to astrologer Briana in private messages - @Your_soul_assistant👈\n\n🧚 With the help of a personal horoscope, we can identify current life problems in all areas and find the right paths to solve them."
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("Let happiness in ✨", url="https://t.me/Your_soul_assistant"))

        users = await db_sendings.get_users_2h_autosending()
        for user in users:
            try:
                await bot.send_message(user, text_for_2h_autosending, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got 2h_autosending')
                await db_sendings.mark_got_2h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_24_h():
    while True:
        await asyncio.sleep(12)

        text_autosending_24h = "🌖Hello, today the Moon is in the most favorable phase, during which the most accurate individual astrological analysis can be made based on the natal chart. In honor of this event, astrologer Vera will prepare an analysis for you and share practices for correcting your destiny.\n\n🧘‍♀️ In it, you will learn about the path recommended by the stars, how to solve current life problems, and avoid further misfortunes in your life journey. To receive it, please send your date and place of birth in private messages - @YouAstro_bot👈"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("🔆Astrological analysis", url="https://t.me/Your_soul_assistant"))

        users = await db_sendings.get_users_24h_autosending()
        for user in users:
            try:
                await bot.send_message(user, text_autosending_24h, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got autosending_24h')
                await db_sendings.mark_got_24h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_48_h():
    while True:
        await asyncio.sleep(12)

        text_autosending_48h = "🧚‍♂️Hello, on this wonderful day, the number of my students who have received astrological consultations this year has exceeded 1,500 people.\n\nIn honor of such an important event, I want to make you a unique offer and provide you with an astrological analysis and give you my author's meditation, which will help you double your income🎉\n\nTo receive analysis and a gift, write me your date of birth and code word MONEY in a private message - @YouAstro_bot👈"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("Pick up a gift🎁", url="https://t.me/Your_soul_assistant"))

        users_for_autosending_1 = await db_sendings.get_users_48h_autosending()
        for user in users_for_autosending_1:
            try:
                await bot.send_message(user, text_autosending_48h, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got autosending_text_48h')
                await db_sendings.mark_got_48h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_72h():
    while True:
        await asyncio.sleep(12)

        text = f'🪐Hello, I want to inform you that after {markdown.hbold("Your numerous requests")} - I {markdown.hbold("open the second stream")} and {markdown.hbold("I want to give 15") } lucky {markdown.hbold("free astrological analysis")}\n\n🙌If you {markdown.hbold("ready to find the right path in your life")}, then write {markdown.hbold("my date of birth in personal messages - @Your_soul_assistant👈")}'
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Get analysis🔱", url="https://t.me/Your_soul_assistant"))

        users_for_autosending_1 = await db_sendings.get_users_72h_autosending()
        for user in users_for_autosending_1:
            try:
                await bot.send_message(user, text, parse_mode='html', reply_markup=kb)
                logger.info(f'ID: {user}. Got autosending_text_72h')
                await db_sendings.mark_got_72h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated):
                logger.exception(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


@dp.callback_query_handler(lambda call: call.data == 'black_friday?get_gift', state='*')
async def send_black_friday_gift(call: types.CallbackQuery, state: FSMContext):
    chat_member = await bot.get_chat_member(-1002059782974, call.from_user.id)
    if chat_member.is_chat_member():
        await call.message.answer_document('BQACAgIAAxkBAAFqLvZlShPPCzUoYZKx5RVGi3ibd2iT6wACHTUAAofGUUq9ksqFXr6WfjME')
    else:
        await call.answer("Войдите в марафон, чтобы получить подарок ❤️")


async def bf_task(id_: int, sending: SendingData, db_func, skip_if_chat_member: bool = False, only_for_chat_member: bool = False):
    try:

        if skip_if_chat_member or only_for_chat_member:
            chat_member = await bot.get_chat_member(-1002059782974, id_)
            if chat_member.is_chat_member() and skip_if_chat_member:
                return 'skip'
            elif not chat_member.is_chat_member() and only_for_chat_member:
                return 'skip'
            name = chat_member.user.first_name
        else:
            name = None

        if id_ in skip_100_leads:
            return 'skip'

        text = await sending.get_text(bot, id_, name)
        if sending.photo is not None:
            await bot.send_photo(id_, types.InputFile(sending.photo), caption=text, reply_markup=sending.kb,
                                 parse_mode='html', disable_notification=True)
        else:
            await bot.send_message(id_, text=text, reply_markup=sending.kb,
                                   parse_mode='html', disable_web_page_preview=True)
        await db_func(id_)
        sending.count += 1
        logger.success(f'{id_} sending_{sending.uid} text')

    except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
        logger.exception(f'ID: {id_}. DELETED')
        await db.delete_user(id_)
    except Exception as e:
        logger.error(f'BUG: {e}')
    else:
        return 'success'
    return 'false'


async def sending_newsletter():
    white_day = 4
    now_time = datetime.now()

    if now_time.day > white_day:
        return

    while True:
        await asyncio.sleep(2)
        if now_time.day == white_day and now_time.hour >= 7:
            try:
                tasks = []
                users = [1371617744] + list(await db_sendings.get_users_for_sending_newsletter())
                print(len(users))
                for user in users:
                    logger.info(f"Пытаюсь отправить сообщение рассылки - {user}")
                    try:
                        _s = bf_sending
                        # if _s.count >= 80000:
                        #     break
                        tasks.append(asyncio.create_task(bf_task(user, _s, db_sendings.set_newsletter)))
                        if len(tasks) > 40:
                            print(len(tasks))
                            r = await asyncio.gather(*tasks, return_exceptions=False)
                            await asyncio.wait(tasks)
                            await asyncio.sleep(0.4)
                            logger.info(f"{r.count('success')=}", f"{r.count('false')=}", f"{r.count('skip')=}")
                            tasks.clear()

                    except Exception as ex:
                        logger.error(f'Ошибка в малом блоке sending: {ex}')
                    finally:
                        await asyncio.sleep(0.03)
            except Exception as ex:
                logger.error(f"Ошибка в большом блоке sending - {ex}")
            finally:
                await bot.send_message(1371617744, f"ERROR рассылка стопнулась.")
                logger.info("Рассылка завершилась")


async def on_startup(_):
    asyncio.create_task(sending_newsletter())
    asyncio.create_task(sending_messages_2h())
    asyncio.create_task(sending_message_24_h())
    asyncio.create_task(sending_message_48_h())
    asyncio.create_task(sending_message_72h())


async def update_db_advices_step_func():
    await db.update_users_advice_step()


try:
    a_logger = logging.getLogger('apscheduler.scheduler')
    a_logger.setLevel(logging.DEBUG)
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(trigger='cron', hour='00', minute='00', func=update_db_advices_step_func)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)
finally:
    stop = True
    logger.info("Бот закончил работу")
