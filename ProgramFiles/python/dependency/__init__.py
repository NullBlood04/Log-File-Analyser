from .Agents.chatbot import ChatBot
from .initialSetups.process_logs import process_new_logs
from .initialSetups.createDatabase import create_errorDbase


__all__ = ["ChatBot"]


# Create database and insert data if not exists
create_errorDbase()
process_new_logs()
