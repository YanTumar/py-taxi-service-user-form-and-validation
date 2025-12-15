from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth import get_user_model

from taxi.forms import CarForm, DriverCreationForm, DriverLicenseUpdateForm
from taxi.models import Manufacturer, Car


def index(request):
    """View function for the home page of the site."""
    num_drivers = get_user_model().objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return generic.TemplateView.as_view(template_name="taxi/index.html",
                                        extra_context=context)(request)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 5


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 5
    queryset = Car.objects.all().select_related("manufacturer")


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()
        user = self.request.user
        context["is_driver"] = user in car.drivers.all()
        return context


class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


@login_required
def assign_driver_to_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    user = request.user

    if user in car.drivers.all():
        car.drivers.remove(user)
    else:
        car.drivers.add(user)

    return HttpResponseRedirect(reverse("taxi:car-detail", args=[pk]))


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()


class DriverCreateView(generic.CreateView):
    model = get_user_model()
    form_class = DriverCreationForm


class DriverLicenseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = DriverLicenseUpdateForm
    template_name = "taxi/driver_license_update.html"
    success_url = reverse_lazy("taxi:driver-list")

    def get_success_url(self):
        return reverse_lazy("taxi:driver-detail",
                            kwargs={"pk": self.object.pk})


class DriverDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = get_user_model()
    success_url = reverse_lazy("taxi:driver-list")
