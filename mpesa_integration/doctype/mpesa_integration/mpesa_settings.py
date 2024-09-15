import frappe
from frappe.model.document import Document
from mpesa_integration.mpesa_settings.mpesa_connector import MpesaConnector

class MpesaSettings(Document):
    def on_update(self):
        self.setup_mpesa_payment_gateway()

    def setup_mpesa_payment_gateway(self):
        from payments.utils import create_payment_gateway
        create_payment_gateway("Mpesa", "Mpesa Settings", "Mpesa")

        # Create Mode of Payment
        self.create_mpesa_mode_of_payment()

    def create_mpesa_mode_of_payment(self):
        if not frappe.db.exists("Mode of Payment", "Mpesa"):
            mode_of_payment = frappe.get_doc({
                "doctype": "Mode of Payment",
                "mode_of_payment": "Mpesa",
                "type": "Bank",
                "enabled": 1,
                "accounts": [
                    {
                        "company": frappe.defaults.get_user_default("company"),
                        "default_account": frappe.db.get_value(
                            "Payment Gateway Account", {"payment_gateway": "Mpesa"}, "payment_account"
                        )
                    }
                ]
            })
            mode_of_payment.insert(ignore_permissions=True)

    @frappe.whitelist()
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        mpesa_connector = MpesaConnector(
            env=self.sandbox,
            consumer_key=self.consumer_key,
            consumer_secret=self.get_password("consumer_secret"),
            business_shortcode=self.business_shortcode,
            online_passkey=self.get_password("online_passkey"),
            till_number=self.till_number
        )
        response = mpesa_connector.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc
        )
        return response

    @frappe.whitelist(allow_guest=True)
    def verify_transaction(self, **kwargs):
        transaction_response = frappe._dict(kwargs["Body"]["stkCallback"])
        checkout_id = transaction_response.get("CheckoutRequestID")
        integration_request = frappe.get_doc("Integration Request", checkout_id)
        integration_request.update_status(transaction_response)
        # Implement logic to handle the payment status

    def get_payment_url(self):
        base_url = "https://api.safaricom.co.ke/mpesa"
        params = {
            "BusinessShortCode": self.business_shortcode,
            "TillNumber": self.till_number,
            "TransactionLimit": self.transaction_limit,
        }
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        payment_url = f"{base_url}/processpayment?{query_string}"
        return payment_url
