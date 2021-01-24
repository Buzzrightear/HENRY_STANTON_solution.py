"""
Please write your name here: Henry Stanton
"""
import csv
import re
import datetime

def breakParser(break_note, start_time):
      #Replace "." with ":"
      x = re.sub("\.", ":", break_note)
      x = re.sub("\s", "", x)
      #Split into list of length 2
      y = re.split("-", x)
     
      #If 1st string has PM, remove "PM" and add  12 and ":00", if needed
      if re.findall("PM\Z",y[0]):
        y[0] = re.sub("PM", "",y[0])
        temp = re.findall("^(.*?):" ,y[0])
        if len(temp)>0:
          temp = str(int(temp[0])+12)+":"
          y[0] = re.sub("^(.*?):",temp,y[0])
        else:
          y[0] = str(int(y[0])+12)+":00"  

      #If 2nd string in array has PM, add  12 and ":00"
      if re.findall("PM\Z",y[1]):
        y[1] = re.sub("PM", "",y[1])
        temp = re.findall("^(.*?):" ,y[1])
        if len(temp)>0:
          temp = str(int(temp[0])+12)+":"
          y[1] = re.sub("^(.*?):",temp,y[1])
        else:
          y[1] = str(int(y[1])+12)+":00"    

      #If 1st string is just digits, add ":00" onto end 
      if (not(re.findall("\D", y[0]))):
        y[0] = y[0] + ":00"

      #If 2nd string is just digits, add ":00" onto end 
      if (not(re.findall("\D", y[1]))):
        y[1] = y[1] + ":00"

      #Add 12 to 1st string if 2nd string is in 24 hr clock 
      if  int(re.findall("^(.*?):" ,y[0])[0]) <12 and (int(re.findall("^(.*?):" ,y[0])[0])+12) <= int(re.findall("^(.*?):" ,y[1])[0]):
        y[0] = re.sub("^(.*?):", str(int(re.findall("^(.*?):" ,y[0])[0])+12)+":", y[0]) 
      
      #If 2nd string is just digits, add ":00" onto  end and add 12 to make it 24 hr clock
      if (not(re.findall("\D", y[1]))) and int(y[1])<12:
        y[1] = str(int(y[1])+12) + ":00"
      elif not(re.findall("\D", y[1])):
        y[1] += ":00"

      #If 1st string is before start time, add 12
      if int(re.findall("^(.*?):" ,y[0])[0]) < int(re.findall("^(.*?):" ,start_time)[0]):
        y[0] = re.sub("^(.*?):", str(int(re.findall("^(.*?):" ,y[0])[0])+12)+":", y[0])
        y[1] = re.sub("^(.*?):", str(int(re.findall("^(.*?):" ,y[1])[0])+12)+":", y[1]) 

      #Return 2 item list of break start and end times of type string
      return y[0], y[1]


def process_shifts(path_to_csv):
  shiftsDict = {}
  
  with open(path_to_csv, newline='') as csvfile:
    shiftsReader = csv.DictReader(csvfile,delimiter=',')
    shiftNumber = 1

    #For each shift worked, go through each hour and, if worked, add pay amount to corresponding hour in shiftsDict   
    for i in shiftsReader:
      shiftNumber+=1
      hourToAdd = datetime.timedelta(hours = 1)
      startBreak, endBreak = breakParser(i["break_notes"], i["start_time"])
      startBreak = datetime.datetime.strptime(startBreak, "%H:%M")
      endBreak = datetime.datetime.strptime(endBreak, "%H:%M")
      startTime = datetime.datetime.strptime(i["start_time"], "%H:%M")
      endTime = datetime.datetime.strptime(i["end_time"], "%H:%M")
      hourCounter = datetime.datetime.strptime((str(startTime.hour)+":00"), "%H:%M") #Extract hour from start time - allows for start times part way through an hour

      #For a given shift, go through each hour, from start time while it is less than end time + 1hr (to allow for end times that finish part way through hour)
      while hourCounter < endTime :
        #If end time is not just at the end of the hour but is instead some time after e.g. half ten: if hourCounter & end time are same hour and end time is bigger than hour counter, calculate additional time cost. Currency amounts are rounded using int, as examples seemed to use integers      
        if (hourCounter.hour == endTime.hour) and (endTime > hourCounter):
          tempMins = (endTime - hourCounter).total_seconds()/60
          tempPay = ((tempMins/60)*(float(i["pay_rate"])*100))/100

          #If hour is already in shiftsDict add data to existing key
          tempKey = str(hourCounter.hour) + ":00" 
          if tempKey in shiftsDict:
            shiftsDict[tempKey] = round(((shiftsDict[tempKey]*100) + (tempPay)*100))/100 
          #Else create new key
          else:
            shiftsDict[tempKey] = round(tempPay)
        
        #Else if hourCounter is not during a break: if hourCounter >= end time of break or hourCounter is <= start time of break, add whole hour's pay
        elif hourCounter >= endBreak or (hourCounter + hourToAdd) <= startBreak and not(hourCounter == endTime):
          #If hour is already in shiftsDict add data to existing key
          tempKey = str(hourCounter.hour) + ":00" 
          if tempKey in shiftsDict:
            shiftsDict[tempKey] = round(((shiftsDict[tempKey]*100) + (float(i["pay_rate"])*100))/100) 
          #Else create new key
          else:
            shiftsDict[tempKey] = round(float(i["pay_rate"]))
        
        #Else it must be during a break, so figure out how much to add, if any:
        else:
          #Calculate number of minutes of given hour not worked as a break
          tempMins = (max(0,((hourCounter+hourToAdd)-endBreak).total_seconds()/60)+max(0,(startBreak-hourCounter).total_seconds()/60))
          tempAmount = (((float(i["pay_rate"])*100) / 60) * tempMins)/100

          #If hour is already in shiftsDict add data to existing key
          tempKey = str(hourCounter.hour) + ":00" 
          if tempKey in shiftsDict:
            shiftsDict[tempKey] = round(((shiftsDict[tempKey]*100) + (tempAmount*100))/100 )
          #Else create new key
          else:
            shiftsDict[tempKey] = round(tempAmount)
  
        hourCounter += hourToAdd

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
    percentagesDict = {}
    
    #For each key in shifts dict, if the key doesn't exist in sales, subtract the sales value from 0, else divide shifts dict value for i by the sales dict value for i and multiply by 100
    for i in sorted(shifts):
      if not(i in sales):
        percentagesDict[i] = round(0.00 - shifts[i], 2)
      else:
        percentagesDict[i] = round((shifts[i]/sales[i])*100, 2)
    
    return percentagesDict

def best_and_worst_hour(percentages):
    bestAndWorstList = ["",""]
    maxValue = 0
    maxValueKey = ""
    minValue = 0 
    minValueKey = ""

    #Find worst hour (highest value) and corresponding key
    for i in percentages:
      if percentages[i] > maxValue:
        maxValue = percentages[i]
        maxValueKey = i

    #Best hour (min value above zero) and corresponding key
    minValue = maxValue
    minValueKey = maxValueKey
    for i in percentages:
      if percentages[i] < minValue and percentages[i] >0:
        minValue = percentages[i]
        minValueKey = i
    
    bestAndWorstList[0] = minValueKey
    bestAndWorstList[1] = maxValueKey

    return bestAndWorstList

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
