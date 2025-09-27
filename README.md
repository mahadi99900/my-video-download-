#!/bin/bash

# ANSI Color Codes for a creative and readable output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
RESET='\033[0m'

# ----------------------------------------------------------------------------------
#          ✨ TELEGRAM BOT AUTOMATED SETUP SCRIPT ✨
# ----------------------------------------------------------------------------------
#    This script will automatically clone your specific repository,
#    set up the environment, install dependencies, and run your bot.
# ----------------------------------------------------------------------------------

echo -e "${PURPLE}
 B#######B O#######O T#######T
 B##     B O##   O## T##     T
 B#######B O##   O## T#######T
 B##     B O##   O## T##
 B#######B O#######O T##
${RESET}"

echo -e "${CYAN}🚀 Launching the automated setup for your Telegram Bot...${RESET}"
echo "--------------------------------------------------------"
sleep 2

# === Step 1: Clone Your Repository from GitHub ===
echo -e "\n${YELLOW}📂 Step 1: Cloning Your Repository...${RESET}"
echo "Downloading the project files from 'https://github.com/mahadi99900/my-video-download-.git'"
git clone https://github.com/mahadi99900/my-video-download-.git
echo -e "${GREEN}✅ Repository cloned successfully!${RESET}"
echo "--------------------------------------------------------"
sleep 2

# === Step 2: Navigate into the Project Directory ===
echo -e "\n${YELLOW}➡️ Step 2: Entering Project Directory...${RESET}"
cd my-video-download-
echo -e "${GREEN}✅ Successfully changed directory. Current location: $(pwd)${RESET}"
echo "--------------------------------------------------------"
sleep 2

# === Step 3: Create and Activate a Python Virtual Environment ===
echo -e "\n${YELLOW}🐍 Step 3: Setting Up Python Virtual Environment...${RESET}"
echo "This creates an isolated space for your project's libraries to avoid conflicts."
python3 -m venv venv
echo "Activating the virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment created and activated!${RESET}"
echo "--------------------------------------------------------"
sleep 2

# === Step 4: Install All Required Libraries ===
echo -e "\n${YELLOW}📦 Step 4: Installing All Required Dependencies...${RESET}"
echo "This will read the 'requirements.txt' file and install all packages automatically. Please wait..."
pip install -r requirements.txt
echo -e "${GREEN}✅ All dependencies have been installed successfully!${RESET}"
echo "--------------------------------------------------------"
sleep 2

# === Step 5: Run The Bot ===
echo -e "\n${YELLOW}🎉 Final Step: Launching the Bot...${RESET}"
echo "You will now be prompted to enter your Telegram Bot Token."
echo "Paste the token you received from BotFather and press Enter."
echo "To stop the bot at any time, press CTRL + C in this terminal."
sleep 3

python main.py

echo -e "\n${CYAN}✨ Bot session has ended. Thank you for using the script! ✨${RESET}"

# --- End of Script ---
