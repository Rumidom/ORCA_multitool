
char key[3];
struct table {
char s[3];
char c;
};

table Layout[] = {{"EC", 'q'}, {"FC", 'w'},{"ED", 'e'},{"FD", 'r'},{"EK", 't'},{"FK", 'y'},{"EO", 'u'},{"FO", 'i'},{"EP", 'o'},{"FP", 'p'},{"FQ", '«'},{"HQ", '␛'},
                 {"GC", 'a'}, {"HC", 's'},{"GD", 'd'},{"HD", 'f'},{"GK", 'g'},{"HK", 'h'},{"GO", 'j'},{"HO", 'k'},{"GP", 'l'},{"HP", '⌫'},{"GQ", '■'},{"EQ", '§'},
                 {"IC", '⇧'}, {"JC", 'z'},{"ID", 'x'},{"JD", 'c'},{"IK", 'v'},{"JK", 'b'},{"IO", 'n'},{"JO", 'm'},{"IP", '␛'},{"JP", ' '},{"JQ", '»'},{"IQ", '␡'}
};

table Layout_UP[] = {{"EC", 'Q'}, {"FC", 'W'},{"ED", 'E'},{"FD", 'R'},{"EK", 'T'},{"FK", 'Y'},{"EO", 'U'},{"FO", 'I'},{"EP", 'O'},{"FP", 'P'},{"FQ", '«'},{"HQ", '␛'},
                 {"GC", 'A'}, {"HC", 'S'},{"GD", 'D'},{"HD", 'F'},{"GK", 'G'},{"HK", 'H'},{"GO", 'J'},{"HO", 'K'},{"GP", 'L'},{"HP", '⌫'},{"GQ", '■'},{"EQ", '§'},
                 {"IC", '⇧'}, {"JC", 'Z'},{"ID", 'X'},{"JD", 'C'},{"IK", 'V'},{"JK", 'B'},{"IO", 'N'},{"JO", 'M'},{"IP", '?'},{"JP", ' '},{"JQ", '»'},{"IQ", '␡'}
};

table Shift_Layout[] = {{"EC", '0'}, {"FC", '1'},{"ED", '2'},{"FD", '3'},{"EK", '4'},{"FK", '5'},{"EO", '6'},{"FO", '7'},{"EP", '8'},{"FP", '9'},{"FQ", '«'},{"HQ", '␛'},
                       {"GC", '#'}, {"HC", '@'},{"GD", '&'},{"HD", '%'},{"GK", '='},{"HK", '*'},{"GO", '('},{"HO", ')'},{"GP", '/'},{"HP", '⌫'},{"GQ", '■'},{"EQ", '§'},
                       {"IC", '⇧'}, {"JC", '-'},{"ID", '+'},{"JD", 'Ç'},{"IK", '~'},{"JK", ':'},{"IO", '`'},{"JO", '^'},{"IP", '!'},{"JP", ' '},{"JQ", '»'},{"IQ", '␡'}
};

bool Shift_Flag = false;
bool Caps_Flag = false;
bool Bat_Flag = false;
bool toggle_Led = false;
const int Rows [] = {4,5,6,7,8,9};
const int Columns [] = {2,3,10,14,15,16};
const char Alpha [] = {'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q'};
int Shift_LED = 13;
int Caps_LED = 12;
int Bat_LED = 11;
int count = 0;
char TempNumArray[5];
int PressedColumn;
int PressedRow;
char SerialCommand;
// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  //Serial.println("Starting");
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  for (int i : Rows) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  for (int j : Columns) {
    pinMode(j, INPUT);
    digitalWrite(j, LOW);
  }
  delay(100);
  digitalWrite(Bat_LED, HIGH);
  delay(100);
  digitalWrite(Bat_LED, LOW);
  //Serial.println(analogRead(A3));
}

void loop() {
  //Serial.println(analogRead(A3));

  SerialCommand = Serial.read();
  if (SerialCommand == 'O'){Bat_Flag = true;}
  if (SerialCommand == 'F'){Bat_Flag = false;}
  if (SerialCommand == 'R'){Serial.print(String(analogRead(A3), DEC));}
  

  if (Bat_Flag) {
    toggle_Led = !toggle_Led;
    digitalWrite(Bat_LED, toggle_Led);
  }else{
    digitalWrite(Bat_LED, LOW);
  }

  if ((PressedColumn== 0) && (PressedRow == 0)){
    for (int i : Rows) {
      digitalWrite(i, HIGH);
      delay(10);
      for (int j : Columns) {
        if (digitalRead(j)){
          PressedColumn = j;
          PressedRow = i;
          key[0] = Alpha[i];
          key[1] = Alpha[j];
          //Serial.print(key);Serial.print(" row: ");Serial.print(i);Serial.print(" col: ");Serial.println(j);
          if (strcmp(key,"IC") == 0){
            Shift_Flag = !Shift_Flag;
            digitalWrite(13, Shift_Flag);
          }

          if (strcmp(key,"EQ") == 0){
            Caps_Flag = !Caps_Flag;
            digitalWrite(12, Caps_Flag);
          }

          for (int i=0; i!=sizeof(Layout)/sizeof(Layout[0]); ++i){
            if (Shift_Flag){
              if((strcmp(Shift_Layout[i].s,key) == 0)&&(Shift_Flag)){Serial.print(Shift_Layout[i].c);break;}
            }else{
              if (Caps_Flag){
                if((strcmp(Layout_UP[i].s,key) == 0)&&(!Shift_Flag)){Serial.print(Layout_UP[i].c);break;}
              }else{
                if((strcmp(Layout[i].s,key) == 0)&&(!Shift_Flag)){Serial.print(Layout[i].c);break;}
              }
            }
            
          }
        break;
        }
      }
      digitalWrite(i, LOW);
      if (PressedColumn!= 0){break;}
    }
  }else{
    digitalWrite(PressedRow, HIGH);
    if (digitalRead(PressedColumn) == false){
      PressedColumn = 0;
      PressedRow = 0;
      key[0] = '\0';
      digitalWrite(PressedRow, LOW);
    }
  }
}

