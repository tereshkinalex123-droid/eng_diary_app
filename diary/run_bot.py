import os
import sys
import asyncio
import traceback


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary.settings')

import django

django.setup()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

from accounts.models import Profile
from records.models import Record, Tag
from vocabulary.models import Deck, Card

TOKEN = "8765444672:AAEjNIXbOrExePt_I6HuotvVD-b74USQNtw"

bot = Bot(token=TOKEN)
dp = Dispatcher()


class AddRecord(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_tags = State()

class AddCard(StatesGroup):
    waiting_for_front = State()
    waiting_for_back = State()
    waiting_for_examples = State()
    waiting_for_deck = State()

@sync_to_async
def link_user_to_tg(token, tg_id):
    try:
        profile = Profile.objects.get(connection_token=token)
        profile.telegram_id = tg_id
        profile.connection_token = None
        profile.save()
        return profile.user.username
    except Profile.DoesNotExist:
        return None


@sync_to_async
def is_user_linked(tg_id):
    return Profile.objects.filter(telegram_id=tg_id).exists()


@sync_to_async
def get_full_user_info(tg_id):
    try:
        profile = Profile.objects.select_related('user').get(telegram_id=tg_id)
        return profile.user.username, profile.user.email
    except Profile.DoesNotExist:
        return None, None


@sync_to_async
def save_new_record(tg_id, data):
    try:
        profile = Profile.objects.get(telegram_id=tg_id)
        current_user = profile.user

        record = Record.objects.create(
            user=current_user,
            title=data['title'],
            content=data['content']
        )

        if data.get('tags'):
            for tag_raw in data['tags'].split(','):
                tag_name = tag_raw.strip().lower()
                if tag_name:
                    add_tag, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        user=current_user
                    )
                    record.tags.add(add_tag)

        return True
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        return False


@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    token = command.args

    if token:
        username = await link_user_to_tg(token, message.from_user.id)
        if username:
            await message.answer(f"✅ Успешно! Аккаунт {username} привязан к этому Telegram.")
        else:
            await message.answer("❌ Ошибка: ссылка недействительна или уже использована.")
    else:
        linked = await is_user_linked(message.from_user.id)
        if linked:
            username, _ = await get_full_user_info(message.from_user.id)
            await message.answer(f"👋 Мы уже знакомы! Вы авторизованы как {username}.")
        else:
            await message.answer(
                "👋 Привет! Чтобы связать бота с вашим аккаунтом на сайте, перейдите в профиль на сайте и нажмите кнопку 'Привязать Telegram'.")


@dp.message(Command("me"))
async def show_me(message: types.Message):
    username, email = await get_full_user_info(message.from_user.id)

    if username:
        display_email = email if email else "не указан"
        await message.answer(f"👤 Ваш профиль: {username}\n📧 Email: {display_email}")
    else:
        await message.answer("⚠️ Вы еще не привязали Telegram. Сделайте это в профиле на сайте.")


@sync_to_async
def save_card(tg_id, card_data):
    try:
        profile = Profile.objects.get(telegram_id=tg_id)
        current_user = profile.user

        if card_data.get('deck'):
           deck = Deck.objects.get_or_create(
               user=current_user,
               name=card_data.get('deck')
           )[0]

        card = Card.objects.create(
            user=current_user,
            front=card_data.get('front'),
            back=card_data.get('back'),
            examples=card_data.get('examples')
        )
        if deck:
            card.deck = deck;
        card.save()

        return True
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        return False

@dp.message(Command("add_card"))
async def start_add_card(message: types.Message, state: FSMContext):
    linked = await is_user_linked(message.from_user.id)
    if not linked:
        await message.answer("⚠️ Сначала привяжите аккаунт через профиль на сайте!")
        return

    await message.answer("📝 Введите фронт для вашей карточки:")
    await state.set_state(AddCard.waiting_for_front)

@dp.message(AddCard.waiting_for_front)
async def process_front(message: types.Message, state: FSMContext):
    await state.update_data(front=message.text)
    await message.answer("Отлично! Теперь введите бэк карты:")
    await state.set_state(AddCard.waiting_for_back)

@dp.message(AddCard.waiting_for_back)
async def process_back(message: types.Message, state: FSMContext):
    await state.update_data(back=message.text)
    await message.answer("Отлично! Теперь введите примеры использования (или напишите 'нет', если примеров нет):")
    await state.set_state(AddCard.waiting_for_examples)

@dp.message(AddCard.waiting_for_examples)
async def process_examples(message: types.Message, state: FSMContext):
    text_examples = message.text if message.text.lower() != "нет" else ""
    await state.update_data(examples=text_examples)
    await message.answer("Отлично! Теперь введите деку использования (или напишите 'нет', если деки нет):")
    await state.set_state(AddCard.waiting_for_deck)

@dp.message(AddCard.waiting_for_deck)
async def process_deck(message: types.Message, state: FSMContext):
    text_deck = message.text if message.text.lower() != "нет" else ""
    await state.update_data(deck=text_deck)
    card_data = await state.get_data()

    await message.answer("Сохранение карты...")
    success = await save_card(message.from_user.id, card_data)

    if success:
        await message.answer("Сохранено успешни успех")
    else:
        await message.answer("лошарски лох")

    await state.clear()

@dp.message(AddRecord.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Отлично! Теперь введите основной текст записи:")
    await state.set_state(AddRecord.waiting_for_content)

@dp.message(AddRecord.waiting_for_content)
async def process_content(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer("Введите теги через запятую (или напишите 'нет', если тегов нет):")
    await state.set_state(AddRecord.waiting_for_tags)

@dp.message(AddRecord.waiting_for_tags)
async def process_tags(message: types.Message, state: FSMContext):
    tags_text = message.text if message.text.lower() != 'нет' else ""
    user_data = await state.get_data()
    user_data['tags'] = tags_text

    await message.answer("⌛ Сохраняю запись...")

    success = await save_new_record(message.from_user.id, user_data)

    if success:
        await message.answer("✅ Запись успешно добавлена в ваш дневник!")
    else:
        await message.answer("❌ Произошла ошибка при сохранении.")

    await state.clear()

@dp.message(Command("add_entry"))
async def start_add_entry(message: types.Message, state: FSMContext):
    linked = await is_user_linked(message.from_user.id)
    if not linked:
        await message.answer("⚠️ Сначала привяжите аккаунт через профиль на сайте!")
        return

    await message.answer("📝 Введите заголовок для вашей записи:")
    await state.set_state(AddRecord.waiting_for_title)


@dp.message(Command("myid"))
async def my_id_check(message: types.Message):
    tg_id_from_telegram = message.from_user.id
    profile_exists = await is_user_linked(tg_id_from_telegram)
    await message.answer(f"Бот видит ваш ID: {tg_id_from_telegram}\nЕсть в базе: {'Да' if profile_exists else 'Нет'}")


async def main():
    print("🚀 Бот запущен и готов к работе...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен.")