from django.urls import path
from .views import MappingListCreateView, MappingDetailView

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping_list_create'),
    path('<int:identifier>/', MappingDetailView.as_view(), name='mapping_detail'),
    path('patient/<int:identifier>/', MappingDetailView.as_view(), name='mapping_patient_detail'),
]
