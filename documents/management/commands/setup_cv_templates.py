from django.core.management.base import BaseCommand
from documents.models import CVTemplate
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Sets up CV templates with their CSS files'

    def handle(self, *args, **kwargs):
        # Professional Template
        professional_css = """
            .cv-container.professional {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px;
                font-family: 'Arial', sans-serif;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }

            .professional header {
                text-align: center;
                margin-bottom: 40px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 5px;
            }

            .professional h1 {
                color: #2c3e50;
                margin-bottom: 15px;
            }

            .professional .contact-info {
                display: flex;
                justify-content: center;
                gap: 20px;
                color: #666;
            }

            .professional .main-content {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 40px;
            }

            .professional section {
                margin-bottom: 30px;
            }

            .professional h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }

            .professional .skills-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }

            .professional .skill-item {
                background: #e9ecef;
                padding: 8px 15px;
                border-radius: 20px;
                text-align: center;
            }

            .professional .experience-item {
                margin-bottom: 25px;
            }

            .professional .date {
                color: #666;
                font-style: italic;
            }
        """

        # Creative Template
        creative_css = """
            .cv-container.creative {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0;
                font-family: 'Poppins', sans-serif;
                display: grid;
                grid-template-columns: 300px 1fr;
                background: #fff;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }

            .creative .sidebar {
                background: #2c3e50;
                color: white;
                padding: 40px;
            }

            .creative .main-content {
                padding: 40px;
            }

            .creative .profile-image {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                margin: 0 auto 20px;
                border: 3px solid #fff;
            }

            .creative .contact-info {
                margin-bottom: 30px;
            }

            .creative .section-title {
                color: #3498db;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }

            .creative .timeline-item {
                position: relative;
                padding-left: 30px;
                margin-bottom: 30px;
            }

            .creative .timeline-item::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #3498db;
            }
        """

        # Minimal Template
        minimal_css = """
            .cv-container.minimal {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                font-family: 'Playfair Display', serif;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
            }

            .minimal header {
                text-align: center;
                margin-bottom: 60px;
            }

            .minimal h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .minimal .section-title {
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #2c3e50;
            }

            .minimal .divider {
                width: 50px;
                height: 2px;
                background: #2c3e50;
                margin: 30px auto;
            }

            .minimal section {
                margin-bottom: 40px;
            }

            .minimal .experience-item,
            .minimal .education-item {
                margin-bottom: 30px;
            }
        """

        # Create or update templates
        templates = [
            {
                'name': 'Professional',
                'description': 'A clean and professional template perfect for corporate roles.',
                'css': professional_css
            },
            {
                'name': 'Creative',
                'description': 'A modern and creative template ideal for design and creative roles.',
                'css': creative_css
            },
            {
                'name': 'Minimal',
                'description': 'A simple and elegant template that focuses on content.',
                'css': minimal_css
            }
        ]

        for template_data in templates:
            template, created = CVTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'is_active': True
                }
            )

            # Save CSS content
            css_content = ContentFile(template_data['css'].strip())
            template.css_template.save(
                f"{template_data['name'].lower()}.css",
                css_content,
                save=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} template: {template.name}"
                )
            ) 