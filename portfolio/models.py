from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from urllib.parse import quote


class Profile(models.Model):
    """Single-record profile — all personal + social + section toggles."""

    # ── Personal ──────────────────────────────────────
    name            = models.CharField(max_length=100)
    tagline         = models.CharField(max_length=200)
    bio             = models.TextField()
    profile_image   = models.ImageField(upload_to='uploads/profile/', blank=True, null=True,
                        help_text="Active profile photo shown on the portfolio.")

    # ── Contact ───────────────────────────────────────
    email           = models.EmailField()
    phone           = models.CharField(max_length=25, blank=True,
                        help_text="Include country code, e.g. +91 98765 43210")
    location        = models.CharField(max_length=100, blank=True)

    # ── Social links ──────────────────────────────────
    github_url         = models.URLField(blank=True)
    linkedin_url       = models.URLField(blank=True)
    instagram_username = models.CharField(max_length=60, blank=True,
                           help_text="Instagram handle without @  e.g.  john.doe")
    instagram_user_id  = models.CharField(max_length=30, blank=True,
                           help_text="Numeric Instagram User ID e.g. 123456789 (optional)")

    # ── Profile appearance
    profile_bg_color   = models.CharField(max_length=30, blank=True, default='',
                           help_text="CSS colour behind profile photo e.g. #1e293b. Leave blank for gradient.")

    # ── Resume ────────────────────────────────────────
    resume_file     = models.FileField(upload_to='uploads/resume/', blank=True, null=True)

    # ── Stats ─────────────────────────────────────────
    years_experience  = models.PositiveIntegerField(default=0)
    projects_completed= models.PositiveIntegerField(default=0)
    clients_served    = models.PositiveIntegerField(default=0)

    # ── Section visibility toggles ────────────────────
    show_certificates = models.BooleanField(default=True,
                        help_text="Show the Certificates section on the portfolio")

    class Meta:
        verbose_name        = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.name

    # ── Computed URLs ─────────────────────────────────
    @property
    def whatsapp_url(self):
        if self.phone:
            clean = ''.join(c for c in self.phone if c.isdigit())
            return f"https://wa.me/{clean}"
        return ""

    @property
    def instagram_url(self):
        if self.instagram_username:
            return f"https://instagram.com/{self.instagram_username.lstrip('@')}"
        return ""

    @property
    def mailto_url(self):
        """mailto with pre-filled subject + greeting so clicking opens a ready-to-send email."""
        if not self.email:
            return ""
        subject = quote(f"Hello {self.name} — Let's Connect")
        body    = quote(
            f"Hi {self.name},\n\n"
            "I came across your portfolio and I'd love to connect.\n\n"
            "Best regards,"
        )
        return f"mailto:{self.email}?subject={subject}&body={body}"


class ProfilePhoto(models.Model):
    """Exactly 2 photo slots: HERO (shown in hero section) and ABOUT (shown in About Me)."""
    SLOT_HERO  = 'hero'
    SLOT_ABOUT = 'about'
    SLOT_CHOICES = [
        (SLOT_HERO,  'Hero Section  (circular photo on home page)'),
        (SLOT_ABOUT, 'About Me Section (rectangular photo beside bio)'),
    ]

    profile     = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
    slot        = models.CharField(
                    max_length=10, choices=SLOT_CHOICES, default=SLOT_HERO, unique=False,
                    help_text="Which section this photo appears in.")
    photo       = models.ImageField(upload_to='uploads/profile/gallery/',
                    help_text="Recommended: square (400×400) for Hero, portrait/landscape for About.")
    label       = models.CharField(max_length=60, blank=True,
                    help_text="Optional internal label e.g. 'Professional headshot'")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['slot', '-uploaded_at']
        verbose_name        = "Profile Photo"
        verbose_name_plural = "Profile Photos"
        # Each profile can have at most one photo per slot (enforced in admin too)
        unique_together     = [('profile', 'slot')]

    def __str__(self):
        slot_label = dict(self.SLOT_CHOICES).get(self.slot, self.slot)
        label = f" | {self.label}" if self.label else ""
        return f"{slot_label}{label}"


@receiver(post_save, sender=ProfilePhoto)
def sync_hero_photo(sender, instance, **kwargs):
    """Keep Profile.profile_image in sync with the Hero slot photo."""
    if instance.slot == ProfilePhoto.SLOT_HERO:
        Profile.objects.filter(pk=instance.profile_id).update(profile_image=instance.photo)


# ────────────────────────────────────────────────────────────
class SkillCategory(models.Model):
    name  = models.CharField(max_length=60)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering            = ['order', 'name']
        verbose_name        = "Skill Category"
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    ICON_CHOICES = [
        ('devicon-python-plain',      'Python'),
        ('devicon-javascript-plain',  'JavaScript'),
        ('devicon-typescript-plain',  'TypeScript'),
        ('devicon-react-original',    'React'),
        ('devicon-vuejs-plain',       'Vue.js'),
        ('devicon-django-plain',      'Django'),
        ('devicon-nodejs-plain',      'Node.js'),
        ('devicon-html5-plain',       'HTML5'),
        ('devicon-css3-plain',        'CSS3'),
        ('devicon-postgresql-plain',  'PostgreSQL'),
        ('devicon-mysql-plain',       'MySQL'),
        ('devicon-mongodb-plain',     'MongoDB'),
        ('devicon-docker-plain',      'Docker'),
        ('devicon-git-plain',         'Git'),
        ('devicon-linux-plain',       'Linux'),
        ('devicon-amazonwebservices-plain-wordmark', 'AWS'),
        ('devicon-figma-plain',       'Figma'),
        ('devicon-tailwindcss-plain', 'Tailwind CSS'),
        ('devicon-bootstrap-plain',   'Bootstrap'),
        ('devicon-flutter-plain',     'Flutter'),
        ('devicon-kotlin-plain',      'Kotlin'),
        ('devicon-swift-plain',       'Swift'),
        ('devicon-rust-plain',        'Rust'),
        ('devicon-go-plain',          'Go'),
        ('devicon-redis-plain',       'Redis'),
        ('devicon-graphql-plain',     'GraphQL'),
        ('devicon-nextjs-plain',      'Next.js'),
        ('devicon-nuxtjs-plain',      'Nuxt.js'),
        ('devicon-flask-original',    'Flask'),
        ('devicon-fastapi-plain',     'FastAPI'),
        ('custom',                   'Custom / Other'),
    ]

    category   = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL,
                   null=True, blank=True, related_name='skills')
    name       = models.CharField(max_length=80)
    icon_class = models.CharField(max_length=80, choices=ICON_CHOICES, default='custom')
    proficiency= models.PositiveSmallIntegerField(default=80,
                   validators=[MinValueValidator(1), MaxValueValidator(100)])
    order      = models.PositiveSmallIntegerField(default=0)
    is_featured= models.BooleanField(default=True)

    class Meta:
        ordering            = ['order', 'name']
        verbose_name        = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return f"{self.name} ({self.proficiency}%)"


# ────────────────────────────────────────────────────────────
class Project(models.Model):
    STATUS_CHOICES = [
        ('completed',   'Completed'),
        ('in_progress', 'In Progress'),
        ('archived',    'Archived'),
    ]

    title             = models.CharField(max_length=120)
    slug              = models.SlugField(max_length=140, unique=True)
    short_description = models.CharField(max_length=200)
    description       = models.TextField()
    image             = models.ImageField(upload_to='uploads/projects/', blank=True, null=True)
    tech_stack        = models.CharField(max_length=300, blank=True,
                          help_text="Comma-separated: Django, React, PostgreSQL")
    github_url        = models.URLField(blank=True)
    live_url          = models.URLField(blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    is_featured       = models.BooleanField(default=True)
    order             = models.PositiveSmallIntegerField(default=0)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['order', '-created_at']
        verbose_name        = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    @property
    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()] if self.tech_stack else []


# ────────────────────────────────────────────────────────────
class Certificate(models.Model):
    title          = models.CharField(max_length=150, help_text="Certificate name")
    issuer         = models.CharField(max_length=100, help_text="Organisation that issued it, e.g. Google, Coursera")
    issue_date     = models.DateField(help_text="Date issued")
    expiry_date    = models.DateField(blank=True, null=True, help_text="Leave blank if no expiry")
    credential_id  = models.CharField(max_length=100, blank=True, help_text="Certificate ID / licence number")
    credential_url = models.URLField(blank=True, help_text="Link to verify the certificate")
    image          = models.ImageField(upload_to='uploads/certificates/', blank=True, null=True,
                       help_text="Badge or certificate image (recommended: 400×300 px)")
    description    = models.TextField(blank=True, help_text="Optional: short description of what was covered")
    order          = models.PositiveSmallIntegerField(default=0)
    is_featured    = models.BooleanField(default=True, help_text="Show on portfolio")

    class Meta:
        ordering            = ['order', '-issue_date']
        verbose_name        = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"{self.title} — {self.issuer}"


# ────────────────────────────────────────────────────────────
class Message(models.Model):
    name     = models.CharField(max_length=100)
    email    = models.EmailField()
    subject  = models.CharField(max_length=200)
    message  = models.TextField()
    sent_at  = models.DateTimeField(auto_now_add=True)
    is_read  = models.BooleanField(default=False)

    class Meta:
        ordering            = ['-sent_at']
        verbose_name        = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.sent_at.strftime('%d %b %Y')})"
