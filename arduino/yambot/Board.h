#ifndef BOARD_H
#define BOARD_H
#include <Arduino.h>

enum Column {
  DOLJE,
  GORE,
  SVUGDJE,
  NAJAVA
};

enum Row {
  ONES,
  TWOS,
  THREES,
  FOURS,
  FIVES,
  SIXES,
  MAX,
  MIN,
  DVAPARA,
  TRIS,
  SKALA,
  FULL,
  POKER,
  YAMB,
};

class Board {
  public:
    Board();
    bool isFeasible(Row r, Column c); // DOES NOT MUTATE check if we can place something in a particular place on the grid
    byte scoreAt(Row r, byte* countArray); // DOES NOT MUTATE computes the score at a particular row based on a particular count array
    bool update(Row r, Column c, byte* countArray); // DOES MUTATE update the board at the specified index, ASSUMING it is valid
  private:
    int doljeIdx; // which element are we due next to fill in the dolje column
    int goreIdx; // which element are we due next to fill in the gore column
    byte matrix[14][4]; // this matrix will store our scores in yamb. 0 means we scored zero points or crossed it out. 255 means we are yet to fill it out
    byte computeSum(byte* countArray);
    bool isDvaPara(byte* countArray); // need to define this
    bool isTris(byte* countArray); // need to define this
    bool isSkala(byte* countArray); // need to define this
    bool isFull(byte* countArray); // need to define this
    bool isPoker(byte* countArray); // need to define this
    bool isYamb(byte* countArray); // need to define this
};

#endif