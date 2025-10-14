
import yaml
import argparse

def add_bookmark(category, name, abbr, href, icon):
    """Adds a new bookmark to the bookmarks.yaml file."""
    with open("bookmarks.yaml", "r") as f:
        bookmarks = yaml.safe_load(f)

    new_bookmark = {name: [{"abbr": abbr, "href": href, "icon": icon}]}

    for item in bookmarks:
        if category in item:
            item[category].append(new_bookmark)
            break
    else:
        bookmarks.append({category: [new_bookmark]})

    with open("bookmarks.yaml", "w") as f:
        yaml.dump(bookmarks, f, default_flow_style=False)

def delete_bookmark(category, name):
    """Deletes a bookmark from the bookmarks.yaml file."""
    with open("bookmarks.yaml", "r") as f:
        bookmarks = yaml.safe_load(f)

    for item in bookmarks:
        if category in item:
            item[category] = [bookmark for bookmark in item[category] if name not in bookmark]

    with open("bookmarks.yaml", "w") as f:
        yaml.dump(bookmarks, f, default_flow_style=False)

def list_bookmarks(category):
    """Lists all bookmarks in a given category."""
    with open("bookmarks.yaml", "r") as f:
        bookmarks = yaml.safe_load(f)

    for item in bookmarks:
        if category in item:
            for bookmark in item[category]:
                for name, details in bookmark.items():
                    print(f"- {name}:")
                    for detail in details:
                        for key, value in detail.items():
                            print(f"    {key}: {value}")

def set_group_layout(group, style, columns):
    """Sets the layout for a specific group."""
    with open("settings.yaml", "r") as f:
        settings = yaml.safe_load(f)

    if "layout" not in settings:
        settings["layout"] = []

    for item in settings["layout"]:
        if group in item:
            item[group]["style"] = style
            item[group]["columns"] = columns
            break
    else:
        settings["layout"].append({group: {"style": style, "columns": columns}})

    with open("settings.yaml", "w") as f:
        yaml.dump(settings, f, default_flow_style=False)

def get_categories():
    """Returns a list of all categories."""
    with open("bookmarks.yaml", "r") as f:
        bookmarks = yaml.safe_load(f)

    return [list(item.keys())[0] for item in bookmarks]

def add_group_layout(group, style, columns):
    """Adds a new group to the layout."""
    with open("settings.yaml", "r") as f:
        settings = yaml.safe_load(f)

    if "layout" not in settings:
        settings["layout"] = []

    settings["layout"].append({group: {"style": style, "columns": columns}})

    with open("settings.yaml", "w") as f:
        yaml.dump(settings, f, default_flow_style=False)

def remove_group_layout(group):
    """Removes a group from the layout."""
    with open("settings.yaml", "r") as f:
        settings = yaml.safe_load(f)

    if "layout" in settings:
        settings["layout"] = [item for item in settings["layout"] if group not in item]

    with open("settings.yaml", "w") as f:
        yaml.dump(settings, f, default_flow_style=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Homepage bookmarks.")
    subparsers = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new bookmark.")
    add_parser.add_argument("--category", required=True, help="The category to add the bookmark to.")
    add_parser.add_argument("--name", required=True, help="The name of the bookmark.")
    add_parser.add_argument("--abbr", required=True, help="The abbreviation for the bookmark.")
    add_parser.add_argument("--href", required=True, help="The URL for the bookmark.")
    add_parser.add_argument("--icon", required=True, help="The icon for the bookmark.")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a bookmark.")
    delete_parser.add_argument("--category", required=True, help="The category to delete the bookmark from.")
    delete_parser.add_argument("--name", required=True, help="The name of the bookmark to delete.")

    # List command
    list_parser = subparsers.add_parser("list", help="List all bookmarks in a category.")
    list_parser.add_argument("--category", required=True, help="The category to list bookmarks from.")

    # Layout command
    layout_parser = subparsers.add_parser("layout", help="Manage the layout of bookmark groups.")
    layout_subparsers = layout_parser.add_subparsers(dest="layout_command")

    # Set-group command
    set_group_parser = layout_subparsers.add_parser("set-group", help="Set the layout for a specific group.")
    set_group_parser.add_argument("--group", required=True, help="The group to set the layout for.")
    set_group_parser.add_argument("--style", required=True, help="The style of the group (e.g., 'row', 'column').")
    set_group_parser.add_argument("--columns", required=True, type=int, help="The number of columns for the group.")

    # Add-group command
    add_group_parser = layout_subparsers.add_parser("add-group", help="Add a new group to the layout.")
    add_group_parser.add_argument("--group", required=True, help="The name of the new group.")
    add_group_parser.add_argument("--style", default="row", help="The style of the group (e.g., 'row', 'column').")
    add_group_parser.add_argument("--columns", default=3, type=int, help="The number of columns for the group.")

    # Remove-group command
    remove_group_parser = layout_subparsers.add_parser("remove-group", help="Remove a group from the layout.")
    remove_group_parser.add_argument("--group", required=True, help="The group to remove from the layout.")

    args = parser.parse_args()

    if args.command == "add":
        add_bookmark(args.category, args.name, args.abbr, args.href, args.icon)
    elif args.command == "delete":
        delete_bookmark(args.category, args.name)
    elif args.command == "list":
        list_bookmarks(args.category)
    elif args.command == "layout":
        if args.layout_command == "set-group":
            set_group_layout(args.group, args.style, args.columns)
        elif args.layout_command == "add-group":
            add_group_layout(args.group, args.style, args.columns)
        elif args.layout_command == "remove-group":
            remove_group_layout(args.group)
