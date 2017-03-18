  void setup() {
  // put your setup code here, to run once: 
  int num = 11;
  int laslist[num] = {2,3,4,5,6, 7,8,9,10,11,12}; 
  for (int i = 0; i < num; i++){
    pinMode(laslist[i], OUTPUT);
    digitalWrite(laslist[i], HIGH);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
