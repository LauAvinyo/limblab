
class NavigationController:
    def __init__(self, window):
        self.window = window


    # Navigation Methods
    def navigate_to(self, screen_func):
        if self.window.current_screen is not None:
            self.window.navigation_stack.append(self.window.current_screen)
        self.window.current_screen = screen_func
        screen_func()

    def go_back(self):
        if self.window.navigation_stack:
            previous_screen = self.window.navigation_stack.pop()
            self.window.current_screen = previous_screen
            previous_screen()


    