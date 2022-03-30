from django.apps import AppConfig


class CustomersConfig(AppConfig):
    name = 'customers'
    def ready(self):
        print('Customer ready')
        #import customers.send_smss
        import customers.signals
        import customers.sms_remider, customers.clean_up
        import customers.sms_one_day_remider