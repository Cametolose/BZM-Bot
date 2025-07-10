# BZM-Discord-Bot

A Discord bot built with `discord.py` that was used by BZM.

## **Features**
✔️ **Verify Command** – Checks if a user's Hypixel account is linked to their Minecraft account and gives them a role. 

✔️ **User Data Storage** – Saves Discord and Minecraft usernames in a `.json` file.  
✔️ **Rollback** – Restores roles and sends a log to a designated channel.  
✔️ **Coinflip Simulation** – Flip a single coin or run multiple simulations.  
✔️ **Online Player List** – Manages a list of online players. Named "griefer" in my code.  
✔️ **Support Ticket System** – Users can create support tickets with different categories.  

## **Setup Instructions**

### **1. Clone the Repository**
```sh
git clone https://github.com/Cametolose/BZM-Bot.git
cd BZM-Bot
```

### **2. Install Dependencies**
Ensure you have Python & pip installed, then run:  
```sh
pip install -r requirements.txt
```

### **3. Configure the Bot**
Edit the `commands/config.py` file  

### **4. Run the Bot**
```sh
python bot.py
```

## **Commands**
| Command | Description |
|---------|-------------|
| `/verify <username>` | Checks if a Minecraft account is linked to Hypixel. |
| `/rollback_roles` | Restores verfied roles. |
| `/rollback_igns` | Sends the Minecraft & Discord username with Discord ID to a channel. |
| `/coinflip` | Flips a single coin. |
| `/coinflip <amount>` | Simulates multiple coin flips. |
| `/griefer` | Shows the list of online players. |
| `/griefer add <player>` | Adds a player to the online list. |
| `/griefer remove <player>` | Removes a player from the online list. |
| `/grieferlist` | Shows all player from the list. |
| `/molten_powder <mode> <value>` | Calculates live prices of molten powder flip |

## **License**
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  
