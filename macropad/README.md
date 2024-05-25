# LiveWires Macro Pad

## Own a macro pad? Start here!

Well done for building your macro pad! Here's where you can find all the information you need to start programming it yourself.

## How it works

The macro pad runs on a Raspberry Pi Pico. If you plug in the macro pad to a computer, it should do two things. Firstly, it'll act as the macro pad it's supposed to! Secondly, it should also act as a tiny memory stick, creating a new drive on your computer that you can browse the files on.

This contains two files - code.py and keys.py - plus a couple of folders.

Unless you're a Python wizard, we recommend you don't touch the folders, or code.py. These are what makes it all work as it should and you risk breaking things/

However, keys.py is where you can tell the macro pad which buttons do what. So this is the one to edit. You should be able to open it in your favourite text editor, make changes, save them and then unplug and plug back in the macro pad. However there's an easier way...

## Using Thonny

This isn't strictly required, but it is highly recommended. The best software we've found to edit the macro pad code is called Thonny. You should be able to download and install it from here: https://thonny.org/

Once installed, it should have a button in the bottom right corner that you can click to choose the option that mentions Circuit Python. On a Windows machine it probably says something like "CircuitPython (generic)  **·** COM3". Click that one.

Once you've done that, you can press File -> Open, and open the keys.py file that's on the device. 

Thonny will highlight the different bits of the code in different colours, which should help you understand the changes you want to make. 

Once you've made the changes to the file, press save. To run the new code immediately, you should just be able to press the red "stop" sign followed by the green "play" sign in the top bar of the Thonny window.

## Troubleshooting

That should be all you need. If you get stuck, feel free to get in touch with a leader, or post an issue here on github. 

If you've bricked your macropad by changing something, don't worry, it should be easy to fix. Just download the contents of the "code" folder in github and copy it across to the device. 

## 


