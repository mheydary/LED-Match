# LED-Match
A Raspberry PI Game

Author: Mohammadreza Hajy Heydary

Requirements:
  Raspberry PI
  Bread Board
  LEDs and Resistors
  Push Button Switches
  Breakout Board (Optional)
  
External Libraries: gpiozero

How to run:
  python3 LED_game.py
  
For bread boad setup guide, look at the attached pictures in the repository

Basic Rules:
  Push the button once the patterns are matched!
  If you push the button mistakenly, you are out of the game
  If both players push the button mistakenly, a new round shall be started
  If players both push the button when there is a match, check the recorded time
  If a winner is detected, a new round shall be started
  The winner is awarded 100 points
  The pattern change frequency shall be increased by 10
  
