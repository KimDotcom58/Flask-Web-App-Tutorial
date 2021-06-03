/*
Needs Variables:
    - Stock_detail_var.toggle_class             class name to listen to
    - Stock_detail_var.actual_document          path of document with submit-button to disable
    - Stock_detail_var.disable_apply_button     ID of submit-button
    - Stock_detail_var.stock_id                 stock-id of traded
    - Stock_detail_var.stocks_breakout
*/
var toggle_div = {

    toggle_class: "toggle-divs",
    toggled_class_prefix: "div",

    case: "detail",

    actual_document: document,
    disable_apply_button: "submitting"
}


$(document).ready(function () {

    $('.' + toggle_div.toggle_class).on('change', function () {

        // show and hide the parameter-div of the chosen dropdown-selection
        var nextAside = $(this).parent('.aside').next('.aside');
        nextAside.find(toggle_div.toggled_class_prefix).hide();
        nextAside.find("." + toggle_div.toggled_class_prefix + this.value).show();
        console.log("Toggle_Div_Script")

        if (toggle_div.case == "detail") {
            // Disable apply_button if "Apply Strategy"-dropdown is on the first value
            var disabled = true;
            if (this.value) {
                disabled = false;
            }
            else {
                disabled = true;
            }
            toggle_div.actual_document.getElementById(toggle_div.disable_apply_button).disabled = disabled;
        }
    });
})