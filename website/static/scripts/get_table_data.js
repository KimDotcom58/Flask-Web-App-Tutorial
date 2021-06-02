function get_row_checkboxes() {
    try {
        //gets table
        var oTable = document.getElementById('myTable');

        //gets rows of table
        var rowLength = oTable.rows.length;
        
        //loops through rows    
        for (i = 1; i < rowLength; i++) {

            //gets cells of current row  
            var oCells = oTable.rows.item(i).cells;

            var parameter_id = oCells.item(3).innerHTML;
            var trading_id = oCells.item(2).innerHTML;
            
            if ($('input[name=checkbox' + parameter_id + ']').attr('checked')) {
                console.log('checkbox'+parameter_id)
                favorites[parameter_id] = {'trading_id':trading_id}
            }
        }

        array = JSON.stringify( favorites );
        document.getElementById("parameters_to_apply").value = array

        return true;
    }
    catch (e) {
        alert(e);
    }
}

function getFavorite()
{
    return favorite;
}