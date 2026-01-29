#include <iostream>
#include <sstream>
#include <map>
#include <cctype>
#include <vector>
#include <algorithm>

void countWordsAndLetters(const std::string& inputLine) {
    std::string normalizedLine;
    for (char ch : inputLine) {
        normalizedLine += std::tolower(ch);
    }

    std::istringstream stream(normalizedLine);
    std::string word;
    int wordCount = 0;
    std::map<char, int> letterCount;

    while (stream >> word) {
        wordCount++;

        for (char ch : word) {
            if (std::isalpha(ch)) {
                letterCount[ch]++;
            }
        }
    }

    std::vector<std::pair<char, int>> sortedLetters(letterCount.begin(), letterCount.end());
    std::sort(sortedLetters.begin(), sortedLetters.end());

    std::cout << wordCount << " words" << std::endl;
    for (const auto& pair : sortedLetters) {
        std::cout << pair.second << " " << pair.first << std::endl;
    }
}

int main() {
    std::string inputLine;
    std::cout << "Enter a line of text: ";
    std::getline(std::cin, inputLine);
    
    countWordsAndLetters(inputLine);
    
    return 0;
}