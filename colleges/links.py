from project_piss.helpers import create_link_dict

colleges = {
    "default": {
        "get_all": create_link_dict("all/")
    },
    "authenticated": {
        "add_college": create_link_dict('create/')
    }
}
links = {
    "colleges": colleges
}