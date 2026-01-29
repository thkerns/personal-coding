#include <iostream>
#include <string>

int main(){
    std::string name;
    int age;

    std::cout << "Please enter your name: ";

    std::getline(std::cin, name);
    
    std::cout << "Please enter your age: ";
    
    std::cin >> age;
    
    std::cout <<"Hello, " << name << "! You are " << age << " years old." << std::endl;

    return 0;
}