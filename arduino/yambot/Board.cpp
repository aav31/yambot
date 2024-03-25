#include "Board.h"

Board::Board() {
  for (int c=DOLJE; c <= NAJAVA ; c++) {
    for (int r=ONES; r <= YAMB; r++) {
      matrix[r][c] = 255; // 255 will tell us that this square has not been used yet
    }
  }
  doljeIdx = 0;
  goreIdx = 13;
}

bool Board::isFeasible(Row r, Column c) {
  // make sure we're trying to fill out a square which is in bounds
  if ( (r > YAMB) || (c > NAJAVA) ) {
    return false;
  }

  // we can't fill out something we have already filled out
  if ( matrix[r][c] != 255 ) {
    return false;
  }

  // we can only fill out the dolje and gore columns in order
  if ((c == DOLJE) && (r != doljeIdx)) {
    return false;
  }
  if ((c == GORE) && (r != goreIdx)) {
    return false;
  }
  
  return true;
}

bool Board::update(Row r, Column c, byte *countArray) {
  if (!isFeasible(r, c)) {
    return false;
  }
  matrix[r][c] = scoreAt(r, countArray);
  if (c == DOLJE) {
    doljeIdx++;
  }
  if (c == GORE) {
    goreIdx--;
  }
  return true;
}

byte Board::scoreAt(Row r, byte* countArray) {
  byte s = 0;
  switch (r) {
    case ONES:
      return 1 * countArray[1];
      break;
    case TWOS:
      return 2 * countArray[2];
      break;
    case THREES:
      return 3 * countArray[3];
      break;
    case FOURS:
      return 4 * countArray[4];
      break;
    case FIVES:
      return 5 * countArray[5];
      break;
    case SIXES:
      return 6 * countArray[6];
      break;
    case MAX:
      return computeSum(countArray);
      break;
    case MIN:
      return computeSum(countArray);
      break;
    case DVAPARA:
      if (isDvaPara(countArray)) {
        for (byte faceValue=1; faceValue<=6; faceValue++) {
          if (countArray[faceValue] >= 2) {
            s += faceValue * 2;
          }
        }
        return s + 10;
      } else {
        return 0;
      }
      break;
    case TRIS:
      if (isTris(countArray)) {
        for (byte faceValue=1; faceValue<=6; faceValue++) {
          if (countArray[faceValue] >= 3) {
            s += faceValue * 3;
          }
        }
        return s + 20;
      } else {
        return 0;
      }
      break;
    case SKALA:
      if (isSkala(countArray)) {
        // check if skala is mala or velika
        if (computeSum(countArray) == 15) {
          return 45;
        } else {
          return 50;
        }
      } else {
        return 0;
      }
      break;
    case FULL:
      if (isFull(countArray)) {
        return computeSum(countArray) + 40;
      } else {
        return 0;
      }
      break;
    case POKER:
      if (isPoker(countArray)) {
        for (byte faceValue=1; faceValue<=6; faceValue++) {
          if (countArray[faceValue] >= 4) {
            s += faceValue * 4;
          }
        }
        return s + 50;
      } else {
        return 0;
      }
      break;
    case YAMB:
      if (isYamb(countArray)) {
        return computeSum(countArray) + 60;
      } else {
        return 0;
      }
      break;
  }
}

byte Board::computeSum(byte* countArray) {
  byte s = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    s += faceValue * countArray[faceValue];
  }
  return s;
}

bool Board::isDvaPara(byte* countArray) {
  byte numPairs = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    if (countArray[faceValue] >= 2) {
      numPairs++;
    }
  }
  return (numPairs==2);
}

bool Board::isTris(byte* countArray) {
  byte numTriplets = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    if (countArray[faceValue] >= 3) {
      numTriplets++;
    }
  }
  return (numTriplets==1);
}

bool Board::isSkala(byte* countArray) {
  byte numSinglets = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    if (countArray[faceValue]==1) {
      numSinglets++;
    }
  }
  return (numSinglets==5);
}

bool Board::isFull(byte* countArray) {
  byte numPairs = 0;
  byte numTriplets = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    if (countArray[faceValue] == 2) {
      numPairs++;
    }
    if (countArray[faceValue] == 3) {
      numTriplets++;
    }
  }
  return ((numPairs == 1) && (numTriplets == 1));
}

bool Board::isPoker(byte* countArray) {
  byte numQuadruplets = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    if (countArray[faceValue] >= 4) {
      numQuadruplets++;
    }
  }
  return (numQuadruplets==1);
}

bool Board::isYamb(byte* countArray) {
  byte numQuintuplets = 0;
  for (byte faceValue=1; faceValue<=6; faceValue++) {
    if (countArray[faceValue] >= 5) {
      numQuintuplets++;
    }
  }
  return (numQuintuplets==1);
}
