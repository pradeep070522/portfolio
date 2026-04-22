"""
Management command to populate the database with demo data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from portfolio.models import Profile, SkillCategory, Skill, Project


class Command(BaseCommand):
    help = 'Seeds the database with demo portfolio data'

    def handle(self, *args, **options):
        self.stdout.write('🌱  Seeding database...')

        # ── Profile ───────────────────────────────────────────
        if not Profile.objects.exists():
            Profile.objects.create(
                name='Alex Johnson',
                tagline='Full-Stack Developer & UI/UX Enthusiast crafting elegant, high-performance web experiences.',
                bio=(
                    'I\'m a passionate full-stack developer with over 5 years of experience building '
                    'modern web applications. I specialise in Python/Django on the backend and React '
                    'on the frontend, always with a keen eye for clean design and performance.\n\n'
                    'When I\'m not coding, I contribute to open-source projects, write technical '
                    'articles, and mentor junior developers. I believe great software is equal parts '
                    'engineering rigour and creative vision.\n\n'
                    'I\'m currently open to exciting full-time roles and freelance collaborations. '
                    'Let\'s build something remarkable together!'
                ),
                email='alex@example.com',
                phone='+1 555 000 0000',
                location='San Francisco, CA',
                github_url='https://github.com/',
                linkedin_url='https://linkedin.com/',
                years_experience=5,
                projects_completed=40,
                clients_served=20,
            )
            self.stdout.write(self.style.SUCCESS('  ✔ Profile created'))
        else:
            self.stdout.write('  ⚠  Profile already exists — skipped')

        # ── Skill Categories ──────────────────────────────────
        frontend, _ = SkillCategory.objects.get_or_create(name='Frontend', defaults={'order': 1})
        backend, _  = SkillCategory.objects.get_or_create(name='Backend',  defaults={'order': 2})
        devops, _   = SkillCategory.objects.get_or_create(name='DevOps & Tools', defaults={'order': 3})

        skills_data = [
            # (category, name, icon_class, proficiency, order)
            (frontend, 'React',       'devicon-react-original',      92, 1),
            (frontend, 'TypeScript',  'devicon-typescript-plain',    88, 2),
            (frontend, 'HTML5',       'devicon-html5-plain',         95, 3),
            (frontend, 'CSS3',        'devicon-css3-plain',          90, 4),
            (frontend, 'Tailwind CSS','devicon-tailwindcss-plain',   85, 5),
            (frontend, 'Bootstrap',   'devicon-bootstrap-plain',     88, 6),

            (backend,  'Python',      'devicon-python-plain',        95, 1),
            (backend,  'Django',      'devicon-django-plain',        92, 2),
            (backend,  'FastAPI',     'devicon-fastapi-plain',       80, 3),
            (backend,  'Node.js',     'devicon-nodejs-plain',        78, 4),
            (backend,  'PostgreSQL',  'devicon-postgresql-plain',    85, 5),
            (backend,  'MongoDB',     'devicon-mongodb-plain',       75, 6),

            (devops,   'Docker',      'devicon-docker-plain',        80, 1),
            (devops,   'Git',         'devicon-git-plain',           92, 2),
            (devops,   'Linux',       'devicon-linux-plain',         82, 3),
            (devops,   'AWS',         'devicon-amazonwebservices-plain-wordmark', 70, 4),
        ]

        created = 0
        for cat, name, icon, prof, order in skills_data:
            _, new = Skill.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'icon_class': icon,
                    'proficiency': prof,
                    'order': order,
                    'is_featured': True,
                }
            )
            if new:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✔ {created} skills created'))

        # ── Projects ──────────────────────────────────────────
        projects_data = [
            {
                'title': 'E-Commerce Platform',
                'slug': 'e-commerce-platform',
                'short_description': 'Full-featured online store with real-time inventory and Stripe payments.',
                'description': (
                    'A production-ready e-commerce platform built with Django REST Framework and React. '
                    'Features include real-time inventory management, Stripe payment integration, '
                    'order tracking, and an admin dashboard with analytics.'
                ),
                'tech_stack': 'Django, React, PostgreSQL, Redis, Stripe, Docker',
                'github_url': 'https://github.com/',
                'live_url': 'https://example.com/',
                'status': 'completed',
                'order': 1,
            },
            {
                'title': 'AI Task Manager',
                'slug': 'ai-task-manager',
                'short_description': 'Smart productivity app that uses AI to prioritise and schedule your tasks.',
                'description': (
                    'A Next.js task management application powered by an OpenAI integration that '
                    'automatically categorises, prioritises, and schedules tasks. Includes team '
                    'collaboration, Kanban boards, and productivity analytics.'
                ),
                'tech_stack': 'Next.js, FastAPI, OpenAI, MongoDB, TailwindCSS',
                'github_url': 'https://github.com/',
                'live_url': '',
                'status': 'completed',
                'order': 2,
            },
            {
                'title': 'Real-Time Chat App',
                'slug': 'real-time-chat-app',
                'short_description': 'WebSocket-powered chat with rooms, DMs, file sharing and read receipts.',
                'description': (
                    'A scalable real-time messaging platform using Django Channels and WebSockets. '
                    'Supports public/private rooms, direct messages, file and image sharing, '
                    'read receipts, and push notifications via Firebase.'
                ),
                'tech_stack': 'Django Channels, React, Redis, PostgreSQL, Firebase',
                'github_url': 'https://github.com/',
                'live_url': 'https://example.com/',
                'status': 'completed',
                'order': 3,
            },
            {
                'title': 'DevOps Dashboard',
                'slug': 'devops-dashboard',
                'short_description': 'Centralised monitoring dashboard for Docker containers and cloud resources.',
                'description': (
                    'A unified DevOps dashboard that aggregates metrics from Docker, AWS, and GitHub. '
                    'Provides real-time container health, CI/CD pipeline status, cost monitoring, '
                    'and Slack/email alerting.'
                ),
                'tech_stack': 'Python, FastAPI, React, Docker, AWS SDK, Chart.js',
                'github_url': 'https://github.com/',
                'live_url': '',
                'status': 'in_progress',
                'order': 4,
            },
            {
                'title': 'Portfolio CMS',
                'slug': 'portfolio-cms',
                'short_description': 'This very portfolio — a Django-powered CMS with a dark glassmorphism UI.',
                'description': (
                    'A fully dynamic personal portfolio built with Django. All content is managed '
                    'through the Django admin panel. Features glassmorphism design, scroll animations, '
                    'AJAX contact form, and full mobile responsiveness.'
                ),
                'tech_stack': 'Django, Bootstrap 5, Vanilla JS, SQLite',
                'github_url': 'https://github.com/',
                'live_url': '',
                'status': 'completed',
                'order': 5,
            },
            {
                'title': 'Data Viz Explorer',
                'slug': 'data-viz-explorer',
                'short_description': 'Upload any CSV and get instant interactive charts, stats and insights.',
                'description': (
                    'A browser-based data exploration tool. Upload a CSV file and instantly get '
                    'auto-generated charts, descriptive statistics, correlation matrices, and '
                    'AI-generated natural language summaries of your data.'
                ),
                'tech_stack': 'Python, Pandas, Plotly, Streamlit, OpenAI',
                'github_url': 'https://github.com/',
                'live_url': 'https://example.com/',
                'status': 'completed',
                'order': 6,
            },
        ]

        proj_created = 0
        for data in projects_data:
            _, new = Project.objects.get_or_create(slug=data['slug'], defaults=data)
            if new:
                proj_created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✔ {proj_created} projects created'))
        self.stdout.write(self.style.SUCCESS('\n✅  Done! Visit http://127.0.0.1:8000/ to see your portfolio.'))
        self.stdout.write('   Admin: http://127.0.0.1:8000/admin/')
