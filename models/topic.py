import time

from sqlalchemy import String, Integer, Column, Text, UnicodeText, Unicode

from models.base_model import SQLMixin, db
from models.user import User
from models.reply import Reply
from models.board import Board
from utils import log

class Topic(SQLMixin, db.Model):
    views = Column(Integer, nullable=False, default=0)
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)
    board_id = Column(Integer, nullable=False)

    @classmethod
    def add(cls, form, user_id):
        form['user_id'] = user_id
        # log('怀疑出错的地方', form)
        m = super().new(form)
        return m

    @classmethod
    def get(cls, id):
        m = cls.one(id=id)
        m.views += 1
        m.save()
        return m

    def user(self):
        u = User.one(id=self.user_id)
        return u

    def replies(self):
        ms = Reply.all(topic_id=self.id)
        return ms

    def reply_count(self):
        count = len(self.replies())
        return count

    def board(self):
        b = Board.one(id=self.board_id)
        return b
