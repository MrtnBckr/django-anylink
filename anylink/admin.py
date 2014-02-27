import re

from django.contrib import admin
from django.template.response import SimpleTemplateResponse
from django.utils.html import escape

from .models import AnyLink


EDITOR_ID_RE = re.compile('^[\w\-]+$')


class AnyLinkAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'link_type', 'text')
    list_filter = ('link_type', 'target')
    search_fields = ('text', 'title')

    def __init__(self, *args, **kwargs):
        super(AnyLinkAdmin, self).__init__(*args, **kwargs)
        for extension in self.model.extensions.values():
            extension.configure_modeladmin(self)

    def get_model_perms(self, request):
        # Adding is disabled to hide the add buttons.
        return {
            'add': False,
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
        }

    def render_change_form(self, request, context, *args, **kwargs):
        context.update({
            'link_extensions': self.model.extensions.values()
        })

        return super(AnyLinkAdmin, self).render_change_form(
            request, context, *args, **kwargs)

    def response_add(self, request, obj):
        if self.is_addorchange_popup(request):
            return self.response_addorchange(request, obj)

        if self.is_rtelink_popup(request):
            return self.response_rtelink(request, obj)

        return super(AnyLinkAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        if self.is_addorchange_popup(request):
            return self.response_addorchange(request, obj)

        if self.is_rtelink_popup(request):
            return self.response_rtelink(request, obj)

        return super(AnyLinkAdmin, self).response_change(request, obj)

    def is_rtelink_popup(self, request):
        return (
            '_popup' in request.POST
            and 'ed' in request.GET
            and EDITOR_ID_RE.match(request.GET['ed'])
        )

    def response_rtelink(self, request, obj):
        return SimpleTemplateResponse(
            'admin/anylink/anylink/rtelink_response.html', {
                'editor_id': request.GET['ed'],
                'link_id': obj.get_rtelink_id()
            })

    def is_addorchange_popup(self, request):
        return (
            '_popup' in request.POST
            and 'aoc' in request.GET
        )

    def response_addorchange(self, request, obj):
        return SimpleTemplateResponse(
            'admin/anylink/anylink/addorchange_response.html', {
                'link_id': obj.pk,
                'link_name': escape(unicode(obj))
            })

admin.site.register(AnyLink, AnyLinkAdmin)