from sqlalchemy import Column, String, Integer

import config
from models.base_model import SQLMixin, db
from utils import log

class Token(SQLMixin, db.Model):

    token = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False)
