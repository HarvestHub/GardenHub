from django.contrib.auth.mixins import UserPassesTestMixin


class UserCanEditGardenMixin(UserPassesTestMixin):
    """
    Only a user who can edit this Garden may access this.
    """
    def test_func(self):
        return self.request.user.can_edit_garden(self.get_object())


class UserCanEditPlotMixin(UserPassesTestMixin):
    """
    Only a user who can edit this Plot may access this.
    """
    def test_func(self):
        return self.request.user.can_edit_plot(self.get_object())
