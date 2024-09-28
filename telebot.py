import os
import re
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

class TeleBot:
    def __init__(self, token, log_dir):
        self.token = token
        self.log_dir = log_dir
        
        # Enable logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
        )

        self.logger = logging.getLogger(__name__)
        
        # Initialize updater and dispatcher
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register the command and message handlers."""
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.search))
        self.dispatcher.add_error_handler(self.error)
        
    def _search_logs(self, keyword):
        """Search for the keyword in log files and return matches."""
        matches = []
        for root, dirs, files in os.walk(self.log_dir):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(keyword, line, re.IGNORECASE):
                                matches.append((file, line_num, line.strip()))
        return matches
    
    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the /start command is issued."""
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\! Send me a keyword to search in the logs\.',
            reply_markup=ForceReply(selective=True),
        )
    
    def search(self, update: Update, context: CallbackContext) -> None:
        """Search for the keyword in logs and return the results."""
        keyword = update.message.text
        results = self._search_logs(keyword)
        if results:
            response = "Found these matches:\n"
            response += "\n".join([f"File: {file} (Line: {line_num}) - {line}" for file, line_num, line in results])
        else:
            response = "No matches found."
        update.message.reply_text(response)
    
    def error(self, update: Update, context: CallbackContext) -> None:
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)
    
    def run(self):
        """Start the bot."""
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    # Initialize the bot with your token and the directory containing the log files
    token = "7254777150:AAFI69SAfyDZSC6BV0Qkw9EUFD7DJKxKGSI"  # Replace with your actual bot token
    log_dir = "path/to/your/logs"  # Change this to your log directory
    bot = TeleBot(token, log_dir)
    bot.run()
