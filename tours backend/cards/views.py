from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from avtorizate.models import VerificationCode
from tours.models import Booking
from .models import Card, Category, Transaction
from .serializers import CardSerializer, CategorySerializer, TransactionSerializer, PaymentSerializer


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(from_card__user=self.request.user)
        card_ids = self.request.query_params.getlist('card', None)
        period_start = self.request.query_params.get('start', None)
        period_end = self.request.query_params.get('end', None)
        value_type = self.request.query_params.get('type', None)

        if card_ids:
            queryset = queryset.filter(from_card__id__in=card_ids)
        if period_start and period_end:
            queryset = queryset.filter(datetime__range=[period_start, period_end])
        if value_type == 'income':
            queryset = queryset.filter(value__gt=0)
        elif value_type == 'expense':
            queryset = queryset.filter(value__lt=0)

        return queryset

    def perform_create(self, serializer):
        from_card = get_object_or_404(Card, id=self.request.data.get('from_card'), user=self.request.user)
        to_card = get_object_or_404(Card, id=self.request.data.get('to_card'), user=self.request.user)
        serializer.save(from_card=from_card, to_card=to_card)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def transfer(self, request):
        from_card = get_object_or_404(Card, id=request.data.get('from_card'), user=request.user)
        to_card = get_object_or_404(Card, id=request.data.get('to_card'), user=request.user)
        value = float(request.data.get('value'))
        category_id = request.data.get('category')

        if from_card.balance < value:
            return Response({'error': 'Недостаточно средств на карте'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            from_card.balance -= value
            from_card.save()
            to_card.balance += value
            to_card.save()

            transaction_instance = Transaction.objects.create(
                value=-value,
                from_card=from_card,
                to_card=to_card,
                category_id=category_id
            )

        return Response({'status': 'перевод успешен', 'transaction_id': transaction_instance.id}, status=200)





class PaymentView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request):
        booking = get_object_or_404(Booking, id=request.data.get('booking_id'), user=request.user)
        card = get_object_or_404(Card, id=request.data.get('card_id'), user=request.user)

        if booking.is_paid:
            return Response({"error": "Оплата уже была произведена."}, status=status.HTTP_400_BAD_REQUEST)

        if card.balance < booking.total_price:
            return Response({"error": "Недостаточно средств."}, status=status.HTTP_400_BAD_REQUEST)

        tour_card = get_object_or_404(Card, card_num="777777777777")

        with transaction.atomic():
            card.balance -= booking.total_price
            card.save()
            tour_card.balance += booking.total_price
            tour_card.save()

            Transaction.objects.create(
                value=-booking.total_price,
                from_card=card,
                to_card=tour_card,
                category_id=1
            )


            booking.is_paid = True
            booking.save()

            booking_details = "\n".join([
                f"<strong>Тур:</strong> {booking.tour.name}<br>",
                f"<strong>Дата:</strong> {booking.tour.date}<br>",
                f"<strong>Общее количество людей:</strong> {booking.people_count}<br>",
                f"<strong>Общая стоимость:</strong> {booking.total_price:.2f} сомов"
            ])

            message = f"""
            <html>
                <body>
                    <h2>Ваше бронирование успешно оплачено!</h2>
                    <p>Спасибо за ваш заказ. Мы рады сообщить, что ваша оплата на сумму <strong>{booking.total_price:.2f} $</strong> прошла успешно.</p>
                    <h3>Детали вашего бронирования:</h3>
                    <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
                        {booking_details}
                    </div>
                    <p>Если у вас есть вопросы, не стесняйтесь обращаться к нашей службе поддержки.</p>
                    <p>С уважением,<br>Команда поддержки</p>
                </body>
            </html>
            """

            send_mail(
                subject='Успешная оплата',
                message='Ваш почтовый клиент не поддерживает HTML.',
                html_message=message,
                from_email='agzamovsaid14@gmail.com',
                recipient_list=[request.user.email],
                fail_silently=False,
            )

        return Response({"status": "Оплата прошла успешно"}, status=status.HTTP_200_OK)




