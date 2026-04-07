from ui.widgets import CustomDropdown
class AnimationMixin:
    def transition_to_page(self, page_function, *args):
        if self.transitioning:
            return
        self.transitioning = True
        CustomDropdown.close_all()
        page_function(*args)
        self.root.update_idletasks()
        self.transitioning = False