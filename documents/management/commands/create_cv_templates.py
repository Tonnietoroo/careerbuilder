from django.core.management.base import BaseCommand
from documents.models import CVTemplate
from django.core.files import File
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Creates default CV templates'

    def handle(self, *args, **kwargs):
        templates = [
            {
                'name': 'Professional',
                'description': 'A clean and professional template perfect for corporate roles.',
                'preview': 'professional.jpg',
                'html': 'professional.html',
                'css': 'professional.css'
            },
            {
                'name': 'Creative',
                'description': 'A modern and creative template ideal for design and creative roles.',
                'preview': 'creative.jpg',
                'html': 'creative.html',
                'css': 'creative.css'
            },
            {
                'name': 'Minimal',
                'description': 'A simple and elegant template that focuses on content.',
                'preview': 'minimal.jpg',
                'html': 'minimal.html',
                'css': 'minimal.css'
            },
        ]

        for template in templates:
            CVTemplate.objects.get_or_create(
                name=template['name'],
                defaults={
                    'description': template['description'],
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created CV templates')) 