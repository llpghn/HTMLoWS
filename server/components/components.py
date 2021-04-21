def greeting(listitems):
    html = ''
    for item in listitems:
        html += '<li>' + item + '</li>'
    return(f"""
        <div id="Liste">
            <ol>
                {html}
            </ol>
        </div>
    """)


def input_temp_preference(props = None):
    table_view = ''
    print('-Props-: ' + str(props))
    if props:
        table_view += '<ul>'
        for k in props.keys():
            table_view += '<li>' + str(k) + ' -- ' + str(props[k]) + '</li>'
        table_view += '</ul><hr>'

    html = table_view + f"""
        <label for="name">Name (4 to 8 characters):</label>
        <input type="text" id="name" name="name" required minlength="4" maxlength="8" size="10">
        <br>
        <button type="button" onClick="loadContent('SHOW_VIEW_ADD_PREFERENCE', {{'ids' : ['name']}})">
            Wert hinzufügen!
        </button>
    """
    return html


def main(props = None):
    html = f"""
        <h1>Websocket Web-Server</h1>
        <div id="nav">
            <button type="button" onClick="loadContent('MAINVIEW_VIEW')">
                Show values
            </button>
            <button type="button" onClick="loadContent('SHOW_VIEW_ADD_PREFERENCE')">
                Add Preference
            </button>
        </div>
        <div id='content'>
        </div>
    """
    return html