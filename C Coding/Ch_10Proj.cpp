#include <iostream>
using namespace std;
int main() {

    double quiz1, quiz2, midterm, finalExam;
    
    cout << "Enter the score for Quiz 1 (out of 10): ";
    cin >> quiz1;
    cout << "Enter the score for Quiz 2 (out of 10): ";
    cin >> quiz2;
    cout << "Enter the score for Midterm Exam (out of 100): ";
    cin >> midterm;
    cout << "Enter the score for Final Exam (out of 100): ";
    cin >> finalExam;

    double quizAverage = ((quiz1 + quiz2) / 20.0) * 100;

    double overallGrade = (quizAverage * 0.25) + (midterm * 0.25) + (finalExam * 0.50);

    char letterGrade;
    if (overallGrade >= 90) {
        letterGrade = 'A';
    } else if (overallGrade >= 80) {
        letterGrade = 'B';
    } else if (overallGrade >= 70) {
        letterGrade = 'C';
    } else if (overallGrade >= 60) {
        letterGrade = 'D';
    } else {
        letterGrade = 'F';
    }

    cout << "Overall Grade: " << overallGrade << endl;
    cout << "Letter Grade: " << letterGrade << endl;
    
    return 0;
}