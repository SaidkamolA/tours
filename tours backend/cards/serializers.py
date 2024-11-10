from rest_framework import serializers

from .models import Card, Category, Transaction

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'user', 'card_num', 'mm_yy', 'balance']
        read_only_fields = ['user', 'balance']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'datetime', 'value', 'from_card', 'to_card', 'category']
class PaymentSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    card_id = serializers.IntegerField()
