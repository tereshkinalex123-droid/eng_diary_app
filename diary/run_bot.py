import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary.settings')

import django

django.setup()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from accounts.models import Profile
from records.models import Record, Tag
from vocabulary.models import Deck, Card, CardProgress
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from django.utils import timezone

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

class ReviewCard(StatesGroup):
    waiting_for_card_limit = State()
    waiting_for_choice = State()
    waiting_for_front_answer = State()
    waiting_for_card_answer = State()

def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="➕ Add card", callback_data="add_card")],
        [InlineKeyboardButton(text="📝 Add entry", callback_data="add_entry")],
        [InlineKeyboardButton(text="Review", callback_data="start_review")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def keyboard_front_card():
    buttons = [
        [KeyboardButton(text="show back")],
        [KeyboardButton(text="show hint")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def keyboard_answer_card():
    buttons = [
        [KeyboardButton(text="0")],
        [KeyboardButton(text="1")],
        [KeyboardButton(text="2")],
        [KeyboardButton(text="3")],
        [KeyboardButton(text="4")],
        [KeyboardButton(text="5")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

async def store_message_id(state: FSMContext, message: types.Message):
    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(message.message_id)
    await state.update_data(message_ids=message_ids)


async def delete_all_messages(state: FSMContext, chat_id: int, bot_instance: Bot):
    data = await state.get_data()
    message_ids = data.get("message_ids", [])

    for msg_id in message_ids:
        try:
            await bot_instance.delete_message(chat_id, msg_id)
        except:
            pass

    await state.update_data(message_ids=[])


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


@sync_to_async
def save_card(tg_id, card_data):
    try:
        profile = Profile.objects.get(telegram_id=tg_id)
        current_user = profile.user

        deck = None
        if card_data.get('deck'):
            deck, _ = Deck.objects.get_or_create(
                user=current_user,
                name=card_data.get('deck')
            )

        card = Card.objects.create(
            user=current_user,
            front=card_data.get('front'),
            back=card_data.get('back'),
            examples=card_data.get('examples')
        )

        CardProgress.objects.create(
            card=card,
            user=current_user,
            next_review=timezone.now().date()
        )

        if deck:
            card.deck = deck

        card.save()

        return True
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        return False


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, command=None):
    token = command.args if command else None
    await delete_all_messages(state, message.chat.id, bot)

    if token:
        username = await link_user_to_tg(token, message.from_user.id)
        if username:
            msg = await message.answer(f"✅ Успешно! Аккаунт {username} привязан к этому Telegram.")
        else:
            msg = await message.answer("❌ Ошибка: ссылка недействительна или уже использована.")
    else:
        linked = await is_user_linked(message.from_user.id)
        if linked:
            username, _ = await get_full_user_info(message.from_user.id)
            msg = await message.answer(f"👋 Мы уже знакомы! Вы авторизованы как {username}.")
        else:
            msg = await message.answer(
                "👋 Привет! Чтобы связать бота с вашим аккаунтом на сайте, перейдите в профиль на сайте и нажмите кнопку 'Привязать Telegram'.")

    await store_message_id(state, msg)

    menu_msg = await message.answer("Menu:", reply_markup=get_main_keyboard())
    await store_message_id(state, menu_msg)


@dp.callback_query(lambda c: c.data in ["add_card", "add_entry", "start_review"])
async def handle_menu_callbacks(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await delete_all_messages(state, callback.message.chat.id, bot)

    current_state = await state.get_state()
    if current_state is not None:
        msg = await callback.message.answer("⚠️ Please finish current operation first. Send /cancel to abort.")
        await store_message_id(state, msg)
        return

    if callback.data == "add_card":
        linked = await is_user_linked(callback.from_user.id)
        if not linked:
            msg = await callback.message.answer("⚠️ Сначала привяжите аккаунт через профиль на сайте!")
            await store_message_id(state, msg)
            return

        msg = await callback.message.answer("📝 Введите фронт для вашей карточки:")
        await store_message_id(state, msg)
        await state.set_state(AddCard.waiting_for_front)

    elif callback.data == "add_entry":
        linked = await is_user_linked(callback.from_user.id)
        if not linked:
            msg = await callback.message.answer("⚠️ Сначала привяжите аккаунт через профиль на сайте!")
            await store_message_id(state, msg)
            return

        msg = await callback.message.answer("📝 Введите заголовок для вашей записи:")
        await store_message_id(state, msg)
        await state.set_state(AddRecord.waiting_for_title)

    elif callback.data == "start_review":
        linked = await is_user_linked(callback.from_user.id)
        if not linked:
            msg = await callback.message.answer("⚠️ Сначала привяжите аккаунт через профиль на сайте!")
            await store_message_id(state, msg)
            return

        msg = await callback.message.answer("Введите количество карточек для повторения: ")
        await store_message_id(state, msg)
        await state.set_state(ReviewCard.waiting_for_card_limit)


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await delete_all_messages(state, message.chat.id, bot)
    await state.clear()
    msg = await message.answer("✅ Operation cancelled.", reply_markup=get_main_keyboard())
    await store_message_id(state, msg)

@sync_to_async
def get_cards(message, card_limit, deck=None):
    cards = CardProgress.objects.filter(user__profile__telegram_id=message.from_user.id, next_review__lte=timezone.now().date())
    if deck:
        cards = cards.filter(card__deck=deck)

    cards = cards.order_by("next_review")[:card_limit]

    cards_data = [
        {
            "progress_id": c.id,
            "front": c.card.front,
            "back": c.card.back,
            "hint": c.card.hint
        }
        for c in cards
    ]

    return cards_data

@sync_to_async
def update_after_review(progress_id, grade):
    progress = CardProgress.objects.get(id=progress_id)
    progress.update_after_review(grade)

@dp.message(ReviewCard.waiting_for_card_limit)
async def process_review(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    limit = int(message.text)
    await state.update_data(limit=limit)
    cards = await get_cards(message, limit)
    await state.update_data(cards=cards)
    if (not cards):
        await delete_all_messages(state, message.chat.id, bot)
        await state.clear()
        msg = await message.answer("Нет карт для повторения", reply_markup=get_main_keyboard())
        await store_message_id(state, msg)
    elif (len(cards) < limit):
        msg = await message.answer(f"{len(cards)} карт для повторения, желаете продолжить с меньшим количчством карт?")
        await store_message_id(state, msg)
        await state.set_state(ReviewCard.waiting_for_choice)
    else:
        await delete_all_messages(state, message.chat.id, bot)
        await state.update_data(current_card=0, right_answers=0)
        await show_card(message, state)

async def show_card(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    data = await state.get_data()
    current_card = int(data.get("current_card", 0))
    cards = data.get("cards")
    limit = data.get("limit")

    if current_card >= limit:
        await process_review_result(message, state)
        return

    card_dict = cards[current_card]
    front = card_dict["front"]

    msg = await message.answer(
        f"{current_card + 1}/{limit}\n{front}",
        reply_markup=keyboard_front_card()
    )
    await store_message_id(state, msg)
    await state.set_state(ReviewCard.waiting_for_front_answer)


@dp.message(ReviewCard.waiting_for_choice)
async def process_choice(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    await delete_all_messages(state, message.chat.id, bot)
    if message.text.lower() == "нет":
        await state.clear()
        await message.answer("Ревью отменено", reply_markup=get_main_keyboard())
    elif message.text.lower() == "да":
        data = await state.get_data()
        cards = data.get("cards")
        await state.update_data(current_card=0, right_answers=0, limit=len(cards))
        await show_card(message, state)

@dp.message(ReviewCard.waiting_for_front_answer)
async def process_front_answer(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    answer = message.text
    data = await state.get_data()
    current_card = int(data.get("current_card", 0))
    cards = data.get("cards")
    card_dict = cards[current_card]
    back = card_dict["back"]
    hint = card_dict["hint"]


    if answer == "show hint":
        msg = await message.answer(hint, reply_markup=keyboard_front_card())
        await store_message_id(state, msg)
        await state.set_state(ReviewCard.waiting_for_front_answer)
    elif answer == "show back":
        msg = await message.answer(back, reply_markup=keyboard_answer_card())
        await store_message_id(state, msg)
        await state.set_state(ReviewCard.waiting_for_card_answer)


@dp.message(ReviewCard.waiting_for_card_answer)
async def process_card_answer(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    grade = int(message.text)
    data = await state.get_data()

    current_card = data.get("current_card", 0)
    cards = data.get("cards")
    right_answers = data.get("right_answers", 0)

    card_dict = cards[current_card]
    progress_id = card_dict["progress_id"]

    await update_after_review(progress_id, grade)

    if grade >= 3:
        right_answers += 1

    current_card += 1

    await delete_all_messages(state, message.chat.id, bot)

    await state.update_data(
        current_card=current_card,
        right_answers=right_answers
    )

    await show_card(message, state)

async def process_review_result(message: types.Message, state: FSMContext):
    right_answers = (await state.get_data()).get("right_answers")
    limit = (await state.get_data()).get("limit")
    await delete_all_messages(state, message.chat.id, bot)
    await state.clear()
    msg = await message.answer(f"результаты ревью: {right_answers} / {limit}", reply_markup=get_main_keyboard())
    await store_message_id(state, msg)

@dp.message(AddCard.waiting_for_front)
async def process_front(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    await state.update_data(front=message.text)
    msg = await message.answer("Отлично! Теперь введите бэк карты:")
    await store_message_id(state, msg)
    await state.set_state(AddCard.waiting_for_back)


@dp.message(AddCard.waiting_for_back)
async def process_back(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    await state.update_data(back=message.text)
    msg = await message.answer("Отлично! Теперь введите примеры использования (или напишите 'нет', если примеров нет):")
    await store_message_id(state, msg)
    await state.set_state(AddCard.waiting_for_examples)


@dp.message(AddCard.waiting_for_examples)
async def process_examples(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    text_examples = message.text if message.text.lower() != "нет" else ""
    await state.update_data(examples=text_examples)
    msg = await message.answer("Отлично! Теперь введите название колоды (или напишите 'нет', если колоды нет):")
    await store_message_id(state, msg)
    await state.set_state(AddCard.waiting_for_deck)


@dp.message(AddCard.waiting_for_deck)
async def process_deck(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    text_deck = message.text if message.text.lower() != "нет" else ""
    await state.update_data(deck=text_deck)

    card_data = await state.get_data()

    status_msg = await message.answer("💾 Сохранение карты...")
    await store_message_id(state, status_msg)

    success = await save_card(message.from_user.id, card_data)

    await delete_all_messages(state, message.chat.id, bot)
    await state.clear()

    if success:
        final_msg = await message.answer("✅ Карта успешно сохранена!", reply_markup=get_main_keyboard())
    else:
        final_msg = await message.answer("❌ Произошла ошибка при сохранении.", reply_markup=get_main_keyboard())

    await store_message_id(state, final_msg)


@dp.message(AddRecord.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    await state.update_data(title=message.text)
    msg = await message.answer("Отлично! Теперь введите основной текст записи:")
    await store_message_id(state, msg)
    await state.set_state(AddRecord.waiting_for_content)


@dp.message(AddRecord.waiting_for_content)
async def process_content(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    await state.update_data(content=message.text)
    msg = await message.answer("Введите теги через запятую (или напишите 'нет', если тегов нет):")
    await store_message_id(state, msg)
    await state.set_state(AddRecord.waiting_for_tags)


@dp.message(AddRecord.waiting_for_tags)
async def process_tags(message: types.Message, state: FSMContext):
    await store_message_id(state, message)
    tags_text = message.text if message.text.lower() != 'нет' else ""
    user_data = await state.get_data()
    user_data['tags'] = tags_text

    status_msg = await message.answer("⌛ Сохраняю запись...")
    await store_message_id(state, status_msg)

    success = await save_new_record(message.from_user.id, user_data)

    await delete_all_messages(state, message.chat.id, bot)
    await state.clear()

    if success:
        final_msg = await message.answer("✅ Запись успешно добавлена в ваш дневник!")
        await message.answer("Menu:", reply_markup=get_main_keyboard())
    else:
        final_msg = await message.answer("❌ Произошла ошибка при сохранении.", reply_markup=get_main_keyboard())

    await store_message_id(state, final_msg)


@dp.message(Command("me"))
async def show_me(message: types.Message, state: FSMContext):
    await delete_all_messages(state, message.chat.id, bot)
    username, email = await get_full_user_info(message.from_user.id)

    if username:
        display_email = email if email else "не указан"
        msg = await message.answer(f"👤 Ваш профиль: {username}\n📧 Email: {display_email}",
                                   reply_markup=get_main_keyboard())
    else:
        msg = await message.answer("⚠️ Вы еще не привязали Telegram. Сделайте это в профиле на сайте.",
                                   reply_markup=get_main_keyboard())

    await store_message_id(state, msg)


@dp.message(Command("myid"))
async def my_id_check(message: types.Message, state: FSMContext):
    await delete_all_messages(state, message.chat.id, bot)
    tg_id_from_telegram = message.from_user.id
    profile_exists = await is_user_linked(tg_id_from_telegram)
    msg = await message.answer(
        f"Бот видит ваш ID: {tg_id_from_telegram}\nЕсть в базе: {'Да' if profile_exists else 'Нет'}",
        reply_markup=get_main_keyboard())
    await store_message_id(state, msg)


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