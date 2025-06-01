import re 
import pandas as pd
def preprocess(data):
    arr = data.split("\n")
    dates = []
    users = []
    msgs = []
    # times= []

    pattern = r"^(\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2}) - ([^:]+): (.+)$"
    pattern2 = r"^(\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2}) - (.+)$"

    for i in arr:
       match = re.match(pattern, i)
       match2 = re.match(pattern2, i)
       if match :
         date  , user , msg = match.groups()
         dates.append(date)
         users.append(user)
         msgs.append(msg)
         
       elif match2 :
         date , msg = match2.groups()
         dates.append(date)
         users.append("system")
         msgs.append(msg)
        
    df = pd.DataFrame({'date - time': dates, "user": users, "msg":msgs})
    df['date - time'] = pd.to_datetime(df['date - time'])
    df[["date","month" , "day" ,  "day_name" , "week" , "year" ,"time" , "hour" , "minutes"]] = df['date - time'].apply(getDateTime)
    df = df[df["user"]!= "system"]
    df = df[df["user"]!= "Meta AI"]
    
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = period
          
    return df
    

def getDateTime(date):
  datee = date.date()
  time = date.time()
  day = date.day
  week = date.week
  day_name = date.day_name()
  month = date.month_name()
  year = date.year
  hours = date.hour
  minutes = date.minute
  return pd.Series([datee,month , day , day_name, week , year , time , hours, minutes])