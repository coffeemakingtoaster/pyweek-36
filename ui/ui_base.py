from direct.showbase import DirectObject

from panda3d.core import TextFont 

from os.path import join

class ui_base(DirectObject.DirectObject):
    def __init__(self):
        
        super().__init__()
        
        self.ui_elements = []
        
        self.font: TextFont = loader.loadFont(join("assets","fonts", "VCR_OSD_MONO_1.001.ttf"))
        
    def destroy(self):
        for ui_element in self.ui_elements:
            print("destroying ui element")
            ui_element.destroy()

    def hide(self):
        for ui_element in self.ui_elements:
            print("hiding ui element")
            ui_element.hide()