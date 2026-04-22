from django.contrib import admin
from django.contrib import messages as django_messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.shortcuts import get_object_or_404
from .models import Profile, ProfilePhoto, Skill, SkillCategory, Project, Certificate, Message


# ═══════════════════════════════════════════════════════════════
# Profile Photo — 2 named slots: Hero + About Me
# ═══════════════════════════════════════════════════════════════
@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display        = ('_big_thumb', '_slot_badge', 'label', 'uploaded_at', '_action_buttons')
    list_display_links  = None
    ordering            = ('slot', '-uploaded_at')
    list_per_page       = 10
    readonly_fields     = ('uploaded_at', '_preview_large', '_slot_hint')

    fieldsets = (
        ('Photo Slot', {
            'description': (
                '<strong>Hero Photo</strong> — circular photo in the top hero banner.<br>'
                '<strong>About Me Photo</strong> — rectangular photo next to your bio.'
                '<br><br>You can upload <strong>one photo per slot</strong> (2 total). '
                'Delete an existing slot to replace it.'
            ),
            'fields': ('profile', 'slot', '_slot_hint', '_preview_large', 'photo', 'label'),
        }),
        ('Timestamps', {'fields': ('uploaded_at',), 'classes': ('collapse',)}),
    )

    # ── Slot hint ───────────────────────────────────────────────
    def _slot_hint(self, obj):
        hints = {
            'hero':  '📐 Square crop recommended (400×400 px). Will appear circular on the portfolio.',
            'about': '🖼 Landscape or portrait works well (500×600 px). Shown rectangular with rounded corners.',
        }
        if obj and obj.slot:
            return mark_safe(f'<p style="color:#555;font-size:12px;margin:4px 0 0;">{hints.get(obj.slot,"")}</p>')
        return ''
    _slot_hint.short_description = ''

    # ── Large preview in edit ───────────────────────────────────
    def _preview_large(self, obj):
        if obj.pk and obj.photo:
            radius = '50%' if (obj.slot == ProfilePhoto.SLOT_HERO) else '12px'
            return format_html(
                '<img src="{}" style="width:180px;height:180px;object-fit:cover;'
                'border-radius:{};border:3px solid #6366f1;box-shadow:0 4px 20px rgba(0,0,0,.15);" />',
                obj.photo.url, radius,
            )
        return mark_safe('<span style="color:#888;">Not saved yet.</span>')
    _preview_large.short_description = 'Current Photo'

    # ── Thumbnail in list ───────────────────────────────────────
    def _big_thumb(self, obj):
        if obj.photo:
            radius = '50%' if obj.slot == ProfilePhoto.SLOT_HERO else '8px'
            return format_html(
                '<img src="{}" style="width:70px;height:70px;object-fit:cover;'
                'border-radius:{};border:2px solid #6366f1;" />',
                obj.photo.url, radius,
            )
        return '—'
    _big_thumb.short_description = 'Photo'

    # ── Slot badge ──────────────────────────────────────────────
    def _slot_badge(self, obj):
        if obj.slot == ProfilePhoto.SLOT_HERO:
            return mark_safe(
                '<span style="padding:4px 12px;background:#dbeafe;color:#1d4ed8;'
                'border-radius:20px;font-size:12px;font-weight:700;">🏠 Hero</span>'
            )
        return mark_safe(
            '<span style="padding:4px 12px;background:#f3e8ff;color:#7c3aed;'
            'border-radius:20px;font-size:12px;font-weight:700;">👤 About Me</span>'
        )
    _slot_badge.short_description = 'Section'

    # ── Delete button ───────────────────────────────────────────
    def _action_buttons(self, obj):
        delete_url = reverse('admin:portfolio_profilephoto_quick_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" style="display:inline-block;padding:5px 14px;background:#fee2e2;'
            'color:#dc2626;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none;"'
            ' onclick="return confirm(\'Delete this photo?\')">✕ Delete</a>',
            delete_url,
        )
    _action_buttons.short_description = 'Actions'

    # ── Custom quick-delete URL ─────────────────────────────────
    def get_urls(self):
        return [
            path('<int:pk>/quick-delete/',
                 self.admin_site.admin_view(self._quick_delete_view),
                 name='portfolio_profilephoto_quick_delete'),
        ] + super().get_urls()

    def _quick_delete_view(self, request, pk):
        photo = get_object_or_404(ProfilePhoto, pk=pk)
        label = photo.label or dict(ProfilePhoto.SLOT_CHOICES).get(photo.slot, f'Photo #{pk}')
        if photo.slot == ProfilePhoto.SLOT_HERO:
            Profile.objects.filter(pk=photo.profile_id).update(profile_image=None)
        photo.photo.delete(save=False)
        photo.delete()
        django_messages.success(request, f'🗑 "{label}" deleted. You can now upload a new photo for that slot.')
        return HttpResponseRedirect(reverse('admin:portfolio_profilephoto_changelist'))

    # ── Only allow adding if a slot is still free ───────────────
    def has_add_permission(self, request):
        if not Profile.objects.exists():
            return False
        profile = Profile.objects.first()
        used_slots = set(profile.photos.values_list('slot', flat=True))
        return len(used_slots) < 2   # still has a free slot

    def save_model(self, request, obj, form, change):
        if not change:
            profile = Profile.objects.first()
            if profile and profile.photos.filter(slot=obj.slot).exists():
                django_messages.error(
                    request,
                    f'❌ A photo for the "{obj.get_slot_display()}" slot already exists. '
                    'Delete it first, then upload a new one.'
                )
                return
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        profile    = Profile.objects.first()
        used_slots = set(profile.photos.values_list('slot', flat=True)) if profile else set()
        all_slots  = {ProfilePhoto.SLOT_HERO, ProfilePhoto.SLOT_ABOUT}
        free_slots = all_slots - used_slots
        slot_labels = dict(ProfilePhoto.SLOT_CHOICES)
        notices = []
        if free_slots:
            free_names = ' and '.join(f'<strong>{slot_labels[s]}</strong>' for s in free_slots)
            notices.append(f'📷 Free slot(s): {free_names}. Click "Add Profile Photo" to upload.')
        else:
            notices.append('✅ Both photo slots (Hero + About Me) are filled. Delete one to replace it.')
        extra_context = extra_context or {}
        extra_context['slot_notices'] = notices
        return super().changelist_view(request, extra_context=extra_context)


# ═══════════════════════════════════════════════════════════════
# Profile Photo Inline (inside Profile edit page)
# ═══════════════════════════════════════════════════════════════
class ProfilePhotoInline(admin.TabularInline):
    model           = ProfilePhoto
    extra           = 0
    max_num         = 2
    fields          = ('_thumb', 'slot', 'photo', 'label')
    readonly_fields = ('_thumb',)
    verbose_name        = 'Profile Photo'
    verbose_name_plural = 'Profile Photos — Hero & About Me (max 2)'
    can_delete      = True

    def _thumb(self, obj):
        if obj.pk and obj.photo:
            radius = '50%' if obj.slot == ProfilePhoto.SLOT_HERO else '8px'
            return format_html(
                '<img src="{}" style="width:60px;height:60px;object-fit:cover;'
                'border-radius:{};border:2px solid #6366f1;" />',
                obj.photo.url, radius,
            )
        return '—'
    _thumb.short_description = 'Preview'


# ═══════════════════════════════════════════════════════════════
# Profile
# ═══════════════════════════════════════════════════════════════
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfilePhotoInline]

    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'tagline', 'bio', '_photo_summary'),
        }),
        ('Contact Details', {'fields': ('email', 'phone', 'location')}),
        ('Social Links', {
            'description': 'Instagram username shown as @handle. User ID (numeric) is optional.',
            'fields': ('github_url', 'linkedin_url',
                       'instagram_username', 'instagram_user_id', '_instagram_info'),
        }),
        ('Profile Appearance', {
            'description': 'CSS colour behind the circular hero photo. E.g. #1e293b or rgba(0,212,255,0.15). Leave blank for default.',
            'fields': ('profile_bg_color',),
        }),
        ('Stats', {'fields': ('years_experience', 'projects_completed', 'clients_served')}),
        ('Resume / CV', {
            'description': 'Upload PDF — a "View Resume" button appears on the portfolio.',
            'fields': ('_resume_preview', 'resume_file'),
        }),
        ('Section Visibility', {
            'description': 'Toggle entire sections on/off on the public portfolio.',
            'fields': ('show_certificates',),
        }),
    )
    readonly_fields = ('_photo_summary', '_resume_preview', '_instagram_info')

    def _photo_summary(self, obj):
        if not obj.pk:
            return mark_safe('<span style="color:#888;">Save first, then add photos via the inline below.</span>')
        manage_url = reverse('admin:portfolio_profilephoto_changelist')
        parts = [
            f'<a href="{manage_url}" style="display:inline-block;margin-bottom:8px;'
            f'font-size:12px;color:#4f46e5;">📷 Manage Profile Photos →</a><br>'
        ]
        photos = obj.photos.all()
        if not photos:
            parts.append('<span style="color:#888;font-size:12px;">No photos uploaded yet. Use the section below.</span>')
        for p in photos:
            radius = '50%' if p.slot == ProfilePhoto.SLOT_HERO else '10px'
            slot_label = dict(ProfilePhoto.SLOT_CHOICES).get(p.slot, p.slot)
            parts.append(
                f'<div style="display:inline-flex;align-items:center;gap:10px;margin-right:16px;">'
                f'<img src="{p.photo.url}" style="width:70px;height:70px;object-fit:cover;'
                f'border-radius:{radius};border:3px solid #6366f1;" />'
                f'<div><strong style="font-size:12px;">{slot_label}</strong>'
                f'<br><span style="color:#888;font-size:11px;">{p.label or "No label"}</span></div>'
                f'</div>'
            )
        return mark_safe(''.join(parts))
    _photo_summary.short_description = 'Profile Photos'

    def _resume_preview(self, obj):
        if obj.pk and obj.resume_file:
            filename = obj.resume_file.name.split('/')[-1]
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;'
                'gap:6px;padding:7px 16px;background:#1a73e8;color:#fff;border-radius:6px;'
                'text-decoration:none;font-size:13px;font-weight:600;">'
                '📄 View Current Resume</a>'
                '<p style="margin:6px 0 0;color:#666;font-size:12px;">{}</p>',
                obj.resume_file.url, filename,
            )
        return mark_safe('<span style="color:#888;">No resume uploaded yet.</span>')
    _resume_preview.short_description = 'Current Resume'

    def _instagram_info(self, obj):
        if not obj.pk:
            return mark_safe('<span style="color:#888;">Save first.</span>')
        parts = []
        if obj.instagram_username:
            parts.append(format_html(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;'
                'gap:6px;padding:6px 14px;'
                'background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366);'
                'color:#fff;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;">'
                '📸 @{}</a>', obj.instagram_url, obj.instagram_username,
            ))
        if obj.instagram_user_id:
            parts.append(format_html(
                '<span style="display:inline-block;margin-top:4px;padding:4px 10px;'
                'background:#f3f4f6;border-radius:4px;font-size:12px;color:#374151;">'
                'User ID: <strong>{}</strong></span>', obj.instagram_user_id,
            ))
        if not parts:
            return mark_safe('<span style="color:#888;">No Instagram set yet.</span>')
        return mark_safe(
            '<div style="display:flex;flex-direction:column;gap:6px;">'
            + ''.join(str(p) for p in parts) + '</div>'
        )
    _instagram_info.short_description = 'Instagram Preview'

    def has_add_permission(self, request):
        return not Profile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════
# Skill Category
# ═══════════════════════════════════════════════════════════════
@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'skill_count')
    ordering     = ('order', 'name')

    def skill_count(self, obj):
        return obj.skills.count()
    skill_count.short_description = '# Skills'


# ═══════════════════════════════════════════════════════════════
# Skill
# ═══════════════════════════════════════════════════════════════
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display  = ('_skill_icon_preview', 'name', 'category', '_bar', 'proficiency', 'order', 'is_featured')
    list_editable = ('proficiency', 'order', 'is_featured')
    list_filter   = ('category', 'is_featured')
    search_fields = ('name',)
    ordering      = ('order', 'name')
    list_per_page = 30
    actions       = ['make_featured', 'make_hidden']

    fieldsets = (
        (None, {
            'fields': ('name', 'icon_class', 'category', 'proficiency', 'order', 'is_featured')
        }),
    )

    def _skill_icon_preview(self, obj):
        if obj.icon_class and obj.icon_class != 'custom':
            return format_html(
                '<i class="{}" style="font-size:24px;"></i>',
                obj.icon_class,
            )
        initial = obj.name[0].upper() if obj.name else '?'
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:26px;height:26px;background:linear-gradient(135deg,#6366f1,#8b5cf6);'
            'color:#fff;border-radius:6px;font-size:13px;font-weight:700;">{}</span>',
            initial,
        )
    _skill_icon_preview.short_description = ''

    def _bar(self, obj):
        pct   = obj.proficiency
        color = '#22c55e' if pct >= 80 else '#f59e0b' if pct >= 50 else '#ef4444'
        return format_html(
            '<div style="width:110px;background:#e5e7eb;border-radius:4px;height:10px;overflow:hidden;">'
            '<div style="width:{}%;background:{};height:10px;border-radius:4px;"></div></div>',
            pct, color,
        )
    _bar.short_description = 'Level'

    @admin.action(description='✅ Show selected skills on portfolio')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='🚫 Hide selected skills from portfolio')
    def make_hidden(self, request, queryset):
        queryset.update(is_featured=False)


# ═══════════════════════════════════════════════════════════════
# Project
# ═══════════════════════════════════════════════════════════════
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display       = ('title', 'status', 'is_featured', 'order', 'created_at')
    list_editable      = ('is_featured', 'order', 'status')
    list_filter        = ('status', 'is_featured')
    search_fields      = ('title', 'description', 'tech_stack')
    prepopulated_fields= {'slug': ('title',)}
    readonly_fields    = ('_image_preview', 'created_at', 'updated_at')
    list_per_page      = 20

    fieldsets = (
        ('Project Info', {'fields': ('title', 'slug', 'short_description', 'description', '_image_preview', 'image')}),
        ('Technical Details', {'fields': ('tech_stack', 'status')}),
        ('Links',             {'fields': ('github_url', 'live_url')}),
        ('Display Settings',  {'fields': ('is_featured', 'order')}),
        ('Timestamps',        {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def _image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-width:320px;max-height:180px;object-fit:cover;border-radius:8px;border:1px solid #ddd;" />',
                obj.image.url,
            )
        return mark_safe('<span style="color:#888;">No image yet.</span>')
    _image_preview.short_description = 'Image Preview'


# ═══════════════════════════════════════════════════════════════
# Certificate — full add / delete / toggle visibility
# ═══════════════════════════════════════════════════════════════
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display       = ('_badge_thumb', 'title', 'issuer', 'issue_date', '_expiry_col', 'order', '_visible_toggle')
    list_display_links = ('title',)
    list_editable      = ('order',)
    list_filter        = ('issuer', 'is_featured')
    search_fields      = ('title', 'issuer', 'credential_id')
    ordering           = ('order', '-issue_date')
    readonly_fields    = ('_cert_preview', '_visibility_note')
    list_per_page      = 20
    actions            = ['make_visible', 'make_hidden']

    fieldsets = (
        ('Certificate Details', {
            'fields': ('title', 'issuer', 'issue_date', 'expiry_date', 'credential_id', 'description'),
        }),
        ('Image / Badge', {'fields': ('_cert_preview', 'image')}),
        ('Verification Link', {'fields': ('credential_url',)}),
        ('Display Settings', {
            'description': 'Control whether this certificate appears on the public portfolio.',
            'fields': ('order', 'is_featured', '_visibility_note'),
        }),
    )

    def _badge_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:52px;height:40px;object-fit:cover;border-radius:6px;border:1px solid #e5e7eb;" />',
                obj.image.url,
            )
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:52px;height:40px;background:linear-gradient(135deg,#e0e7ff,#ede9fe);border-radius:6px;font-size:18px;">🏅</span>'
        )
    _badge_thumb.short_description = ''

    def _expiry_col(self, obj):
        if obj.expiry_date:
            return format_html('<span style="color:#f59e0b;font-size:12px;">⏱ {}</span>', obj.expiry_date.strftime('%b %Y'))
        return format_html('<span style="color:#9ca3af;font-size:12px;">No expiry</span>')
    _expiry_col.short_description = 'Expires'

    def _visible_toggle(self, obj):
        url = reverse('admin:portfolio_certificate_toggle_visibility', args=[obj.pk])
        if obj.is_featured:
            return format_html(
                '<a href="{}" title="Click to hide" style="padding:4px 10px;background:#dcfce7;'
                'color:#15803d;border-radius:20px;font-size:12px;font-weight:700;text-decoration:none;">👁 Visible</a>', url,
            )
        return format_html(
            '<a href="{}" title="Click to show" style="padding:4px 10px;background:#f3f4f6;'
            'color:#9ca3af;border-radius:20px;font-size:12px;font-weight:700;text-decoration:none;">🚫 Hidden</a>', url,
        )
    _visible_toggle.short_description = 'Portfolio'

    def _cert_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-width:260px;max-height:160px;object-fit:cover;border-radius:8px;border:1px solid #ddd;" />',
                obj.image.url,
            )
        return mark_safe('<span style="color:#888;">No image yet.</span>')
    _cert_preview.short_description = 'Badge Preview'

    def _visibility_note(self, obj):
        if not obj.pk:
            return ''
        profile = Profile.objects.first()
        if profile and not profile.show_certificates:
            return mark_safe(
                '<span style="display:inline-block;padding:6px 12px;background:#fef3c7;'
                'border:1px solid #f59e0b;border-radius:6px;color:#92400e;font-size:12px;">'
                '⚠️ The Certificates section is hidden on the portfolio. '
                'Enable via <a href="/admin/portfolio/profile/">Profile → Section Visibility</a>.</span>'
            )
        return ''
    _visibility_note.short_description = ''

    def get_urls(self):
        return [
            path('<int:pk>/toggle-visibility/',
                 self.admin_site.admin_view(self._toggle_view),
                 name='portfolio_certificate_toggle_visibility'),
        ] + super().get_urls()

    def _toggle_view(self, request, pk):
        cert = get_object_or_404(Certificate, pk=pk)
        cert.is_featured = not cert.is_featured
        cert.save()
        action = 'shown on' if cert.is_featured else 'hidden from'
        django_messages.success(request, f'"{cert.title}" is now {action} the portfolio.')
        return HttpResponseRedirect(reverse('admin:portfolio_certificate_changelist'))

    @admin.action(description='✅ Show selected on portfolio')
    def make_visible(self, request, queryset):
        django_messages.success(request, f'{queryset.update(is_featured=True)} certificate(s) now visible.')

    @admin.action(description='🚫 Hide selected from portfolio')
    def make_hidden(self, request, queryset):
        django_messages.success(request, f'{queryset.update(is_featured=False)} certificate(s) now hidden.')


# ═══════════════════════════════════════════════════════════════
# Messages
# ═══════════════════════════════════════════════════════════════
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display    = ('name', 'email', 'subject', 'sent_at', 'is_read')
    list_filter     = ('is_read', 'sent_at')
    search_fields   = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'sent_at')
    list_editable   = ('is_read',)
    date_hierarchy  = 'sent_at'

    def has_add_permission(self, request):
        return False
