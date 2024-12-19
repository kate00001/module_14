from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


api = 'ххххххххххххххххххххххххххххххххххххххххххххххххххх'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton(text='Расчитать')
button_info = KeyboardButton(text='Информация')
button_buy = KeyboardButton(text='Купить')
kb.row(button_calculate, button_info)
kb.add(button_buy)


inline_kb = InlineKeyboardMarkup(row_width=2)
inline_button1 = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
inline_button2 = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_button1, inline_button2)


inline_buy_kb = InlineKeyboardMarkup(row_width=4)
buttons = [InlineKeyboardButton(f"Продукт{i}", callback_data="product_buying") for i in range(1, 5)]
inline_buy_kb.add(*buttons)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def info(message: Message):
    await message.answer('Привет! Я бот, помогающий Вашему здоровью!', reply_markup=kb)


@dp.message_handler(text='Информация')
async def calories(message: Message):
    await message.answer('Я экспериментальный бот, сейчас я могу считать норму калорий, '
                         'а потом еще много чего смогу полезного сделать.')


@dp.message_handler(text='Расчитать')
async def main_menu(message: Message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = ("Формула Миффлина-Сан Жеора:\n"
                    "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161\n"
                    "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5")
    await call.message.answer(formula_text)
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = int(message.text)
    await message.reply("Введите свой рост (в см):")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['growth'] = int(message.text)
    await message.reply("Введите свой вес (в кг):")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['weight'] = int(message.text)
        age = data['age']
        growth = data['growth']
        weight = data['weight']
        bmr = 10 * weight + 6.25 * growth - 5 * age - 161
        await message.reply(f"Ваша норма калорий: {bmr:.2f} ккал в день.")
    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message: Message):
    for i in range(1, 5):
        image_path = f'filesforbot/Product{i}.jpeg'

        with open(image_path, 'rb') as photo:
            await message.answer_photo(
                photo=photo,
                caption=f"Название: Product{i} | Описание: описание {i} | Цена: {i * 100}"
            )

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_buy_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler()
async def all_messages(message: Message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
