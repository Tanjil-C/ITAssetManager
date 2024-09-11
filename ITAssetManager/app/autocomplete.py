
from .autocomplete import autocomplete
from .models import Equipment

class EquipmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Equipment.objects.none()

        qs = Equipment.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
