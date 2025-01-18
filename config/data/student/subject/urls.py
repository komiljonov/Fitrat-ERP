from django.urls import path

from .views import (SubjectList,SubjectNoPG,SubjectDetail,
                    LevelList,LevelDetail,LevelNoPG,
                    ThemeList,ThemeDetail,ThemeNoPG)


urlpatterns = [
    path('', SubjectList.as_view(), name='subject-list'),
    path('<uuid:pk>/', SubjectDetail.as_view(), name='subject-detail'),
    path('no-pg/', SubjectNoPG.as_view(), name='subject-no-pg'),

    path('level/', LevelList.as_view(), name='level-list'),
    path('level/<uuid:pk>/', LevelDetail.as_view(), name='level-detail'),
    path('level/no-pg/', LevelNoPG.as_view(), name='level-nopg'),

    path('theme/', ThemeList.as_view(), name='theme-list'),
    path('theme/<uuid:pk>/', ThemeDetail.as_view(), name='theme-detail'),
    path('theme/no-pg/', ThemeNoPG.as_view(), name='theme-nopg'),

]