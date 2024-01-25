String key = "";
struct table {
String s;
char c;
};

table Layout[] = {{"HP", 'Q'}, {"EP", 'W'},{"HM", 'E'},{"EM", 'R'},{"HL", 'T'},{"EL", 'Y'},{"HK", 'U'},{"EK", 'I'},{"HC", 'O'},{"EC", 'P'},{"HD", '«'},
                 {"IP", 'A'}, {"FP", 'S'},{"IM", 'D'},{"FM", 'F'},{"IL", 'G'},{"FL", 'H'},{"IK", 'J'},{"FK", 'K'},{"IC", 'L'},{"FC", '⌫'},{"ID", '■'},
                 {"JP", '⇧'}, {"GP", 'Z'},{"JM", 'X'},{"GM", 'C'},{"JL", 'V'},{"GL", 'B'},{"JK", 'N'},{"GK", 'M'},{"JC", '␛'},{"GC", ' '},{"JD", '»'}
};
table Shift_Layout[] = {{"HP", '0'}, {"EP", '1'},{"HM", '2'},{"EM", '3'},{"HL", '4'},{"EL", '5'},{"HK", '6'},{"EK", '7'},{"HC", '8'},{"EC", '9'},{"HD", '«'},
                       {"IP", '!'}, {"FP", '@'},{"IM", '#'},{"FM", '%'},{"IL", '='},{"FL", '*'},{"IK", '('},{"FK", ')'},{"IC", '/'},{"FC", '⌫'},{"ID", '■'},
                       {"JP", '⇧'}, {"GP", '-'},{"JM", '+'},{"GM", 'Ç'},{"JL", '_'},{"GL", ':'},{"JK", '`'},{"GK", '^'},{"JC", '␛'},{"GC", ' '},{"JD", '»'}
};

boolean Shift_Flag = false;
const int Rows [] = {9,8,7,5,6,5,4};
const int Columns [] = {2,3,10,11,12,15};
const String Alpha [] = {"A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q"};

char TempNumArray[5];
int PressedColumn;
int PressedRow;
// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  Serial.println("Starting");
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(13, OUTPUT);
  for (int i : Rows) {
    pinMode(i, OUTPUT);
  }
  for (int i : Columns) {
    pinMode(i, INPUT);
  }
}

// the loop function runs over and over again forever
void loop() {
  //Serial.println(analogRead(A0));
  
  if ((PressedColumn== 0) && (PressedRow == 0)){

  for (int i : Rows) {
    digitalWrite(i, HIGH);

    for (int j : Columns) {
      if (digitalRead(j)){
      key = Alpha[i]+Alpha[j];
      PressedColumn = j;
      PressedRow = i;
      if (key == "JP"){
        Shift_Flag = !Shift_Flag;
        if (Shift_Flag){
          digitalWrite(13, HIGH);
        }else{
          digitalWrite(13, LOW);
        }
        break;
      }

      for (int i=0; i!=sizeof(Layout)/sizeof(Layout[0]); ++i){
        if (Shift_Flag){
          if((Shift_Layout[i].s == key)&&(Shift_Flag)){Serial.print(Shift_Layout[i].c);break;}
        }else{
          if((Layout[i].s == key)&&(!Shift_Flag)){Serial.print(Layout[i].c);break;}
        }
      }
      break;
      }
    }
    if (PressedRow != 0){break;}
    digitalWrite(i, LOW);
    delay(5);
  }
  }else{
    if (digitalRead(PressedColumn) == false){
      PressedColumn = 0;
      PressedRow = 0;
      digitalWrite(PressedRow, LOW);
    }
  }
}

