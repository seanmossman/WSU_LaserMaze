#include <stdio.h>

// Make integer that stores the "state" of the maze.
// 0 -> Off, 1 -> Easy, 2 -> Medium, 3 -> Hard
int state = 0;
int input = 0;

//Indicate the total number of laser/sensor pairs and enumerate them. Then
// indicate which will be used for each maze setting.
const int numlasers = 11;
const int laslist[numlasers] = {2,3,4,5,6,7,8,9,10,11,12};
const int detlist[numlasers] = {1,2,3,4,5,6,7,8, 9,10,11};
//Indicate which indices in laslist[] are to be used for each maze difficulty
const int easy_lasindex[6] = {1, 3, 4, 5, 9, 10};
const int med_lasindex[8] = {0, 1, 3, 4, 5, 7, 8, 10};
const int hard_lasindex[11] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

int random_lasindex[7] = {0,0,0,0,0, 0,0};

// Determine the number of lasers in each set
const int num_easy_lasers = 6;
const int num_med_lasers = 8;
const int num_hard_lasers = 11;
const int num_random_lasers = 7;

//Indicate the pin wired to the various buttons
const int finishbutton = 21;
int button_state = 0;

// this array will be populated during calibration.  The
// indexing goes as calarray[2i] = sensorpin corresponding to lasindex i and 
// calarray[2i+1] = threshold value for lasindex i.
int calarray[numlasers*2] = {0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0} ;

//Function declaration for auto calibrate
void calibrate(int *cal);

/////////////////////////////////////////////////////////////////////////////////

// the setup routine runs once when you press reset:
void setup() {             
  // initialize Serial and set digital pins to output:
  Serial.begin(9600);

  // set the laser pins to output and make sure they are off to begin with
  for(int i = 0; i < numlasers; i++){
    pinMode(laslist[i], OUTPUT);
    digitalWrite(laslist[i], LOW);
  }
  pinMode(finishbutton, INPUT);

  
  delay(100);
  
  //Make a calibration run
  calibrate( calarray );
  
  //Print calarray for testing
//  Serial.println("calarray = ");
//  for (int i = 0; i < 2*numlasers; i++){
//    Serial.println(calarray[i]);
//  }
  
  //Tell python that the arduino setup is complete
  Serial.write('1');
}
/////////////////////////////////////////////////////////////////////////////////

// the loop routine runs over and over again forever:
void loop() {  
  // Check if finish button is pushed
  button_state = digitalRead(finishbutton);
    
  if(button_state == HIGH && state != 0){
    // If the button has been pushed, write '3' to the
    // serial monitor and turn off the maze.
    Serial.println(3);

    // Delay a little bit, so that maze turning off isn't
    // mistaken for a broken beam.
    delay(100);
    state = 0;
  }
  
  // Code for stopped maze
  if(state == 0){
    maze_off();
  }
  
  // Code for the easy maze
  if(state == 1){
    for (int i = 0; i < num_easy_lasers; i++){
      sensor(analogRead(detlist[calarray[2*easy_lasindex[i]]]), calarray[2*easy_lasindex[i]+1]);
    }
  }

  // Code for the medium maze
  if(state == 2){
    for (int i = 0; i < num_med_lasers; i++){
      sensor(analogRead(detlist[calarray[2*med_lasindex[i]]]), calarray[2*med_lasindex[i]+1]);
    }
  }

  // Code for the hard maze
  if(state == 3){
    for (int i = 0; i < num_hard_lasers; i++){
      sensor(analogRead(detlist[calarray[2*hard_lasindex[i]]]), calarray[2*hard_lasindex[i]+1]);
    }
  }
  
  //Code for random maze
  if(state == 4){
    for (int i = 0; i < num_random_lasers; i++){
      sensor(analogRead(detlist[calarray[2*random_lasindex[i]]]), calarray[2*random_lasindex[i]+1]);
    }
  }

}

// This gets executed at the beginning of every loop.  It reads the Python input from
// serial monitor, and turns on the corresponding maze.  This is written with the
// assumption that the only Python input will be turning on the the maze (0,1,2,3,4} 
// for {cancel, easy, medium, hard, calibrate), and that the arduino won't read it's 
// own input from the serial monitor.
void serialEvent(){
  if (Serial.available()>0){
    input = Serial.read();
  }

  // easy_maze, medium_maze, and hard_maze are defined below
  // easy_maze
  if(input == 49){
    state = 1;
    easy_maze();
    input = 0;
    delay(500);
  }
  
  //medium_maze
  if(input == 50){
    state = 2;
    medium_maze();
    input = 0;
    delay(500);
  }
  
  //hard_maze
  if(input == 51){
    state = 3;
    hard_maze();
    input = 0;
    delay(500);
  }

  //random_maze
  if(input == 52){
    state = 4;
    random_maze();
    input = 0;
    delay(500);
  }
  
  //maze_off
  if(input == 48){
    state = 0;
    input = 0;
    maze_off();
  }
  
  //recalibrate
  if(input == 53){
    state = 5;
    calibrate(calarray);
    input = 0;
    state = 0;
  }
}

void easy_maze(){
  // All off
  for(int i; i < numlasers; i++){
    digitalWrite(laslist[i], LOW);
  }
  // Easy lasers on
  for(int i = 0; i < num_easy_lasers; i++){
    digitalWrite(laslist[easy_lasindex[i]], HIGH);
  }
  return;
}

void medium_maze(){
// All off
  for(int i; i < numlasers; i++){
    digitalWrite(laslist[i], LOW);
  }
  // Medium lasers on
  for(int i = 0; i < num_med_lasers; i++){
    digitalWrite(laslist[med_lasindex[i]], HIGH);
  }
  return;
}
  
void hard_maze(){
  // All off
  for(int i; i < numlasers; i++){
    digitalWrite(laslist[i], LOW);
  }
  // Hard lasers on
  for(int i = 0; i < num_hard_lasers; i++){
    digitalWrite(laslist[hard_lasindex[i]], HIGH);
  }
  return;
}

void random_maze(){
  int j = 0;
  int random_number = 0;
  bool new_random_number = true;
  //Reset the random list to a number not in the laser list
  for(int i = 0; i < num_random_lasers; i++){
    random_lasindex[i] = 15;
  }
  // Choose 7 lasers to turn on from the laslist
  while(j < 7){
    randomSeed(analogRead(0));
    random_number = random(12);
    new_random_number = true;
    for (int i = 0; i<7; i++){
      if(random_number == random_lasindex[i]){
        new_random_number = false;
      }
    }
    if(new_random_number){ 
        random_lasindex[j] = random_number;
        j++; 
    }
  }
  for(int i = 0; i < 7; i++){
    digitalWrite(laslist[random_lasindex[i]], HIGH);
  }
  return;
}   

void maze_off(){
  for(int i; i < numlasers; i++){
    digitalWrite(laslist[i], LOW);
  }
  return;
}

void sensor(int reading, int threshold){
  // Check if beam is broken. If it is,
  // write '2' to serial monitor.
  if(reading < threshold){
    Serial.println(2);
    delay(700);
  }
  return;
}

void calibrate( int *cal){
    // Turn on all the lasers
    for(int i = 0; i < numlasers; i++){
      pinMode(laslist[i], OUTPUT);
      digitalWrite(laslist[i], HIGH);
    }
    //Wait a second for the lasers to warm and settle a bit
    delay(1000);

    // Read and store the detector values with lasers on:
    int detectorValues[numlasers];
    for(int i = 0; i < numlasers; i++){
      detectorValues[i] = analogRead(detlist[i]); 
    }

    delay(100);
    
    // Turn off a laser, find difference in reading -> get threshold. 
    for(int i = 0; i < numlasers; i++){
      // Initialize some local variables that will be handy
      int maxDiff = 0;
      int maxDetectorIndex = 0;

      // We turn off a laser to determine the difference the detector measures
      // when a laser is turned off.
      digitalWrite(laslist[i], LOW);
      delay(500);
      
      // For each detector, we measure the difference in reading when
      // laser is  off vs on and record maximum difference.  The detector that
      // records the maximum difference is the that which the laser is incident
      // upon.
      for(int j = 0; j < numlasers; j++){
        int diff = detectorValues[j] - analogRead(detlist[j]);
        if(diff > maxDiff){
          maxDiff = diff;
          maxDetectorIndex = j;
        }
      }
      delay(100);
      
      // Compute threshold for detector associated with laser `laserNum`
      // If the threshold difference is too small (laser broke or off track) set to zero
      if(abs(maxDiff)<50){
        cal[2*i] = maxDetectorIndex;
        cal[2*i+1] =  0;  
      }
      else{
        cal[2*i] = maxDetectorIndex;
        cal[2*i+1] =  detectorValues[maxDetectorIndex] - maxDiff/2;
      }
      // Turn the laser back on
      digitalWrite(laslist[i], HIGH);
      
//      /*For testing */
//      char testPrint[64];
//      sprintf(testPrint, "Laser: %d, Detector: %d, Min: %d, Max: %d, Threshold: %d \n", laslist[i], detlist[maxDetectorIndex], detectorValues[maxDetectorIndex] - maxDiff, detectorValues[maxDetectorIndex], detectorValues[maxDetectorIndex] - maxDiff/2);
//      Serial.print(testPrint);
    }
    //Turn all the lasers off
    for(int i = 0; i < numlasers; i++){
      digitalWrite(laslist[i], LOW);
    }
    return;
}

