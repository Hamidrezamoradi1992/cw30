import django_filters

from .models import File


class FileFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    label = django_filters.CharFilter(method='filter_label')

    def filter_label(self, queryset, name, value):
        """
        Custom filter for JSONField 'label'.
        Assumes label is a JSON object and searches for the value in its keys/values.
        """
        if value:
            return queryset.filter(label__icontains=value)
        return queryset

    class Meta:
        model = File
        fields = ['name', 'category', 'label']
