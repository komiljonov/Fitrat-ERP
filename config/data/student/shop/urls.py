from .views import (ShopList, ShopDetail, PointsList,
                    PointsDetail, CoinsList, CoinsDetail,
                    ProductsDetail,ProductsList)

from django.urls import path

urlpatterns = [
    path('', ShopList.as_view()),
    path('<uuid:pk>', ShopDetail.as_view()),

    path("points/", PointsList.as_view()),
    path("points/<uuid:pk>", PointsDetail.as_view()),

    path("coins/", CoinsList.as_view()),
    path("coins/<uuid:pk>", CoinsDetail.as_view()),

    path("products/", ProductsList.as_view()),
    path("products/<uuid:pk>", ProductsDetail.as_view()),

]