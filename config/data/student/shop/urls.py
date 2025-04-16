from .views import (PurchaseList, PurchaseDetail, PointsList,
                    PointsDetail, CoinsList, CoinsDetail,
                    ProductsDetail, ProductsList, PointToCoinExchangeApiView, CategoryList, CategoryDetail)

from django.urls import path

urlpatterns = [
    path('', PurchaseList.as_view()),
    path('<uuid:pk>', PurchaseDetail.as_view()),

    path("points/", PointsList.as_view()),
    path("points/<uuid:user_id>", PointsDetail.as_view()),

    path("coins/", CoinsList.as_view()),
    path("coins/<uuid:user_id>", CoinsDetail.as_view()),

    path("products/", ProductsList.as_view()),
    path("products/<uuid:pk>", ProductsDetail.as_view()),

    path("categories/", CategoryList.as_view()),
    path("categories/<uuid:pk>", CategoryDetail.as_view()),

    path("exchange/", PointToCoinExchangeApiView.as_view()),

]