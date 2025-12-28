from src.bot.handler import BotHandler
import os


if __name__ == "__main__":

    # Ensure required directories exist
    os.makedirs("models", exist_ok=True)

    print("initializing bot…") 
    bot = BotHandler()

    print("Starting bot…")  
    bot.run()   



