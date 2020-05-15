if (top.location != location) top.location.href = location.href;

function onChangeItem(sel)
{
        var op = sel[sel.selectedIndex].value;
        var url = op;

        location.href=url;
}

function copysource()
{
        var source = clipboardData.getData("Text");
        source = source + "Source URL: " + window.location.href;
        clipboardData.setData("Text", source);
}
