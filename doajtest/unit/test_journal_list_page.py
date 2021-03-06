from doajtest.helpers import DoajTestCase
from doajtest.fixtures import JournalFixtureFactory
from portality import models
from portality.app import app

class TestClient(DoajTestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True

    def test_01_journal_list_page_content(self):
        """test if the journal list page used in the sitemap for bots works and only displays journals accepted in DOAJ"""
        journal_sources = JournalFixtureFactory.make_many_journal_sources(2, in_doaj=True)
        j_public = models.Journal(**journal_sources[0])
        j_public.save(blocking=True)

        j_private = models.Journal(**journal_sources[1])
        j_private.set_in_doaj(False)
        j_private.save(blocking=True)

        with app.test_client() as t_client:
            response_authorised = t_client.get('/toc')
            assert response_authorised.status_code == 200
            assert '<a href="/toc/{public_issn}">Test Title 0</a>'.format(public_issn=j_public.bibjson().get_one_identifier(j_public.bibjson().E_ISSN)) in response_authorised.data, response_authorised.data
            assert '<a href="/toc/{private_eissn}">Test Title 1</a>'.format(private_eissn=j_private.bibjson().get_one_identifier(j_private.bibjson().E_ISSN)) not in response_authorised.data, response_authorised.data
            assert '<a href="/toc/{private_pissn}">Test Title 1</a>'.format(private_pissn=j_private.bibjson().get_one_identifier(j_private.bibjson().P_ISSN)) not in response_authorised.data, response_authorised.data
