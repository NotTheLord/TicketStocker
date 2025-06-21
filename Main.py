import http.client
import json
import time
import random
import urllib.parse
from datetime import datetime

# Configuration
RESTOCK_INTERVAL_MINUTES = 15  # Change this value to adjust restock timing
UNIVERSE_ID = "7920755743"
API_KEY = "SRdqqjZDkEiHsOBVXNLX6+ItFIzan5RQgu0TTUyqN7lC4w5YZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaVlYTmxRWEJwUzJWNUlqb2lVMUprY1hGcVdrUnJSV2xJYzA5Q1ZsaE9URmcySzBsMFJrbDZZVzQxVWxGbmRUQlVWRlY1Y1U0M2JFTTBkelZaSWl3aWIzZHVaWEpKWkNJNklqRTNNell5TVRNNE1qVWlMQ0poZFdRaU9pSlNiMkpzYjNoSmJuUmxjbTVoYkNJc0ltbHpjeUk2SWtOc2IzVmtRWFYwYUdWdWRHbGpZWFJwYjI1VFpYSjJhV05sSWl3aVpYaHdJam94TnpVd05UQXpNVGM1TENKcFlYUWlPakUzTlRBME9UazFOemtzSW01aVppSTZNVGMxTURRNU9UVTNPWDAuZmVmSmZpVFB5dHl6bmhPVzU4VWNFV1JXbnNpQnc0RFZWWWJILWJLbUpiWjlScWVHa18wdnVfNnlWZzNDbEtXZnlFUEZQSW5xSmhIZTZoNmxmNWNGdnpDWjhkdl83OVMzQzU0T2hKOWFnSGdqV0pYbHBHTWZDSEVMU20xR01pRGpvd1d2RlluMWV3OENxbGJyUW5jaEtuRUktWWJ2Tkx4Qi0xRklaM2NvVnA1Wms2ZkpjY25nNkZTQ2RMLVpTZ1Y3bWJxMHNONXNpOC1CMFBpbk5DQzBqTUVCal83TGd0TGFZNWtaSGp4S3M0Qlp1WEo4UHNMa3RvQS1tVHMtU2N4MTFabmJMY0xHU0pUeXlzaUZNX1FXQ2ttYlptWG9fUzBoRktOVkp3ZG9jc2ZUTWYzS01lWGhiMUpub0M0MzJxQVhZa3Z3U00zdUh3RkowMDVUYmk2S0VR"

# Rarity system configuration
RARITY_SYSTEM = {
    "common": {"weight": 86, "min_stock": 1, "max_stock": 2},
    "uncommon": {"weight": 9, "min_stock": 3, "max_stock": 8},
    "rare": {"weight": 3, "min_stock": 9, "max_stock": 20},
    "epic": {"weight": 1.9, "min_stock": 21, "max_stock": 50},
    "legendary": {"weight": 0.1, "min_stock": 51, "max_stock": 100}
}

def get_rarity_emoji(rarity):
    """Get emoji for rarity level"""
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟡"
    }
    return emojis.get(rarity, "⚪")

def determine_stock_amount():
    """Determine stock amount based on rarity system"""
    # Create weighted list
    weighted_rarities = []
    for rarity, config in RARITY_SYSTEM.items():
        # Add rarity multiple times based on weight (multiply by 10 for precision)
        count = int(config["weight"] * 10)
        weighted_rarities.extend([rarity] * count)
    
    # Select random rarity
    selected_rarity = random.choice(weighted_rarities)
    config = RARITY_SYSTEM[selected_rarity]
    
    # Generate stock amount within rarity range
    stock_amount = random.randint(config["min_stock"], config["max_stock"])
    
    return stock_amount, selected_rarity

def update_with_http_client(stock_data):
    """Alternative method using http.client"""
    
    # Connection
    conn = http.client.HTTPSConnection("apis.roblox.com")
    
    # Parameters
    params = urllib.parse.urlencode({
        'datastoreName': 'GlobalTicketStock',
        'entryKey': 'Stock'
    })
    
    # Headers
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Data
    json_data = json.dumps(stock_data)
    
    try:
        # Make request
        conn.request(
            "POST", 
            f"/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?{params}",
            body=json_data,
            headers=headers
        )
        
        # Get response
        response = conn.getresponse()
        data = response.read().decode()
        
        print(f"Status: {response.status}")
        print(f"Response: {data}")
        
        return response.status == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def get_valid_restock_minutes():
    """Get list of valid restock minutes based on interval"""
    valid_minutes = []
    minute = 0
    while minute < 60:
        valid_minutes.append(minute)
        minute += RESTOCK_INTERVAL_MINUTES
    return valid_minutes

def wait_for_next_restock_time():
    """Wait until the next restock interval"""
    current_time = time.time()
    current_dt = datetime.fromtimestamp(current_time)
    current_minute = current_dt.minute
    current_second = current_dt.second
    
    # Get valid restock minutes
    valid_minutes = get_valid_restock_minutes()
    
    # Find next restock minute
    next_restock_minute = None
    for minute in valid_minutes:
        if minute > current_minute:
            next_restock_minute = minute
            break
    
    # If no valid minute found in current hour, use first minute of next hour
    if next_restock_minute is None:
        next_restock_minute = valid_minutes[0]
        # Calculate seconds until next hour + first restock minute
        wait_time = (60 - current_minute) * 60 - current_second + (next_restock_minute * 60)
    else:
        # Calculate seconds until next restock minute
        wait_time = (next_restock_minute - current_minute) * 60 - current_second
    
    if wait_time > 0:
        wait_minutes = wait_time // 60
        wait_seconds = wait_time % 60
        print(f"⏰ Waiting {wait_minutes}m {wait_seconds}s until next restock time (:{next_restock_minute:02d})")
        time.sleep(wait_time)

def main():
    print(f"🎫 Starting {RESTOCK_INTERVAL_MINUTES}-minute rarity-based restock service...")
    
    # Show valid restock times
    valid_minutes = get_valid_restock_minutes()
    restock_times = [f":{minute:02d}" for minute in valid_minutes]
    print(f"⏰ Restock times: {', '.join(restock_times)} (every {RESTOCK_INTERVAL_MINUTES} minutes)")
    
    print("\n📊 Rarity System:")
    for rarity, config in RARITY_SYSTEM.items():
        emoji = get_rarity_emoji(rarity)
        print(f"  {emoji} {rarity.capitalize()}: {config['weight']}% chance, {config['min_stock']}-{config['max_stock']} tickets")
    
    # Wait for first restock time
    wait_for_next_restock_time()
    
    while True:
        try:
            # Get current time for logging
            now = datetime.now()
            
            # Determine stock amount and rarity
            stock_amount, rarity = determine_stock_amount()
            rarity_emoji = get_rarity_emoji(rarity)
            
            stock_data = {
                "stock": stock_amount,
                "rarity": rarity,
                "restockId": int(time.time()),
                "timestamp": int(time.time())
            }
            
            print(f"\n📦 [{now.strftime('%H:%M:%S')}] {rarity_emoji} {rarity.upper()} RESTOCK: {stock_amount} tickets")
            
            if update_with_http_client(stock_data):
                print(f"✅ Success! {rarity_emoji} {rarity.capitalize()} restock completed")
            else:
                print(f"❌ Failed {rarity_emoji} {rarity.capitalize()} restock")
            
            # Wait for next restock interval
            wait_for_next_restock_time()
            
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            # Still wait for next restock time even if there was an error
            wait_for_next_restock_time()

if __name__ == "__main__":
    main()
