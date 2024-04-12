from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import and_

from App.Database.Models.Models import AccountStories, PremiumChatMember
from App.Logger import ApplicationLogger

import asyncio
from App.Database.session import async_session
from App.Config import sessions_dirPath

logger = ApplicationLogger()

class ChatMemberDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def createChatMember(self, username, account_stories_id, target_channel):
        try:
            existing_account = await self.getChatMember(
                username=username, 
                account_stories_id=account_stories_id
            )
            if existing_account:
                logger.log_error(f"ChatMember with username {username} has already been added to data base")
                return None
            
            premium_chat_member = PremiumChatMember(
                username=username, 
                account_stories_id=account_stories_id,
                target_channel=target_channel
            )
            self.db_session.add(premium_chat_member)
            await self.db_session.flush()
            return premium_chat_member
        except IntegrityError:
            await self.db_session.rollback()
            logger.log_warning("IntegrityError, db rollback")
            return None

    async def deleteChatMember(self, username, account_stories_id):
        premium_chat_member = await self.getChatMember(
            username=username, 
            account_stories_id=account_stories_id
        )
        if premium_chat_member:
            await self.db_session.delete(premium_chat_member)
            await self.db_session.flush()
            logger.log_info(f"ChatMember {username} has been removed from the data base")
            return True
        else:
            logger.log_error("ChatMember doesn't exist in database")
            return False
    
    async def deleteChatMemberByIdAndTargetChannel(self, username, target_channel, account_stories_id):
        premium_chat_member = await self.getChatMemberByIdAndTargetChannel(
            username=username, 
            target_channel=target_channel, 
            account_stories_id=account_stories_id
        )

        if premium_chat_member:
            await self.db_session.delete(premium_chat_member)
            await self.db_session.flush()
            logger.log_info(f"ChatMember {username} has been removed from the data base")
            return True
        else:
            logger.log_error("ChatMember doesn't exist in database")
            return False

    async def getChatMember(self, username, account_stories_id):
        query = select(PremiumChatMember).where(PremiumChatMember.username == username).where(PremiumChatMember.account_stories_id == account_stories_id)
        result = await self.db_session.execute(query)
        return result.scalar()
    
    async def getChatMemberByIdAndTargetChannel(self, username, target_channel, account_stories_id):
        query = select(PremiumChatMember).where(PremiumChatMember.username == username).where(
            and_(
                PremiumChatMember.account_stories_id == account_stories_id,
                PremiumChatMember.target_channel == target_channel
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar()