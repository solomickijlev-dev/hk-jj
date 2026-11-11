
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from aiogram.types.inline_query import InlineQuery

TOKEN = "9147467235:AAESUFoxUg_688cKWGDJkkW67BFIGN5Iszo"

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

active_offers = {}


@router.message(Command("start", "offer"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Бот активен!\n\n"
        "Напиши в любом чате:\n"
        "@nftsales514bot ссылка | цена"
    )


@router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    query = inline_query.query.strip()
    
    link = "t.me/nft/LunarSnake-120435"
    price = "600"
    
    if query:
        if "|" in query:
            parts = [p.strip() for p in query.split("|")]
            link = parts[0] if parts[0] else link
            price = parts[1] if len(parts) > 1 and parts[1] else price
        else:
            parts = query.split()
            link = parts[0] if parts[0] else link
            price = parts[1] if len(parts) > 1 and parts[1] else price

    gift_name = link.split("/")[-1] if "/" in link else "Gift"
    
    offer_id = str(hash(f"{inline_query.from_user.id}_{link}_{price}"))[-8:]
    active_offers[offer_id] = {"link": link, "price": price, "gift": gift_name}

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отклонить", callback_data=f"dec_{offer_id}"),
                InlineKeyboardButton(text="Принять", callback_data=f"acc_{offer_id}"),
            ]
        ]
    )

    card_text = (
        f"🎁 {gift_name} • {price} ⭐️ Stars\n"
        f"🔗 {link}\n\n"
        f"Пользователь предлагает вам сделку."
    )

    result = InlineQueryResultArticle(
        id=offer_id,
        title=f"{gift_name} • {price} ⭐️ Stars",
        description="Нажми чтобы отправить оффер",
        thumbnail_url="https://cdn-icons-png.flaticon.com/512/4213/4213958.png",
        input_message_content=InputTextMessageContent(
            message_text=card_text
        ),
        reply_markup=keyboard
    )

    await inline_query.answer([result], cache_time=1)


@router.callback_query(F.data.startswith("acc_"))
async def accept_callback(callback: CallbackQuery):
    offer_id = callback.data.split("_")[1]
    offer = active_offers.get(offer_id, {"link": "t.me/nft/LunarSnake-120435", "price": "600", "gift": "Gift"})
    
    accepted_text = (
        f"✅ Оффер принят!\n"
        f"🎁 {offer['gift']} • {offer['price']} ⭐️ Stars\n"
        f"🔗 {offer['link']}\n\n"
        f"• Передайте NFT на @sales_of_NFT_gifts"
    )

    new_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Передать NFT", url="https://t.me/sales_of_NFT_gifts")],
            [InlineKeyboardButton(text="✅ Подтвердить оффер", callback_data=f"conf_{offer_id}")]
        ]
    )

    await callback.answer()

    try:
        if callback.inline_message_id:
            await bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=accepted_text,
                reply_markup=new_keyboard
            )
        elif callback.message:
            await callback.message.edit_text(
                text=accepted_text,
                reply_markup=new_keyboard
            )
    except Exception as e:
        print(f"Ошибка редактирования (Accept): {e}")


@router.callback_query(F.data.startswith("conf_"))
async def confirm_callback(callback: CallbackQuery):
    offer_id = callback.data.split("_")[1]
    offer = active_offers.get(offer_id, {"price": "600"})
    
    await callback.answer(
        f"GiftRedo\n\nОффер принят!\n\nПередайте NFT на @sales_of_NFT_gifts\n\nСумма предложения: {offer['price']} Stars.",
        show_alert=True
    )


@router.callback_query(F.data.startswith("dec_"))
async def decline_callback(callback: CallbackQuery):
    offer_id = callback.data.split("_")[1]
    declined_text = "❌ Оффер отклонен."
    
    await callback.answer("❌ Оффер отклонен.", show_alert=True)

    try:
        if callback.inline_message_id:
            await bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=declined_text,
                reply_markup=None
            )
        elif callback.message:
            await callback.message.edit_text(
                text=declined_text,
                reply_markup=None
            )
    except Exception as e:
        print(f"Ошибка редактирования (Decline): {e}")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
