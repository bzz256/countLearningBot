import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from bot.bot import dp
from database.models import create_tables, Result
from utils.utils import generate_problem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


# States
class Quiz(StatesGroup):
    quizStarted = State()
    quizAnswered = State()
    quizStopped = State()
    quiz = State()
    timeStart = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message, state: FSMContext):
    user_db = Result.get_or_none(Result.select(Result.name == message.from_user.first_name))
    current_state = await state.get_state()
    if current_state is None:
        if user_db is None:
            Result.create(name=message.from_user.first_name, score=0, answers=1, time=0)
            await message.answer(f'Привет, {message.from_user.first_name}! Похоже, ты у нас впервые!')
            await message.answer('Правильных ответов пока: 0')
        else:
            await message.answer(f'Привет, {message.from_user.first_name}!')
            await message.answer(f'Всего ответов: {user_db.answers - 1}')
            await message.answer(f'Правильных ответов: {user_db.score}')
            await message.answer(f'Среднее время ответа: {round((user_db.time / user_db.answers), 2)} сек.')
    quiz = generate_problem()
    await message.answer(f'Сколько будет {" ".join(quiz[0:3])} = ?', reply_markup=types.ReplyKeyboardRemove())
    logging.info(quiz)
    await state.update_data(quiz=quiz)
    await state.update_data(timeStart=datetime.datetime.now())
    await Quiz.quizStarted.set()


@dp.message_handler(state='*', commands='help')
async def help_handler(message: types.Message):
    pass


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='stop')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    user_data = await state.get_data()
    if 'timeStart' not in user_data.keys():
        elapsed_time = datetime.datetime.now() - datetime.datetime.now()
    else:
        elapsed_time = datetime.datetime.now() - user_data['timeStart']
    user_db = Result.get(Result.name == message.from_user.first_name)
    tmp = user_db.answers
    user_db.answers = tmp
    tmp = user_db.time
    user_db.time = tmp + elapsed_time.seconds
    user_db.save()
    if current_state is None:
        return
    logging.info('Bot is stopping. Cancelling state %r', current_state)
    await state.finish()
    await message.answer("Викторина завершена!", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f"Всего ответов: {user_db.answers - 1}")
    await message.answer(f"Правильных ответов: {user_db.score}")
    await message.answer(f"Среднее время ответа: {round((user_db.time / user_db.answers), 2)} сек.")


# Check answer - should be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Quiz.quizStarted)
async def process_answer_invalid(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    elapsed_time = datetime.datetime.now() - user_data['timeStart']
    user_db = Result.get(Result.name == message.from_user.first_name)
    tmp = user_db.answers
    user_db.answers = tmp + 1
    tmp = user_db.time
    user_db.time = tmp + elapsed_time.seconds
    user_db.save()
    return await message.reply("Ответ должен быть числом!")


@dp.message_handler(lambda message: message.text.isdigit(), state=Quiz.quizStarted)
async def process_answer(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    answer = str(user_data['quiz'][3])
    elapsed_time = datetime.datetime.now() - user_data['timeStart']
    user_db = Result.get(Result.name == message.from_user.first_name)
    if message.text == answer:
        kb = [
            [
                types.KeyboardButton(text="Давай ещё!"),
            ],
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Ещё примерчик?"
        )
        await message.answer(f"Правильных ответов: {user_db.score + 1}")
        await message.answer("Молодец! Ещё примерчик?", reply_markup=keyboard)
        await Quiz.quizAnswered.set()
        tmp = user_db.score
        user_db.score = tmp + 1
        tmp = user_db.answers
        user_db.answers = tmp + 1
        tmp = user_db.time
        user_db.time = tmp + elapsed_time.seconds
        user_db.save()
    else:
        tmp = user_db.answers
        user_db.answers = tmp + 1
        tmp = user_db.time
        user_db.time = tmp + elapsed_time.seconds
        user_db.save()
        await message.answer("Неправильно! Попробуй еще раз!")


@dp.message_handler(state=Quiz.quizAnswered)
async def process_next_quiz(message: types.Message, state: FSMContext):
    if message.text.lower() in ("давай ещё!", "да", "ага"):
        await cmd_start(message, state)
    else:
        await message.answer("Пока!", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()


if __name__ == '__main__':
    create_tables()
    executor.start_polling(dp, skip_updates=True)
