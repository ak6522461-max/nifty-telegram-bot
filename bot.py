from datetime import 
import pandas as pd
now = datetime.now()

# Market hours: Monday-Friday, 9:15 AM to 3:30 PM
if now.weekday() >= 5:
    exit()

if not ((now.hour > 9 or (now.hour == 9 and now.minute >= 15)) and
        (now.hour < 15 or (now.hour == 15 and now.minute <= 30))):
    exit()