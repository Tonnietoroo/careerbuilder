from django.core.management.base import BaseCommand
from documents.models import CVTemplate
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from django.core.files import File

class Command(BaseCommand):
    help = 'Generates preview images for CV templates'

    def handle(self, *args, **kwargs):
        # First ensure the templates exist
        if not CVTemplate.objects.exists():
            self.stdout.write(self.style.WARNING('No templates found. Please run setup_cv_templates first.'))
            return

        templates = [
            {
                'name': 'Professional',
                'bg_color': '#ffffff',
                'accent_color': '#2c3e50',
                'layout': 'two_column'
            },
            {
                'name': 'Creative',
                'bg_color': '#f8f9fa',
                'accent_color': '#e74c3c',
                'layout': 'sidebar'
            },
            {
                'name': 'Minimal',
                'bg_color': '#ffffff',
                'accent_color': '#333333',
                'layout': 'single_column'
            }
        ]

        # Create the directory if it doesn't exist
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'cv_templates', 'previews')
        os.makedirs(preview_dir, exist_ok=True)

        for template_data in templates:
            try:
                # Create a new image
                img = Image.new('RGB', (800, 1000), template_data['bg_color'])
                draw = ImageDraw.Draw(img)

                # Draw template preview based on layout
                if template_data['layout'] == 'two_column':
                    self._draw_professional_preview(draw, template_data)
                elif template_data['layout'] == 'sidebar':
                    self._draw_creative_preview(draw, template_data)
                else:
                    self._draw_minimal_preview(draw, template_data)

                # Save the preview image
                preview_path = os.path.join(preview_dir, f"{template_data['name'].lower()}_preview.jpg")
                img.save(preview_path, 'JPEG', quality=95)

                # Update template in database
                try:
                    template = CVTemplate.objects.get(name=template_data['name'])
                    with open(preview_path, 'rb') as f:
                        template.preview_image.save(
                            f"{template_data['name'].lower()}_preview.jpg",
                            File(f),
                            save=True
                        )
                    self.stdout.write(self.style.SUCCESS(f"Generated preview for {template_data['name']} template"))
                except CVTemplate.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Template {template_data['name']} not found in database"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating preview for {template_data['name']}: {str(e)}"))

    def _draw_professional_preview(self, draw, template_data):
        # Header
        draw.rectangle([0, 0, 800, 150], fill=template_data['accent_color'])
        # Left column
        draw.rectangle([50, 200, 250, 900], fill='#f0f2f5')
        # Right column content blocks
        for y in range(300, 801, 150):
            draw.rectangle([280, y, 750, y+100], fill='#f0f2f5')

    def _draw_creative_preview(self, draw, template_data):
        # Sidebar
        draw.rectangle([0, 0, 300, 1000], fill=template_data['accent_color'])
        # Content blocks with timeline
        for y in range(100, 801, 200):
            # Timeline dot
            draw.ellipse([320, y+25, 340, y+45], fill=template_data['accent_color'])
            # Content block
            draw.rectangle([360, y, 780, y+150], fill='#f0f2f5')

    def _draw_minimal_preview(self, draw, template_data):
        # Header text block
        draw.rectangle([50, 50, 750, 150], fill='#f8f9fa')
        # Content sections
        for y in range(200, 801, 160):
            draw.rectangle([50, y, 750, y+120], fill='#f8f9fa')
            # Section title line
            draw.rectangle([50, y-30, 200, y-10], fill='#e0e0e0') 