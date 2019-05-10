#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =================================================================================================================
# Author: Mohammadreza Hajy Heydary
# =================================================================================================================
import random
import time
import threading
from gpiozero import LEDBoard, Button, RGBLED
# =================================================================================================================
random.seed(time.time())
SCORE_INCREMENT = 100
# =================================================================================================================
class LEDGame:
    def __init__(self):
        self.__player1_score = 0
        self.__player2_score = 0
        self.__winning_seq = None
        self.__switch_freq = 32
        self.__level = 0
        # is the winning sequence displayed already?
        self.__isDisplayed = False
        # have they pressed the switch when they should not have?
        self.__user1_false_press = False
        self.__user2_false_press = False
        # has the user casted input and the time casted
        self.__user1_true_press = False
        self.__user2_true_press = False
        self.__user1_time_pushed = -1
        self.__user2_time_pushed = -1
        # loop flag
        self.__push_button1 = False
        self.__push_button2 = False
        self.__disp_loop = False
        # winning sequence LEDs handler
        self.__winning_led_handle = LEDBoard(18, 23, 24, 25, pwm=True)
        self.__starting_light_handle = RGBLED(red=6, green=13, blue=19)
        self.__pattern_light_handle = LEDBoard(4, 17, 27, 22, pwm=True)

    def __del__(self):
        # turn all the LEDs off before terminating
        self.__winning_led_handle.off()
        self.__starting_light_handle.off()
        self.__pattern_light_handle.off()

    @staticmethod
    def __pattern_generator():
        # generate a pattern of behaviors for 4 LEDs and save the results in a dictionary
        sequence = '{:0>4b}'.format(random.randint(1, 15))
        return {'B': int(sequence[0]), 'R': int(sequence[1]), 'Y': int(sequence[2]), 'G': int(sequence[3])}

    def __starting_light(self):
        # set color to red
        self.__starting_light_handle.color = (0.1, 0, 0)
        time.sleep(1)
        # yellow
        self.__starting_light_handle.color = (0.1, 0.08, 0)
        time.sleep(1)
        # green
        self.__starting_light_handle.color = (0, 0.05, 0)
        time.sleep(0.5)
        # turn the led off
        self.__starting_light_handle.off()

    def __show_winning_seq(self):
        # show the winning sequence and adjust the brightness of LEDs
        self.__winning_led_handle.value = (
            0.2 * self.__winning_seq['G'], 0.2 * self.__winning_seq['Y']/2,
            0.05 * self.__winning_seq['R']/2, 0.05 * self.__winning_seq['B']/2
        )

    def __show_patterns(self):
        # continuously generate a pattern and show it on the respective LEDs
        while self.__disp_loop:
            self.__isDisplayed = False
            seq = self.__pattern_generator()
            # reduce the brightness of LEDs with constant multiplies
            self.__pattern_light_handle.value = (0.2 * seq['G'], 0.2 * seq['Y']/2, 0.05 * seq['R']/2, 0.05 * seq['B']/2)

            if seq == self.__winning_seq:
                self.__isDisplayed = True

            time.sleep(60/self.__switch_freq)
            self.__pattern_light_handle.off()

    def __switch1(self):
        button = Button(5)
        while self.__push_button1:
            if button.is_pressed:
                timer1 = time.time()
                if not self.__isDisplayed:
                    self.__user1_false_press = True
                    # no more input is allowed for this user
                    print("False push by User 1")
                    return

                else:
                    self.__user1_time_pushed = timer1
                    self.__user1_true_press = True
                    # no more input is allowed for this user
                    print("Matched push by User 1")
                    return

    def __switch2(self):
        button = Button(12)
        while self.__push_button2:
            if button.is_pressed:
                timer2 = time.time()
                if not self.__isDisplayed:
                    self.__user2_false_press = True
                    # no more input is allowed for this user
                    print("False push by User 2")
                    return

                else:
                    self.__user2_time_pushed = timer2
                    self.__user2_true_press = True
                    # no more input is allowed for this user
                    print("Matched push by User 2")
                    return

    def __no_winner_state(self):
        print("No winner detected. ")
        self.__level -= 1

    def __find_winner(self):
        if self.__user1_time_pushed < self.__user2_true_press:
            self.__user1_won()
        elif self.__user1_time_pushed > self.__user2_time_pushed:
            self.__user2_won()
        else:
            self.__no_winner_state()

    def __user1_won(self):
        print("User one has won the game!")
        self.__player1_score += SCORE_INCREMENT

    def __user2_won(self):
        print("User two has won the game!")
        self.__player2_score += SCORE_INCREMENT

    def start_game(self):
        # set the flags
        self.__isDisplayed = False
        self.__user1_false_press = False
        self.__user2_false_press = False
        self.__user1_true_press = False
        self.__user2_true_press = False
        self.__push_button1 = True
        self.__push_button2 = True
        self.__disp_loop = True
        # set variables
        self.__level += 1
        self.__switch_freq += 10

        # create three threads 1 for each user and one for the
        disp_thread = threading.Thread(target=self.__show_patterns)
        disp_thread.daemon = True
        user1_thread = threading.Thread(target=self.__switch1)
        user1_thread.daemon = True
        user2_thread = threading.Thread(target=self.__switch2)
        user2_thread.daemon = True

        # generate a sequence
        self.__winning_seq = self.__pattern_generator()
        self.__show_winning_seq()

        # show the starting light
        self.__starting_light()

        # start the thread
        disp_thread.start()
        user1_thread.start()
        user2_thread.start()

        while True:
            if self.__user1_false_press and self.__user2_false_press:
                # no winner case scenario
                self.__push_button1 = False
                self.__push_button2 = False
                self.__disp_loop = False
                # wait for the threads to join
                disp_thread.join()
                user1_thread.join()
                user2_thread.join()
                # take the necessary actions for this state
                self.__no_winner_state()
                break

            if self.__user1_true_press and self.__user2_true_press:
                # close push scenario
                self.__push_button1 = False
                self.__push_button2 = False
                self.__disp_loop = False
                # wait for the threads to join
                disp_thread.join()
                user1_thread.join()
                user2_thread.join()
                # take the necessary action for this state
                self.__find_winner()
                break

            if self.__user1_true_press or self.__user2_true_press:
                # end all the spinning loops
                self.__disp_loop = False
                self.__push_button1 = False
                self.__push_button2 = False
                # wait for them to arrive
                disp_thread.join()
                user1_thread.join()
                user2_thread.join()

                if self.__user1_true_press:
                    self.__user1_won()

                elif self.__user2_true_press:
                    self.__user2_won()

                else:
                    print("Error in the winner detection system.")
                    exit(1)

                break

    def show_score(self):
        print("********************** Scores Table ************************")
        print("PLAYER 1: {}".format(self.__player1_score))
        print("PLAYER 2: {}".format(self.__player2_score))

    def get_level(self):
        return self.__level

def main():
    led_game = LEDGame()
    print("LED Game Started! Press CTR + C to quit")
    while True:
        try:
            led_game.show_score()
            print("********************** level {} ************************".format(led_game.get_level()))
            print("Press the button once the patterns matched!")
            led_game.start_game()
            print("\nStarting a new round...")
            time.sleep(1)
            print('\n')

        except KeyboardInterrupt:
            print('\n')
            led_game.show_score()
            print("Goodbye.")
            break


if __name__ == '__main__': main()
