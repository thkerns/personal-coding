#Alarm Clock
import time
import datetime

def main():
    print("Welcome to the Python Alarm Clock!")
    print("Choose an option:")
    print("1. Set alarm for a specific time (e.g., 08:00:00)")
    print("2. Set a timer (e.g., in seconds)")
    
    choice = input("Enter 1 or 2: ")
    
    if choice == '1':
        target_time_str = input("Enter the time in HH:MM:SS format (e.g., 08:00:00): ")
        
        try:
            now = datetime.datetime.now()
            target_time = datetime.datetime.strptime(target_time_str, "%H:%M:%S")
            target_datetime = now.replace(hour=target_time.hour, minute=target_time.minute, second=target_time.second, microsecond=0)
            
            if target_datetime > now:
                wait_seconds = (target_datetime - now).total_seconds()
                print(f"Alarm set for {target_time_str}. Waiting for {wait_seconds} seconds...")
                time.sleep(wait_seconds)
                trigger_alarm()
            else:
                print("The specified time is in the past. Please try again.")
        except ValueError:
            print("Invalid time format. Please use HH:MM:SS.")
    
    elif choice == '2':
        try:
            duration_seconds = float(input("Enter the duration in seconds (e.g., 300 for 5 minutes): "))
            if duration_seconds > 0:
                print(f"Timer set for {duration_seconds} seconds...")
                time.sleep(duration_seconds)
                trigger_alarm()
            else:
                print("Duration must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    else:
        print("Invalid choice. Please run the program again and enter 1 or 2.")

def trigger_alarm():
    print("Alarm is going off! Wake up!")
    for _ in range(3):
        print("\a")
        time.sleep(0.5)

if __name__ == "__main__":
    main()