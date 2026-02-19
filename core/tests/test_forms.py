from django.test import TestCase

from core.forms import ContactForm


class ContactFormTests(TestCase):
    def test_contact_form_valid(self):
        form = ContactForm(
            data={
                "name": "Ion Popescu",
                "email": "ion@example.com",
                "phone": "+40740111222",
                "subject": "Oferta PPF",
                "message": "As dori o oferta pentru protectie front complet.",
                "consent": True,
                "company": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_contact_form_rejects_honeypot(self):
        form = ContactForm(
            data={
                "name": "Ion Popescu",
                "email": "ion@example.com",
                "phone": "+40740111222",
                "subject": "Oferta PPF",
                "message": "Acesta este un mesaj suficient de lung.",
                "consent": True,
                "company": "spam",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("company", form.errors)
