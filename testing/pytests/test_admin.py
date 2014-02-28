import mock
import pytest

from django.contrib import admin
from django.forms.models import modelform_factory

from anylink.admin import AnyLinkAdmin
from anylink.models import AnyLink

from testing.testproject.models import TestModel


TestForm = modelform_factory(TestModel)


@pytest.mark.django_db
class TestAnyLinkAdmin:
    def setup(self):
        self.modeladmin = AnyLinkAdmin(AnyLink, admin.site)

    def test_model_perms(self, rf):
        request = rf.get('/')
        request.user = mock.Mock()
        request.user.has_perm.return_value = False
        assert self.modeladmin.get_model_perms(request) == {
            'add': False,
            'change': False,
            'delete': False,
        }

        request.user.has_perm.return_value = True
        assert self.modeladmin.get_model_perms(request) == {
            'add': False,
            'change': True,
            'delete': True,
        }

    def test_is_rtelink_popup(self, rf):
        assert self.modeladmin.is_rtelink_popup(rf.post('/?ed=ed1', data={
            'foo': 'bar'
        })) is False
        assert self.modeladmin.is_rtelink_popup(rf.post('/?foo=ed1', data={
            '_popup': '1'
        })) is False
        assert self.modeladmin.is_rtelink_popup(rf.post('/?ed=/ed1', data={
            '_popup': '1'
        })) is False
        assert self.modeladmin.is_rtelink_popup(rf.post('/?ed=ed1', data={
            '_popup': '1'
        })) is True

    def test_is_addorchange_popup(self, rf):
        assert self.modeladmin.is_addorchange_popup(rf.post('/?aoc=1', data={
            'foo': 'bar'
        })) is False
        assert self.modeladmin.is_addorchange_popup(rf.post('/?foo=1', data={
            '_popup': '1'
        })) is False
        assert self.modeladmin.is_addorchange_popup(rf.post('/?aoc=1', data={
            '_popup': '1'
        })) is True

    def test_response_rtelink_popup_add(self, admin_client):
        response = admin_client.post('/admin/anylink/anylink/add/?ed=ed1', data={
            '_popup': '1',
            'link_type': 'external_url',
            'target': '_self',
            'external_url': 'http://test.de'
        })

        assert response.status_code == 200
        assert (
            "opener.tinymce.plugins.AnyLink.popupCallback('ed1', '{0}');"
        ).format(AnyLink.objects.get().get_rtelink_id()) in response.content

    def test_response_addorchange_popup_add(self, admin_client):
        response = admin_client.post('/admin/anylink/anylink/add/?aoc=1', data={
            '_popup': '1',
            'link_type': 'external_url',
            'target': '_self',
            'external_url': 'http://test.de'
        })

        assert response.status_code == 200
        assert (
            "opener.AnyLinkAddOrChangeWidget.callback(window, {0}, 'http://test.de/')"
        ).format(AnyLink.objects.get().pk) in response.content

    def test_response_popup_add(self, admin_client):
        response = admin_client.post('/admin/anylink/anylink/add/', data={
            '_popup': '1',
            'link_type': 'external_url',
            'target': '_self',
            'external_url': 'http://test.de'
        })

        assert response.status_code == 200
        assert (
            'opener.dismissAddAnotherPopup(window, "{0}", "http://test.de/");'
        ).format(AnyLink.objects.get().pk) in response.content


    def test_response_rtelink_popup_change(self, admin_client):
        obj = AnyLink.objects.create(link_type='external_url', external_url='http://foo')
        response = admin_client.post('/admin/anylink/anylink/{0}/?ed=ed1'.format(obj.pk), data={
            '_popup': '1',
            'link_type': 'external_url',
            'target': '_self',
            'external_url': 'http://test.de'
        })

        assert response.status_code == 200
        assert (
            "opener.tinymce.plugins.AnyLink.popupCallback('ed1', '{0}');"
        ).format(AnyLink.objects.get().get_rtelink_id()) in response.content

    def test_response_addorchange_popup_change(self, admin_client):
        obj = AnyLink.objects.create(link_type='external_url', external_url='http://foo')
        response = admin_client.post('/admin/anylink/anylink/{0}/?aoc=1'.format(obj.pk), data={
            '_popup': '1',
            'link_type': 'external_url',
            'target': '_self',
            'external_url': 'http://test.de'
        })

        assert response.status_code == 200
        assert (
            "opener.AnyLinkAddOrChangeWidget.callback(window, {0}, 'http://test.de/')"
        ).format(AnyLink.objects.get().pk) in response.content

    def test_response_popup_change(self, admin_client):
        obj = AnyLink.objects.create(link_type='external_url', external_url='http://foo')
        response = admin_client.post('/admin/anylink/anylink/{0}/'.format(obj.pk), data={
            '_popup': '1',
            'link_type': 'external_url',
            'target': '_self',
            'external_url': 'http://test.de'
        })

        assert response.status_code == 302
        assert response['Location'] == 'http://testserver/admin/anylink/anylink/'

    def test_change_view_context(self, admin_client, settings):
        obj = AnyLink.objects.create(link_type='external_url', external_url='http://foo')
        response = admin_client.get('/admin/anylink/anylink/{0}/'.format(obj.pk))

        assert response.status_code == 200
        assert len(response.context_data['link_extensions']) == len(
            settings.ANYLINK_EXTENSIONS)