import json

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from order.factories import UserFactory
from product.factories import CategoryFactory, ProductFactory
from product.models import Product


class TestProductViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user = UserFactory()
        token = Token.objects.create(user=self.user)  # added
        token.save()  # added

        self.product = ProductFactory(
            title="pro controller",
            price=200.00,
        )

    def test_get_all_product(self):
        token = Token.objects.get(user__username=self.user.username)  # added
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key)  # added
        response = self.client.get(
            reverse("product-list", kwargs={"version": "v1"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_data = json.loads(response.content)

        self.assertEqual(product_data["results"][0]["title"], self.product.title)
        self.assertEqual(product_data["results"][0]["price"], self.product.price)
        self.assertEqual(product_data["results"][0]["active"], self.product.active)

    def test_create_product(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        category = CategoryFactory()
        
        data = {
            "title": "notebook",
            "price": 800.00,
            "categories_id": [category.id]
        }

        response = self.client.post(
            reverse("product-list", kwargs={"version": "v1"}),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(title="notebook")

        self.assertEqual(product.price, 800.00)
        self.assertEqual(product.category.count(), 1)

        if response.status_code != status.HTTP_201_CREATED:
            print(response.json())