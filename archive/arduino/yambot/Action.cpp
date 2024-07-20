#include "Action.h"

String actionToString(Action a, bool canRoll, bool canAnnounce, bool canFillIn) {
  String str = "";
  if (canRoll) {
    str += "onesToKeep: ";
    str += String(a.onesToKeep);
    str += ", twosToKeep: ";
    str += String(a.twosToKeep);
    str += ", threesToKeep: ";
    str += String(a.threesToKeep);
    str += ", foursToKeep: ";
    str += String(a.foursToKeep);
    str += ", fivesToKeep: ";
    str += String(a.fivesToKeep);
    str += ", sixesToKeep: ";
    str += String(a.sixesToKeep);
  }
  if (canAnnounce) {
    str += ", announce: ";
    str += String(a.announce);
    str += ", announcementRow: ";
    str += String(a.announcementRow);
  }
  if (canFillIn) {
    str += "rowToFillIn: ";
    str += String(Board::convertRowToCharArray(a.rowToFillIn));
    str += ", colToFillIn: ";
    str += String(Board::convertColToCharArray(a.colToFillIn));
  }
  return str;
}

bool isValid(Action a, byte* countArray, byte rollNumber, Board& b, bool announced, Row announcedRow, bool canRoll, bool canAnnounce, bool canFillIn) {
  // if you can roll some of your dice, check that the dice you're rolling are valid
  if (canRoll) {
    if ((a.onesToKeep>countArray[1]) || (a.twosToKeep>countArray[2]) || (a.threesToKeep>countArray[3]) || (a.foursToKeep>countArray[4]) || (a.fivesToKeep>countArray[5]) || (a.sixesToKeep>countArray[6])) {
      Serial.println("The number of dice you keep must be less than or equal to the number of dice you have.");
      return false;
    }
    if ((a.onesToKeep<0) || (a.twosToKeep<0) || (a.threesToKeep<0) || (a.foursToKeep<0) || (a.fivesToKeep<0) || (a.sixesToKeep<0)) {
      Serial.println("The number of dice you keep must be greater than or equal to zero.");
      return false;
    }
  }

  // if you can't announce this variable cannot be set to be true
  if ((!canAnnounce) && (a.announce)) {
    Serial.println("You cannot announce on this turn.");
    return false;
  }

  // if you announce but the announcement row is not feasible - this isnt valid
  Row unusedParameter = 0;
  if ((a.announce) && (!b.isFeasible(a.announcementRow, NAJAVA, false, unusedParameter))) {
    Serial.println("You announced an unfeasible grid square.");
    return false;
  }

  // if you can fill stuff in, check it's valid
  if ( (canFillIn) && (!b.isFeasible(a.rowToFillIn, a.colToFillIn, announced, announcedRow)) ) {
    Serial.println("You are trying to fill out an unfeasable grid square.");
    Serial.println(actionToString(a, canRoll, canAnnounce, canFillIn));
    return false;
  }

  return true;
}