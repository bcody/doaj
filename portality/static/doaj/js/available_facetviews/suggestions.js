jQuery(document).ready(function($) {
  $('.facetview.suggestions').each(function() {
  $(this).facetview({
    search_url: 'http://' + es_domain + '/query/suggestion/_search?',
    search_index: 'elasticsearch',
    sharesave_link: false,
    searchbox_shade: 'none',
    pager_on_top: true,
    pager_slider: true,
    display_images: false,
    pre_search_callback: customise_facetview_presearch,
    post_search_callback: customise_facetview_results,
    post_init_callback: customise_facetview_init,
    freetext_submit_delay:"500",
    results_render_callbacks: {
        'bibjson.author_pays': fv_author_pays,
        'created_date': fv_created_date,
        'bibjson.abstract': fv_abstract,
        'journal_license' : fv_journal_license,
        "title_field" : fv_title_field,
        "doi_link" : fv_doi_link,
        "links" : fv_links,
        "issns" : fv_issns,
        "edit_suggestion" : fv_edit_suggestion,
    },
    hide_inactive_facets: true,
    facets: [
        {'field': 'admin.application_status.exact', 'display': 'Suggestion Status'},
        {'field': 'suggestion.suggested_by_owner.exact', 'display': 'Suggested by owner?'},

        {'field': 'index.classification.exact', 'display': 'Subject'},
        {'field': 'index.language.exact', 'display': 'Journal Language'},
        {'field': 'index.country.exact', 'display': 'Journal Country'},
        {'field': 'index.subject.exact', 'display': 'Subject'},
        {'field': 'index.publisher.exact', 'display': 'Publisher'},
        {'field': 'bibjson.provider.exact', 'display': 'Provider'},
        {'field': 'bibjson.author_pays.exact', 'display': 'Publication charges?'},
        {'field': 'index.license.exact', 'display': 'Journal License'},
        {'field': 'bibjson.oa_start.exact', 'display': 'Started publishing OA content (year)'},
        {'field': 'bibjson.oa_end.exact', 'display': 'Stopped publishing OA content (year)'},
    ],
    search_sortby: [
        {'display':'Date suggested','field':'suggestion.suggested_on.exact'},
        {'display':'Title','field':'bibjson.title.exact'},
    ],
    searchbox_fieldselect: [
        {'display':'Title','field':'index.title'},
        {'display':'Keywords','field':'index.keywords'},
        {'display':'Subject','field':'index.classification'},
        {'display':'ISSN', 'field':'index.issn.exact'},
        {'display':'Journal Country','field':'index.country'},
        {'display':'Journal Language','field':'index.language'},
        {'display':'Publisher','field':'index.publisher'},

        {'display':'Journal: Alternative Title','field':'bibjson.alternative_title'},
        {'display':'Journal: Provider','field':'bibjson.provider'},
    ],
    paging: {
      from: 0,
      size: 10
    },
    default_operator: "AND",
    result_display: [
        [
            {
                "field" : "title_field"
            }
        ],
        [
            {
                "pre": '<span class="alt_title">Alternative title: ',
                "field": "bibjson.alternative_title",
                "post": "</span>"
            }
        ],
        [
            {
                "pre": "<strong>Date suggested</strong>: ",
                "field": "suggestion.suggested_on",
            }
        ],
        [
            {
                "pre" : "<strong>ISSN(s)</strong>: ",
                "field" : "issns"
            }
        ],
        [
            {
                "pre" : "<strong>Application status</strong>: ",
                "field" : "admin.application_status"
            }
        ],
        [
            {
                "pre" : "<strong>Description</strong>: ",
                "field" : "suggestion.description"
            }
        ],
        [
            {
                "pre" : "<strong>Contact</strong>: ",
                "field" : "admin.contact.name"
            },
            {
                "field" : "admin.contact.email"
            }
        ],
        [
            {
                "pre" : "<strong>Suggested by</strong>: ",
                "field" : "suggestion.suggester.name"
            },
            {
                "field" : "suggestion.suggester.email"
            }
        ],
        [
            {
                "pre": "<strong>Suggested by owner?</strong>: ",
                "field": "suggestion.suggested_by_owner"
            }
        ],
        [
            {
                "pre": "<strong>Subjects</strong>: ",
                "field": "index.subject",
            }
        ],
        [
            {
                "pre": "<strong>Keywords</strong>: ",
                "field": "bibjson.keywords",
            }
        ],
        [
            {
                "pre": "<strong>Publisher</strong>: ",
                "field": "bibjson.publisher",
            }
        ],
        [
            {
                "pre": "<strong>Provider</strong>: ",
                "field": "bibjson.provider",
            }
        ],
        [
            {
                "pre": "<strong>Publication charges?</strong>: ",
                "field": "bibjson.author_pays",
            }
        ],
        [
            {
                "pre": "<strong>Started publishing Open Access content in</strong>: ",
                "field": "bibjson.oa_start.year",
            }
        ],
        [
            {
                "pre": "<strong>Stopped publishing Open Access content in</strong>: ",
                "field": "bibjson.oa_end.year",
            }
        ],
        [
            {
                "pre": "<strong>Journal Country</strong>: ",
                "field": "bibjson.country",
            }
        ],
        [
            {
                "pre": "<strong>Journal Language</strong>: ",
                "field": "bibjson.language",
            }
        ],
        [
            {
                "pre": "<strong>Journal License</strong>: ",
                "field": "journal_license"
            }
        ],
        [
            {
                "field" : "links"
            }
        ],
        [
            {
                "field" : "edit_suggestion"
            }
        ],
    ],
  });
  });
});