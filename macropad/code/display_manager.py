import board
import busio
import adafruit_ssd1306

class DisplayManager:
    def __init__(self):
        i2c = busio.I2C(board.GP1, board.GP0)
        self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        
    def set_loading_bar(self, n):
        '''n should be between 0 and 128'''
        self.disp.fill_rect(0, 25, n, 31, 1)
        self.disp.show()
        
    def show_splash_screen(self):
        self.disp.fill(0)
        self.disp.text("LiveWires MacroPad", 0, 0, 1)
        self.disp.text("Loading...!", 10, 10, 1)
        self.set_loading_bar(1)
        self.disp.show()
        
    def centre_aligned_text(self, text, y):
        chars = len(text)
        # Assumes fixed width text of 5 px per char, plus 1 px separator
        width_pixels = 6 * chars - 1
        # Screen is 64 pixels wide
        offset = 64 - (width_pixels // 2)
        self.disp.text(text, offset, y, 1)
        
    def show_page(self, page):
        self.disp.fill(0)
        self.centre_aligned_text(page.name, 0)
        key_names = page.get_key_names()
        self.disp.text(key_names[0], 0, 10, 1)
        self.disp.text(key_names[1], 32, 10, 1)
        self.disp.text(key_names[2], 64, 10, 1)
        self.disp.text(key_names[3], 96, 10, 1)
        self.disp.text(key_names[4], 0, 20, 1)
        self.disp.text(key_names[5], 32, 20, 1)
        self.disp.text(key_names[6], 64, 20, 1)
        self.disp.text(key_names[7], 96, 20, 1)
        self.disp.show()
        


