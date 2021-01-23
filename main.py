"""
Please write your name here: Henry Stanton
"""
import csv
import re
import datetime

def breakParser(break_note, start_time):
      print(break_note)

      #Replace "." with ":"
      x = re.sub("\.", ":", break_note)
      print(x)

      x = re.sub("\s", "", x)
      print(x)

      #Slit into list of length 2
      y = re.split("-", x)
      print(y)

      #If 1st string has PM, remove "PM" and add  12 and ":00", if needed
      if re.findall("PM\Z",y[0]):
        y[0] = re.sub("PM", "",y[0])
        temp = re.findall("^(.*?):" ,y[0])
        print(temp)
        if len(temp)>0:
          temp = str(int(temp[0])+12)+":"
          y[0] = re.sub("^(.*?):",temp,y[0])
        else:
          y[0] = str(int(y[0])+12)+":00"  
      print(y)

      #If 2nd string in array has PM, add  12 and ":00"
      if re.findall("PM\Z",y[1]):
        y[1] = re.sub("PM", "",y[1])
        temp = re.findall("^(.*?):" ,y[1])
        print(temp)
        if len(temp)>0:
          temp = str(int(temp[0])+12)+":"
          y[1] = re.sub("^(.*?):",temp,y[1])
        else:
          y[1] = str(int(y[1])+12)+":00"    
      print(y)

      #If 1st string is just digits, add ":00" onto end 
      if (not(re.findall("\D", y[0]))):
        y[0] = y[0] + ":00"
        print(y[0])

      #If 2nd string is just digits, add ":00" onto end 
      if (not(re.findall("\D", y[1]))):
        y[1] = y[1] + ":00"
        print(y[1])

      #Add 12 to 1st string if 2nd string is in 24 hr clock 
      if  int(re.findall("^(.*?):" ,y[0])[0]) <12 and (int(re.findall("^(.*?):" ,y[0])[0])+12) <= int(re.findall("^(.*?):" ,y[1])[0]):
        y[0] = re.sub("^(.*?):", str(int(re.findall("^(.*?):" ,y[0])[0])+12)+":", y[0]) 
        print(y)
      
      #If 2nd string is just digits, add ":00" onto  end and add 12 to make it 24 hr clock
      if (not(re.findall("\D", y[1]))) and int(y[1])<12:
        y[1] = str(int(y[1])+12) + ":00"
        print(y)
      elif not(re.findall("\D", y[1])):
        y[1] += ":00"

      print (y)

      #If 1st string is before start time, add 12
      if int(re.findall("^(.*?):" ,y[0])[0]) < int(re.findall("^(.*?):" ,start_time)[0]):
        y[0] = re.sub("^(.*?):", str(int(re.findall("^(.*?):" ,y[0])[0])+12)+":", y[0])
        y[1] = re.sub("^(.*?):", str(int(re.findall("^(.*?):" ,y[1])[0])+12)+":", y[1]) 
        print(y)
      #Return 2 item list of break start and end times of type string
      return y[0], y[1]


def process_shifts(path_to_csv):
  
  """

    :return: A dictionary with time as key (string) with format %H:%M
        (e.g. "18:00") and cost as value (Number)
    For example, it should be something like :
    {
        "17:00": 50,
        "22:00: 40,
    }
    In other words, for the hour beginning at 17:00, labour cost was
    50 pounds
    :rtype dict:
  """
  shiftsDict = {}
  print('Shifts:\n')
  with open(path_to_csv, newline='') as csvfile:
    shiftsReader = csv.DictReader(csvfile,delimiter=',')

    #For each shift worked, go through each hour and, if worked, add pay amount to corresponding hour in shiftsDict   
    shiftNumber = 1
    for i in shiftsReader:
      print("\nShift number: ", shiftNumber)
      shiftNumber+=1
      hourToAdd = datetime.timedelta(hours = 1)
      startBreak, endBreak = breakParser(i["break_notes"], i["start_time"])
      startBreak = datetime.datetime.strptime(startBreak, "%H:%M")
      endBreak = datetime.datetime.strptime(endBreak, "%H:%M")
      startTime = datetime.datetime.strptime(i["start_time"], "%H:%M")
      endTime = datetime.datetime.strptime(i["end_time"], "%H:%M")
      endTimePlusHr = datetime.datetime.strptime(str(endTime.hour)+":00", "%H:%M")+ hourToAdd
      hourCounter = datetime.datetime.strptime((str(startTime.hour)+":00"), "%H:%M") #Extract hour from start time - allows for start times part way through an hour

      #For a given shift, go through each hour, from start time while it is less than end time + 1hr (to allow for end times that finish part way through hour)
      while hourCounter < endTime :
        print(hourCounter)

        #if hourCounter & end time are same hour and end time is bigger than hour counter, calculate additional time cost. Currency amounts are rounded using int, as examples seemed to use integers
        
        if (hourCounter.hour == endTime.hour) and (endTime > hourCounter):
          print("hourCounter is: ", hourCounter, " & endTime is ", endTime)
          tempMins = (endTime - hourCounter).total_seconds()/60
          tempPay = ((tempMins/60)*(float(i["pay_rate"])*100))/100

          #If hour is already in shiftsDict add data to existing key
          tempKey = str(hourCounter.hour) + ":00" 
          if tempKey in shiftsDict:
            shiftsDict[tempKey] = int(((shiftsDict[tempKey]*100) + (tempPay)*100))/100 
          #Else create new key
          else:
            shiftsDict[tempKey] = int(tempPay)
        
        #If hourCounter is >= end time of break or hourCounter is <= start time of break, add whole hour's pay
        elif hourCounter >= endBreak or (hourCounter + hourToAdd) <= startBreak and not(hourCounter == endTime):
          print("Whole hour's pay added")
          #If hour is already in shiftsDict add data to existing key
          tempKey = str(hourCounter.hour) + ":00" 
          if tempKey in shiftsDict:
            shiftsDict[tempKey] = int(((shiftsDict[tempKey]*100) + (float(i["pay_rate"])*100))/100) 
            print(int(float(i["pay_rate"])), " added")
          #Else create new key
          else:
            shiftsDict[tempKey] = int(float(i["pay_rate"]))
            print(int(float(i["pay_rate"])), " added")
        
        #Else figure out how much to add, if any:
        elif not(hourCounter  == endTime):
          print("partial amount added")
          #Calculate number of minutes of given hour not worked as a break
          tempMins = (((hourCounter+hourToAdd)-endBreak)+(startBreak-hourCounter)).total_seconds()/60
          tempAmount = (((float(i["pay_rate"])*100) / 60) * tempMins)/100
          print("tempAmount added is ", tempAmount)
          #If hour is already in shiftsDict add data to existing key
          tempKey = str(hourCounter.hour) + ":00" 
          if tempKey in shiftsDict:
            shiftsDict[tempKey] = int(((shiftsDict[tempKey]*100) + (tempAmount*100))/100 )
          #Else create new key
          else:
            shiftsDict[tempKey] = int(tempAmount)
  
        hourCounter += hourToAdd

  print(sorted(shiftsDict.items()))
  return shiftsDict


def process_sales(path_to_csv):
  salesDict = {}

  #Open csv file using DictReader to ignore header line
  with open(path_to_csv, newline='') as csvfile:
    transactionsReader = csv.DictReader(csvfile,delimiter=',')
	    
    #Loop over each dictionary returned by transactionsReader
    for i in transactionsReader:
      #if first two chars of i already in salesdict, add value of i to existing value (*100 and then sum to avoid floating point error)
      if (i["time"][:2] + ":00") in salesDict:
        salesDict[i["time"][:2] + ":00"] = ((salesDict[i["time"][:2] + ":00"]*100) + (float(i["amount"])*100))/100
      #Add i and corresponding value to salesDict   
      else: 
        temp = i["time"][:2] + ":00"
        salesDict[temp] = float(i["amount"])

  return salesDict

def compute_percentage(shifts, sales):
    """

    :param shifts:
    :type shifts: dict
    :param sales:
    :type sales: dict
    :return: A dictionary with time as key (string) with format %H:%M and
    percentage of labour cost per sales as value (float),
    If the sales are null, then return -cost instead of percentage
    For example, it should be something like :
    {
        "17:00": 20,
        "22:00": -40,
    }
    :rtype: dict
    """
    return 1

def best_and_worst_hour(percentages):
    """

    Args:
    percentages: output of compute_percentage
    Return: list of strings, the first element should be the best hour,
    the second (and last) element should be the worst hour. Hour are
    represented by string with format %H:%M
    e.g. ["18:00", "20:00"]

    """

    return 1,1

def main(path_to_shifts, path_to_sales):
    """
    Do not touch this function, but you can look at it, to have an idea of
    how your data should interact with each other
    """

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "./transactions.csv"
    path_to_shifts = "./work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)
    print("best_hour is ", best_hour)
    print("worst_hour is ", worst_hour)


# Please write your name here: Henry Stanton
