from doajtest.helpers import DoajTestCase, load_from_matrix
from parameterized import parameterized, param
from doajtest.fixtures import JournalFixtureFactory, AccountFixtureFactory, ApplicationFixtureFactory

from copy import deepcopy
from random import randint

from portality.models import Journal, Account, Suggestion

from portality.bll import DOAJ
from portality.bll import exceptions

EXCEPTIONS = {
    "ArgumentException" : exceptions.ArgumentException
}

def load_j2a_cases():
    journal = Journal(**JournalFixtureFactory.make_journal_source(in_doaj=True))
    account_source = AccountFixtureFactory.make_publisher_source()

    owner_account = Account(**deepcopy(account_source))
    owner_account.set_id(journal.owner)

    non_owner_publisher = Account(**deepcopy(account_source))

    non_publisher = Account(**deepcopy(account_source))
    non_publisher.remove_role("publisher")

    admin = Account(**deepcopy(account_source))
    admin.add_role("admin")

    return [
        param("no_journal_no_account", None, None, raises=exceptions.ArgumentException),
        param("no_journal_with_account", None, owner_account, raises=exceptions.ArgumentException),
        param("journal_no_account", journal, None, comparator=application_matches),
        param("journal_matching_account", journal, owner_account, comparator=application_matches),
        param("journal_unmatched_account", journal, non_owner_publisher, raises=exceptions.AuthoriseException),
        param("journal_non_publisher_account", journal, non_publisher, raises=exceptions.AuthoriseException),
        param("journal_admin_account", journal, admin, comparator=application_matches)
    ]


def load_a2j_cases():
    return load_from_matrix("application_2_journal.csv", test_ids=[])

def application_matches(journal, application):
    assert isinstance(application, Suggestion)
    assert journal.bibjson().data == application.bibjson().data
    assert application.application_status == "update_request"
    assert journal.contacts() == application.contacts()
    assert application.current_journal == journal.id
    #assert application.editor == journal.editor
    #assert application.editor_group == journal.editor_group
    assert application.notes == journal.notes
    assert application.owner == journal.owner
    assert application.has_seal() is journal.has_seal()
    assert application.suggester == journal.contacts()[0]


class TestBLLObjectConversions(DoajTestCase):

    @parameterized.expand(load_j2a_cases)
    def test_01_journal_2_application(self, name, journal, account, raises=None, comparator=None):
        doaj = DOAJ()
        if raises is not None:
            with self.assertRaises(raises):
                doaj.journal_2_application(journal, account)
        elif comparator is not None:
            application = doaj.journal_2_application(journal, account)
            comparator(journal, application)
        else:
            assert False, "Specify either raises or comparator"

    @parameterized.expand(load_a2j_cases)
    def test_02_application_2_journal(self, name, application_type, manual_update, app_key_properties, current_journal, raises):
        # set up for the test
        #########################################

        cj = None
        has_seal = bool(randint(0, 1))
        application = None
        if application_type == "present":
            application = Suggestion(**ApplicationFixtureFactory.make_application_source())
            application.set_id(application.makeid())
            application.remove_contacts()
            application.remove_editor_group()
            application.remove_editor()
            application.remove_owner()
            application.remove_current_journal()
            application.remove_notes()

            if app_key_properties == "yes":
                application.add_contact("Application", "application@example.com")
                application.set_editor_group("appeditorgroup")
                application.set_editor("appeditor")
                application.set_owner("appowner")

            application.set_seal(has_seal)
            application.add_note("Application Note")

            if current_journal == "present":
                journal = Journal(**JournalFixtureFactory.make_journal_source())
                journal.remove_contacts()
                journal.add_contact("Journal", "journal@example.com")
                journal.set_editor_group("journaleditorgroup")
                journal.set_editor("journaleditor")
                journal.set_owner("journalowner")
                journal.remove_current_application()
                journal.remove_notes()
                journal.add_note("Journal Note")
                journal.save(blocking=True)
                application.set_current_journal(journal.id)
                cj = journal
            elif current_journal == "missing":
                application.set_current_journal("123456789987654321")

        mu = None
        if manual_update == "true":
            mu = True
        elif manual_update == "false":
            mu = False

        # execute the test
        ########################################

        doaj = DOAJ()
        if raises is not None and raises != "":
            with self.assertRaises(EXCEPTIONS[raises]):
                doaj.application_2_journal(application, mu)
        else:
            journal = doaj.application_2_journal(application, mu)

            # check the result
            ######################################

            assert journal is not None
            assert isinstance(journal, Journal)
            assert journal.is_in_doaj() is True

            jbj = journal.bibjson().data
            del jbj["active"]
            assert jbj == application.bibjson().data

            if current_journal == "present":
                assert len(journal.related_applications) == 3
            else:
                assert len(journal.related_applications) == 1
            related = journal.related_application_record(application.id)
            assert related is not None

            if manual_update == "true":
                assert journal.last_manual_update is not None and journal.last_manual_update != "1970-01-01T00:00:00Z"

            if app_key_properties == "yes":
                contacts = journal.contacts()
                assert len(contacts) == 1
                assert contacts[0].get("name") == "Application"
                assert contacts[0].get("email") == "application@example.com"
                assert journal.editor_group == "appeditorgroup"
                assert journal.editor == "appeditor"
                assert journal.owner == "appowner"
                assert journal.has_seal() == has_seal

                if current_journal == "present":
                    assert len(journal.notes) == 2
                else:
                    assert len(journal.notes) == 1

            elif app_key_properties == "no":
                if current_journal == "present":
                    contacts = journal.contacts()
                    assert len(contacts) == 1
                    assert contacts[0].get("name") == "Journal"
                    assert contacts[0].get("email") == "journal@example.com"
                    assert journal.editor_group == "journaleditorgroup"
                    assert journal.editor == "journaleditor"
                    assert journal.owner == "journalowner"
                    assert journal.has_seal() == has_seal
                    assert len(journal.notes) == 2

                elif current_journal == "none" or current_journal == "missing":
                    contacts = journal.contacts()
                    assert len(contacts) == 0
                    assert journal.editor_group is None
                    assert journal.editor is None
                    assert journal.owner is None
                    assert journal.has_seal() == has_seal
                    assert len(journal.notes) == 1

            if current_journal == "present":
                assert cj.id == journal.id
                assert cj.created_date == journal.created_date
