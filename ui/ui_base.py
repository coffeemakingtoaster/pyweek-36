class ui_base:
    def __init__(self):
        self.ui_elements = []

    def destroy(self):
        for ui_element in self.ui_elements:
            print("destroying ui element")
            ui_element.destroy()

    def hide(self):
        for ui_element in self.ui_elements:
            print("hiding ui element")
            ui_element.hide()