#Random Number Generator 
import random

def main():
    count = ask_how_many_numbers()
    length = ask_length_of_numbers()

    while True:
        generate_numbers(count, length)

        while True:
            print("\nWhat would you like to do next?:")
            print("1: Generate again with the same settings")
            print("2: Change number count and length")
            print("3: Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                break
            elif choice == '2':
                count = ask_how_many_numbers()
                length = ask_length_of_numbers()
                break
            elif choice == '3':
                print("Thanks for using the Random Number Generator!")
                return
            else:
                print("Invalid input. Please enter 1, 2, or 3.")
#-------------------------------------------------------
def ask_how_many_numbers():
    while True:
        try:
            count = int(input("How many numbers are we generating 1-10? "))
            if 1 <= count <= 10:
                return count
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
#-------------------------------------------------------
def ask_length_of_numbers():
    while True:
        try:
            length = int(input("What is the length of numbers to generate (1-9)? "))
            if 1 <= length <= 9:
                return length
            else:
                print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
#-------------------------------------------------------
def generate_numbers(count, length):
    print("\nWelcome to the Random Number Generator")
    start = 10**(length - 1)
    end = 10**length - 1

    numbers = [random.randint(start, end) for _ in range(count)]

    print(f"\nGenerated {count} number(s) with length {length}:")
    for i, num in enumerate(numbers, 1):
        print(f" Number {i}: {num}")
#-------------------------------------------------------
if __name__ == "__main__":
    main()
