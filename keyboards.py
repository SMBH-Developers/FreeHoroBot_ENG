from aiogram import types


class Markups:
    start_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_mrkup.add(types.KeyboardButton(text='✨Get a horoscope'))
    start_mrkup.add(types.KeyboardButton(text='📜Educational Menu'))

    study_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    study_btns_titles = ['✨What is astrology?', '✨What is a horoscope?',
                         '✨How did the first horoscope appear?', '✨Astrological advice of the day',
                         '✨What do they study in astrology?', '✨What are the 12 houses in astrology?',
                         '✨Which house is responsible for work?', '✨Which house is responsible for family?',
                         '🙏Get a horoscope']

    study_mrkup.add(types.KeyboardButton('✨What is astrology?'), types.KeyboardButton('✨What is a horoscope?'))
    study_mrkup.add(types.KeyboardButton('✨How did the first horoscope appear?'), types.KeyboardButton('✨Astrological advice of the day'))
    study_mrkup.add(types.KeyboardButton('✨What do they study in astrology?'), types.KeyboardButton('✨What are the 12 houses in astrology?'))
    study_mrkup.add(types.KeyboardButton('✨Which house is responsible for work?'), types.KeyboardButton('✨Which house is responsible for family?'))
    study_mrkup.add(types.KeyboardButton('🙏Get a personalized horoscope'))

    mrkup_for_every_study_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mrkup_for_every_study_btn.add(types.KeyboardButton('✨Get a horoscope for the year'))
    mrkup_for_every_study_btn.add(types.KeyboardButton('👈Back'))

    to_menu_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    to_menu_mrkup.add(types.KeyboardButton('📜Educational Menu'))

    kb_if_how_to_get_know_zodiac = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb_if_how_to_get_know_zodiac.add(types.KeyboardButton(text='✨Get a horoscope for 2024'))
    kb_if_how_to_get_know_zodiac.add(types.KeyboardButton(text='👈Back'))

    admin_mrkup = types.InlineKeyboardMarkup()
    admin_mrkup.add(types.InlineKeyboardButton(text='Пользователей всего', callback_data='Admin_Users_Total'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Пользователей за сегодня', callback_data='Admin_Users_For_TODAY'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Ввели дату за сегодня', callback_data='Admin_Dates_For_TODAY'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Зашли после рассылки 17ого марта 19:15', callback_data='Admin_17_march_sending'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Рассылка', callback_data='Admin_Send_Messages'))  # Рассылка по любым
    admin_mrkup.add(types.InlineKeyboardButton(text='Рассылка тем, кто еще не перешёл', callback_data='Admin_Special_Send_Msgs'))  # Раcсылка только по тем, кто не перешёл на наш аккаунт
    admin_mrkup.add(types.InlineKeyboardButton(text='Перешедших по реф ссылкам', callback_data='Admin_Referal_Users'))
    back_admin_mrkup = types.InlineKeyboardMarkup()
    back_admin_mrkup.add(types.InlineKeyboardButton(text='⬅️ В меню админа', callback_data='Admin_BACK'))

    @staticmethod
    def generate_send_msgs_step(sending_type: str) -> types.InlineKeyboardMarkup:
        send_messages_step_mrkup = types.InlineKeyboardMarkup()
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Первая ступень', callback_data=f'Sending?Step=0&type={sending_type}'),
                                     types.InlineKeyboardButton(text='Вторая ступень', callback_data=f'Sending?Step=1&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Третья ступень', callback_data=f'Sending?Step=2&type={sending_type}'),
                                     types.InlineKeyboardButton(text='Четвёртая ступень', callback_data=f'Sending?Step=3&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Отправить всем', callback_data=f'Sending?Step=ALL&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='⬅️ В меню админа', callback_data='Admin_BACK'))
        return send_messages_step_mrkup

    back_to_steps = types.InlineKeyboardMarkup()
    back_to_steps.add(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='Admin_Send_Messages'))

    cancel_sending = types.InlineKeyboardMarkup()
    cancel_sending.add(types.InlineKeyboardButton(text='Отмена!', callback_data='Cancel_Getting_Msg_For_Sending'))

    to_our_tg_mrkup = types.InlineKeyboardMarkup()
    to_our_tg_mrkup.add(types.InlineKeyboardButton(text='GET HOROSCOPE', url=f'https://t.me/Your_soul_assistant'))

    @staticmethod
    def generate_delete_msg_mrkup(arg=None):
        mrkup_to_del_msg = types.InlineKeyboardMarkup()
        mrkup_to_del_msg.add(types.InlineKeyboardButton('Close', callback_data=f'delete_msg{arg if arg else ""}'))
        return mrkup_to_del_msg

    mrkup_referal_program = types.InlineKeyboardMarkup()
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨Check if conditions are met', callback_data='ref_program?check_reqs'))
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨View reviews', callback_data='ref_program?reviews'))
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨How to invite friends correctly', callback_data='ref_program?guide'))
