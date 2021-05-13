function get_row_data() {
    var rowId = event.target.parentNode.parentNode.id;
    //this gives id of tr whose button was clicked
    var data =
        document.getElementById(rowId).querySelectorAll(".row-data");
    /*returns array of all elements with 
    "row-data" class within the row with given id*/
    var len = data.length
    var text = ""
    var symbol = data[0].innerHTML;
    var name = data[1].innerHTML;
    var stock_id = data[2].innerHTML;
    var parameter_id = data[3].innerHTML;
    text += "Do you really want to delete \"" + name + "\"?\n\t- Symbol: \t\t" + symbol + "\n\t- Stock ID: \t\t" + stock_id + "\n\t- Parameter ID: \t" + parameter_id+ "\n\t- ";
    for (i = 4; i < len ; i++){
        text += "Parameter"+String(i-3)+": \t\t"+ data[i].innerHTML;
        if(i < len-1)
        {
            text += "\n\t- ";
        }
    }
    text += "\nAll parameters will be saved and can be re-applied in the settings."

    document.getElementById("parameter_id").value = parameter_id;
    document.getElementById("stock_id").value = stock_id;

    return confirm(text);
}