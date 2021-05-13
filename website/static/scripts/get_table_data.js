function get_row_checkboxes() {
    try {
        //gets table
        var oTable = document.getElementById('myTable');

        //gets rows of table
        var rowLength = oTable.rows.length;
        
        //loops through rows    
        var has_checked = false;
        for (i = 1; i < rowLength; i++) {

            //gets cells of current row  
            var oCells = oTable.rows.item(i).cells;

            var parameter_id = oCells.item(3).innerHTML;
            var stock_id = oCells.item(2).innerHTML;
            if ($('input[name=checkbox' + parameter_id + ']').attr('checked')) {
                console.log('checkbox'+parameter_id)
                has_checked = true;
                favorites[parameter_id] = {'stock_id':stock_id}
            }
        }

        array = JSON.stringify( favorites );
        document.getElementById("parameters_to_apply").value = array

        if(!has_checked)
        {
            alert("Nothing happens, no checkboxex checked!")
        }
        return has_checked;
    }
    catch (e) {
        alert(e);
    }
}

function getFavorite()
{
    return favorite;
}