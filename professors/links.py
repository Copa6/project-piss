from project_piss.helpers import create_link_dict

professors = {
    "default": {
        "get_all": create_link_dict("search/<str:college_id>")
    },
    "authenticated": {
        "add_professor": create_link_dict('create/'),
        "add_review": create_link_dict('add-review/<int:professor_id>'),
        "get_review": create_link_dict('get-reviews/<int:professor_id>', method='GET')
    }
}
links = {
    "professors": professors
}