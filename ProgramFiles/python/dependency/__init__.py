from .Agents.chatbot import ChatBot
from .AdditionalTools.insertData import data_insert
from .AdditionalTools.createDatabase import create_errorDbase


__all__ = ["ChatBot"]

# Automaticaly creates database and table if not exists
create_errorDbase()

# Inserts data into tables
data_insert()
