from common.decorators import login_not_required


class LoginNotRequiredMixin:

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return login_not_required(view_func=view)
