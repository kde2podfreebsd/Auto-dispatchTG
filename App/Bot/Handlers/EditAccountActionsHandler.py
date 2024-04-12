import os
import re

from telebot.asyncio_handler_backends import State
from telebot.asyncio_handler_backends import StatesGroup

from App.Bot.Handlers.EditAccountsMenuHandler import _editAccountsMenu
from App.Bot.Handlers.EditAccountsMenuHandler import _showAccountActions
from App.Bot.Markups import MarkupBuilder
from App.YandexGPT.YandexGPTMsgRebuilder import YandexGPTMessageRebuilder
from App.Config import account_context
from App.Config import bot
from App.Config import message_context_manager
from App.Config import sessions_dirPath
from App.Database.DAL.AccountTgDAL import AccountDAL
from App.Database.DAL.AccountStoriesDAL import AccountStoriesDAL
from App.Database.session import async_session


class EditAccountActionStates(StatesGroup):
    EditMessage = State()
    EditPrompt = State()
    AddAdvChat = State()
    RemoveAdvChat = State()
    ChangeTargetChat = State()
    ChangeStatus = State()
    DeleteAccount = State()
    SetDelay = State()

# --------------Change Message--------------


async def _sendChangeAccountMessageText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendChangeAccountMessageText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.EditMessage)


@bot.message_handler(state=EditAccountActionStates.EditMessage)
async def edit_message(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)

        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        await account_dal.updateMessage(
            session_name=account_context.account_name[message.chat.id],
            new_message=message.text,
        )

        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=MarkupBuilder.message_edited,
            reply_markup=MarkupBuilder.back_to_edit_menu(
                account_name=account_context.account_name[message.chat.id]
            ),
            parse_mode="HTML",
        )
        await message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )

# --------------Change Prompt--------------


async def _sendChangePromptText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendChangePromptText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.EditPrompt)


@bot.message_handler(state=EditAccountActionStates.EditPrompt)
async def edit_prompt(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)

        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        await account_dal.updatePrompt(
            session_name=account_context.account_name[message.chat.id],
            new_prompt=message.text,
        )

        msg = await bot.send_message(
            chat_id=message.chat.id, 
            text=MarkupBuilder.prompt_edited, 
            reply_markup=MarkupBuilder.back_to_edit_menu(
                account_name=account_context.account_name[message.chat.id]
            ),
            parse_mode="HTML"
        )

        await message_context_manager.add_msgId_to_help_menu_dict(
            chat_id=message.chat.id,
            msgId=msg.id
        )

# ------------------Change Delay-------------------
        

async def _sendChangeDelayText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendChangeDelayText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.SetDelay)

async def _errorNotIntegerDelay(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        message.chat.id
    )
    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.errorNotIntegerDelayTg,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name = account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML"
    )

    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, 
        msgId=msg.message_id
    )

    await bot.set_state(message.chat.id, EditAccountActionStates.SetDelay)

@bot.message_handler(state=EditAccountActionStates.SetDelay)
async def change_delay(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)
        new_delay = message.text
        pattern = r'^\d+$'
        if (re.match(pattern, new_delay) and new_delay != '0'):
            await account_dal.updateDelay(
                session_name=account_context.account_name[message.chat.id],
                new_delay=int(new_delay)
            )
            await message_context_manager.delete_msgId_from_help_menu_dict(
                chat_id=message.chat.id
            )
            msg = await bot.send_message(
                message.chat.id,
                MarkupBuilder.delayForSpamTgHasBeenSet,
                reply_markup=MarkupBuilder.back_to_edit_menu(
                    account_name=account_context.account_name[message.chat.id]
                ),
                parse_mode="HTML"
            )
            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, 
                msgId=msg.message_id
            )
        else:
            await _errorNotIntegerDelay(message)

# --------------Change Target Channel--------------


async def _sendChangeTargetChannelText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendChangePromptText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.ChangeTargetChat)


async def _errorSetTargetChannel(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.errorSetTargetChannel,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id],
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.ChangeTargetChat)


@bot.message_handler(state=EditAccountActionStates.ChangeTargetChat)
async def edit_target_chat(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)

        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        pattern = r"^@[A-Za-z0-9]+(_[A-Za-z0-9]+)*$"

        if re.match(pattern, message.text):
            await account_dal.updateTargetChat(
                session_name=account_context.account_name[message.chat.id],
                new_target_chat=message.text,
            )

            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=MarkupBuilder.target_edited,
                reply_markup=MarkupBuilder.back_to_edit_menu(
                    account_name=account_context.account_name[message.chat.id]
                ),
                parse_mode="HTML",
            )
            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )

        else:
            await _errorSetTargetChannel(message=message)


# --------------Add advertisement chat--------------


async def _sendAddAdvChatText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendAddAdvChatText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.AddAdvChat)


async def _errorSetAdvChat(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.errorSetTargetChannel,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.AddAdvChat)


@bot.message_handler(state=EditAccountActionStates.AddAdvChat)
async def add_adv_chat(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)

        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        pattern = r"^@[A-Za-z0-9]+(_[A-Za-z0-9]+)*$"

        if re.match(pattern, message.text):
            await account_dal.addAdvertisingChannel(
                session_name=account_context.account_name[message.chat.id],
                channel_name=message.text,
            )

            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=MarkupBuilder.adv_chat_added,
                reply_markup=MarkupBuilder.back_to_edit_menu(
                    account_name=account_context.account_name[message.chat.id]
                ),
                parse_mode="HTML",
            )

            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )

        else:
            await _errorSetAdvChat(message=message)


# --------------Remove advertisement chat--------------


async def _sendRemoveAdvChatText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendRemoveAdvChatText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.RemoveAdvChat)


async def _errorRemoveAdvChat(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.errorSetTargetChannel,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.RemoveAdvChat)

async def _errorNonExistentAdvChat(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.errorNonExistentAdvChat,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
    await bot.set_state(message.chat.id, EditAccountActionStates.RemoveAdvChat)

@bot.message_handler(state=EditAccountActionStates.RemoveAdvChat)
async def remove_adv_chat(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)

        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )

        pattern = r"^@[A-Za-z0-9]+(_[A-Za-z0-9]+)*$"

        if re.match(pattern, message.text):
            result = await account_dal.removeAdvertisingChannel(
                session_name=account_context.account_name[message.chat.id],
                channel_name=message.text,
            )
            if (result):
                msg = await bot.send_message(
                    chat_id=message.chat.id,
                    text=MarkupBuilder.adv_chat_removed,
                    reply_markup=MarkupBuilder.back_to_edit_menu(
                        account_name=account_context.account_name[message.chat.id]
                    ),
                    parse_mode="HTML",
                )
                
                await message_context_manager.add_msgId_to_help_menu_dict(
                    chat_id=message.chat.id, msgId=msg.message_id
                )
            else:
                await _errorNonExistentAdvChat(message)

        else:
            await _errorRemoveAdvChat(message=message)


# --------------Reload message by YandexGPT--------------

async def _errorNotAllFieldsFilledForYandexGPT(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.errorNotAllFieldsFilledForYandexGPT,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )

async def _sendReloadYandexGPTMessageText(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)
        account = await account_dal.getAccountBySessionName(
            session_name=account_context.account_name[message.chat.id]
        )
        if (account.message != "Не указано" and account.prompt != "Не указан" and account.target_chat != "Не указан"):

            await message_context_manager.delete_msgId_from_help_menu_dict(
                chat_id=message.chat.id
            )

            msg = await bot.send_message(
                message.chat.id,
                "⏰<b>Ожидаем ответ от YandexGPT</b>",
                reply_markup=MarkupBuilder.hide_menu,
                parse_mode="HTML",
            )
            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
            prompt = f"""
        Переформулируй и дополни рекламное сообщение.
        Не убирай {account.target_chat} из сообщения - это ссылка на рекламируемый чат. Если его нет, то обязательно добавь в конец сообщения.
        Не добавляй лишних слов в ответ, только сгенерированое рекламное сообщение.
        Вот описание канала, оно поможет для переформулировки и дополнения рекламного сообщения: {account.prompt}.
        Вот сообщение для редактирования: {account.message}
        """

            new_message = await YandexGPTMessageRebuilder.rewrite_message(
                cls=YandexGPTMessageRebuilder,
                account_name=account_context.account_name[message.chat.id],
                prompt=prompt
            )
            await account_dal.updateMessage(
                session_name=account_context.account_name[message.chat.id],
                new_message=new_message
            )

            await message_context_manager.delete_msgId_from_help_menu_dict(
                chat_id=message.chat.id
            )

            msg = await bot.send_message(
                message.chat.id,
                f"{MarkupBuilder.ReloadedYandexGPTMessageText}\n",
                reply_markup=MarkupBuilder.back_to_edit_menu(
                    account_name=account_context.account_name[message.chat.id]
                ),
                parse_mode="HTML",
            )
            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )
        else: 
            await _errorNotAllFieldsFilledForYandexGPT(message)


# --------------Reload message by ChatGPT--------------


async def _sendDeleteAccountText(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        MarkupBuilder.sendDeleteAccountText,
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )

    await bot.set_state(message.chat.id, EditAccountActionStates.DeleteAccount)


async def _errorDeleteAccountChat(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        message.chat.id,
        "❌ Ошибка удаления аккаунта телеграм",
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )
    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )

    await bot.delete_state(message.chat.id, message.chat.id)


@bot.message_handler(state=EditAccountActionStates.DeleteAccount)
async def delete_account(message):
    async with async_session() as session:
        account_dal = AccountDAL(session)
        account_stories_dal = AccountStoriesDAL(session)
        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )
        if message.text == "ДА, ТОЧНО":
            await account_dal.deleteAccount(
                session_name=account_context.account_name[message.chat.id]
            )
            await account_stories_dal.deleteAccountStories(
                session_name=account_context.account_name[message.chat.id]
            )
            if os.path.exists(
                f"{sessions_dirPath}/{account_context.account_name[message.chat.id]}.session"
            ):
                os.remove(
                    f"{sessions_dirPath}/{account_context.account_name[message.chat.id]}.session"
                )
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=MarkupBuilder.account_deleted,
                reply_markup=MarkupBuilder.back_to_acc_edit(),
                parse_mode="HTML",
            )
            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.id
            )
            await bot.delete_state(
                user_id=message.chat.id,
                chat_id=message.chat.id
            )
        else:
            await _errorDeleteAccountChat(message=message)


# --------------Edit account status--------------
async def _sendChangeStatusMenu(message):
    async with async_session() as session:

        await message_context_manager.delete_msgId_from_help_menu_dict(
            chat_id=message.chat.id
        )
        account_dal = AccountDAL(session)
        account = await account_dal.getAccountBySessionName(
            session_name=account_context.account_name[message.chat.id]
        )
        status = account.status
        ready_status = await account_dal.check_account_conditions(
            session_name=account_context.account_name[message.chat.id]
        )

        if not ready_status:
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=MarkupBuilder.not_ready_change_status(status=status),
                reply_markup=MarkupBuilder.back_to_edit_menu(
                    account_name=account_context.account_name[message.chat.id]
                ),
                parse_mode="HTML",
            )

            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )

        else:
            msg = await bot.send_message(
                chat_id=message.chat.id,
                text=MarkupBuilder.ready_change_status(status=status),
                reply_markup=MarkupBuilder.change_status_menu(
                    session_name=account_context.account_name[message.chat.id]
                ),
                parse_mode="HTML",
            )

            await message_context_manager.add_msgId_to_help_menu_dict(
                chat_id=message.chat.id, msgId=msg.message_id
            )


async def _set_status_on(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text="✅Текущий статус аккаунта: <b>Включен</b>",
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )

    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )


async def _set_status_off(message):
    await message_context_manager.delete_msgId_from_help_menu_dict(
        chat_id=message.chat.id
    )

    msg = await bot.send_message(
        chat_id=message.chat.id,
        text="❌Текущий статус аккаунта: <b>Выключен</b>",
        reply_markup=MarkupBuilder.back_to_edit_menu(
            account_name=account_context.account_name[message.chat.id]
        ),
        parse_mode="HTML",
    )

    await message_context_manager.add_msgId_to_help_menu_dict(
        chat_id=message.chat.id, msgId=msg.message_id
    )
