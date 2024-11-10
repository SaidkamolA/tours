from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_email = State()
    waiting_for_password = State()
    awaiting_code = State()


class LoginStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    waiting_for_recovery_email = State()
    waiting_for_verification_code = State()


class TourStates(StatesGroup):
    waiting_for_tour = State()
    waiting_for_child_count = State()
    waiting_for_adult_count = State()
    waiting_for_senior_count = State()


class PaymentStates(StatesGroup):
    waiting_for_payment = State()
    waiting_for_card_details = State()
    confirming_payment = State()
    processing_payment = State()
    payment_successful = State()
    payment_failed = State()


class AddCardStates(StatesGroup):
    waiting_for_card_number = State()
    waiting_for_card_expiry = State()
    waiting_for_card_holder = State()

class ResetPasswordStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_code = State()
    waiting_for_new_password = State()